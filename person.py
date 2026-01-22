import pygame 
import random
import math
from settings import *

class Person:
    # On ajoute 'supermarket_rect', 'sports_complex_rect' et 'nav' dans les arguments
    def __init__(self, x, y, city_rect, supermarket_rect, sports_complex_rect, nav):
        self.x = x
        self.y = y
        self.home = (x, y)
        self.city_rect = city_rect
        self.supermarket_rect = supermarket_rect if supermarket_rect else city_rect 
        self.sports_complex_rect = sports_complex_rect if sports_complex_rect else city_rect # Fallback
        
        self.shopping_day = random.randint(0, 6) # 0-6 (Lundi-Dimanche)
        
        # 20% de sportifs
        self.is_sportive = random.random() < 0.2
        self.sport_day = -1
        if self.is_sportive:
            # On choisit un jour de sport différent du jour de course
            while True:
                self.sport_day = random.randint(0, 6)
                if self.sport_day != self.shopping_day:
                    break

        self.nav = nav # <--- On stocke le GPS
        self.radius = 5
        
        # --- PATHFINDING ---
        self.path = []      # La liste des points à suivre
        self.final_target = (x, y) # La destination finale réelle
        # -------------------

        # Identité 
        self.gender = random.choice(["M", "F"])
        self.color = BLUE if self.gender == "M" else PINK
        self.age = random.randint(18, 90)
        self.is_fragile = (random.random() < FRAGILITY_RATE) or (self.age > 70)
        self.is_employed = random.random() < 0.6
        self.is_mobile_worker = random.random() < 0.5
        self.stay_tonight = False
        self.goes_to_city_today = False
        self.wanders_locally_today = False

        # Mouvement
        self.target = (x, y) # Cible immédiate (prochain point du chemin)
        self.base_speed = BASE_WALK_SPEED + random.uniform(-0.2, 0.2)
        self.speed = self.base_speed 
        self.base_speed = BASE_WALK_SPEED + random.uniform(-0.2, 0.2)
        self.speed = self.base_speed 
        self.wandering_target = None 
        self.job = None # Metier special 
        self.wait_timer = 0 # Pause généralisée

    def update_behavior(self, hour, day_index):
        # SI ON A UN MÉTIER : ON DÉLÈGUE TOUT
        if self.job:
            self.job.apply_behavior(self, hour)
            return

        # Cette fonction décide OÙ on veut aller (self.final_target)
        # J'ai remplacé tous les 'self.target =' par 'self.final_target ='

        # 0. SHOPPING DAY (Overrides almost everything except night)
        # Si c'est notre jour de course, on va au supermarché pendant la journée (8h-17h/19h)
        if day_index == self.shopping_day and 8 <= hour < 19:
            self.speed = self.base_speed
            
            # Si on est DANS le supermarché
            if self.supermarket_rect.collidepoint(self.x, self.y):
                # On erre dedans
                if self.wait_timer == 0:
                    dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                    if dist < 10: 
                        self.wait_timer = random.randint(120, 240)
                        rx = random.randint(self.supermarket_rect.left + 5, self.supermarket_rect.right - 5)
                        ry = random.randint(self.supermarket_rect.top + 5, self.supermarket_rect.bottom - 5)
                        self.final_target = (rx, ry)
            else:
                # On va vers le supermarché
                if not self.supermarket_rect.collidepoint(*self.final_target):
                    rx = random.randint(self.supermarket_rect.left + 5, self.supermarket_rect.right - 5)
                    ry = random.randint(self.supermarket_rect.top + 5, self.supermarket_rect.bottom - 5)
                    self.final_target = (rx, ry)
            return 

            return 

        # 0.5. SPORT DAY (Overrides routine too)
        # Si c'est notre jour de sport, on va au complexe sportif (8h-19h)
        if self.is_sportive and day_index == self.sport_day and 8 <= hour < 19:
            self.speed = self.base_speed
            
            # Si on est DANS le complexe sportif
            if self.sports_complex_rect.collidepoint(self.x, self.y):
                # On erre dedans
                if self.wait_timer == 0:
                    dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                    if dist < 10: 
                        self.wait_timer = random.randint(120, 240)
                        rx = random.randint(self.sports_complex_rect.left + 5, self.sports_complex_rect.right - 5)
                        ry = random.randint(self.sports_complex_rect.top + 5, self.sports_complex_rect.bottom - 5)
                        self.final_target = (rx, ry)
            else:
                # On va vers le complexe
                if not self.sports_complex_rect.collidepoint(*self.final_target):
                    rx = random.randint(self.sports_complex_rect.left + 5, self.sports_complex_rect.right - 5)
                    ry = random.randint(self.sports_complex_rect.top + 5, self.sports_complex_rect.bottom - 5)
                    self.final_target = (rx, ry)
            return

        # PHASE 1 : JOURNÉE (8h - 17h)
        if 8 <= hour < 17:
            self.speed = self.base_speed
            
            if self.is_employed:
                if self.city_rect.collidepoint(self.x, self.y):
                    if self.is_mobile_worker:
                        dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                        if dist < 10 and self.wait_timer == 0: # On recalcule si on est arrivé et pas en pause
                            self.wait_timer = random.randint(120, 240)
                            rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                            ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                            self.final_target = (rx, ry)
                else:
                    if self.wandering_target is None:
                        rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                        ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                        self.final_target = (rx, ry)
                        self.wandering_target = True 
                        self.stay_tonight = (random.random() < 0.1)
                    
                    # SI ON EST ARRIVÉ (Distance < 10) -> Pause puis nouveau point
                    dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                    if dist < 10 and self.wait_timer == 0:
                         self.wait_timer = random.randint(120, 240)
                         # On prépare le prochain point (il sera pris en compte après la pause)
                         rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                         ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                         self.final_target = (rx, ry)
            
            else: # Sans emploi
                if self.wandering_target is None:
                    self.wandering_target = True 
                    if random.random() < 0.2:
                        self.goes_to_city_today = True
                        rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                        ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                        self.final_target = (rx, ry)
                    else:
                        self.goes_to_city_today = False
                        if random.random() < 0.5:
                            self.wanders_locally_today = True
                            rx = self.home[0] + random.randint(-60, 60)
                            ry = self.home[1] + random.randint(-60, 60)
                            self.final_target = (rx, ry)
                        else:
                            self.final_target = self.home

                if self.goes_to_city_today:
                    if self.city_rect.collidepoint(self.x, self.y):
                        dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                        if dist < 10 and self.wait_timer == 0:
                            self.wait_timer = random.randint(120, 240)
                            rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                            ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                            self.final_target = (rx, ry)
                
                elif self.wanders_locally_today:
                    self.speed = self.base_speed / 2
                    dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                    if dist < 10:
                        if self.wait_timer == 0:
                            self.wait_timer = random.randint(120, 240)
                            rx = self.home[0] + random.randint(-60, 60)
                            ry = self.home[1] + random.randint(-60, 60)
                            self.final_target = (rx, ry)
                else:
                    self.final_target = self.home

        # PHASE 2 : SOIRÉE
        elif 17 <= hour < 23:
            if self.is_employed and self.stay_tonight:
                self.speed = self.base_speed * 0.6
                if self.city_rect.collidepoint(self.x, self.y):
                     dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                     if dist < 10:
                        rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                        ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                        self.final_target = (rx, ry)
                elif self.wandering_target is None:
                     rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                     ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                     self.final_target = (rx, ry)
                     self.wandering_target = True 
                
                # PAUSE SOIRÉE
                dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                if dist < 10 and self.wait_timer == 0:
                     self.wait_timer = random.randint(120, 240)
                     rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                     ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                     self.final_target = (rx, ry) 
            else:
                self.speed = self.base_speed
                self.final_target = self.home

        # PHASE 3 : NUIT
        else:
            self.final_target = self.home
            self.wandering_target = None
            self.stay_tonight = False
            self.speed = self.base_speed
            self.goes_to_city_today = False
            self.wanders_locally_today = False

    
    def update(self, hour, game_speed_multiplier, day_index):
        # 0. GESTION PAUSE GÉNÉRALE
        if self.wait_timer > 0:
            self.wait_timer -= 1
            # On annule le mouvement
            return
            
        # 1. On décide où on veut aller au final
        self.update_behavior(hour, day_index)

        # 2. LOGIQUE GPS AUTOMATIQUE
        # Si on est loin de l'objectif (> 100px) et qu'on n'a pas de chemin, on en calcule un
        dist_to_final = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
        
        if dist_to_final > 100 and not self.path:
            # OPTIMISATION : Si le trajet est 100% urbain (départ ET arrivée dans la ville), on n'utilise pas le GPS
            in_city_start = self.city_rect.collidepoint(self.x, self.y)
            in_city_end = self.city_rect.collidepoint(*self.final_target)
            
            in_shop_start = self.supermarket_rect.collidepoint(self.x, self.y)
            in_shop_end = self.supermarket_rect.collidepoint(*self.final_target)
            
            in_sport_start = self.sports_complex_rect.collidepoint(self.x, self.y)
            in_sport_end = self.sports_complex_rect.collidepoint(*self.final_target)

            if not (in_city_start and in_city_end) and not (in_shop_start and in_shop_end) and not (in_sport_start and in_sport_end):
                # On demande la route au GPS seulement si on sort ou rentre
                # ET si on n'est pas en train de bosser (mode local)
                should_use_gps = True
                if self.job and self.job.is_in_work_mode(self, hour):
                    should_use_gps = False
                
                if should_use_gps:
                    self.path = self.nav.calculate_route((self.x, self.y), self.final_target)
        
        # Si on est proche (< 100px) ou qu'on erre localement, on vide le chemin pour aller tout droit
        elif dist_to_final <= 100:
            self.path = [] 

        # 3. DÉPLACEMENT
        # Quelle est ma cible IMMEDIATE ?
        if self.path:
            # Si j'ai un chemin, je vise le premier point
            self.target = self.path[0]
        else:
            # Sinon, je vise la destination finale (tout droit)
            self.target = self.final_target

        road_boost = 1.0

        if self.path:
            road_boost = 2.0


        real_speed = (self.speed * road_boost + random.uniform(-0.5, 0.5)) * game_speed_multiplier
        
        # Distance vers la cible immédiate
        dx = self.target[0] - self.x
        dy = self.target[1] - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            if dist < real_speed:
                # On est arrivé au point intermédiaire !
                self.x = self.target[0]
                self.y = self.target[1]
                if self.path:
                    self.path.pop(0) # On retire le point atteint, on passe au suivant
            else:
                move_dist = min(dist, real_speed)
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist

    def draw(self, screen, zoom, pan_x, pan_y):
        cx = int(self.x * zoom + pan_x)
        cy = int(self.y * zoom + pan_y)
        screen_radius = int(max(2, self.radius * zoom))

        pygame.draw.circle(screen, self.color, (cx, cy), screen_radius)
        
        if self.is_fragile:
            inner_radius = screen_radius // 2
            if inner_radius < 1: inner_radius = 1
            pygame.draw.circle(screen, WHITE, (cx, cy), inner_radius)