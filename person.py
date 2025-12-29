import pygame 
import random
import math
from settings import *

class Person:
    # On ajoute 'nav' dans les arguments
    def __init__(self, x, y, city_rect, nav):
        self.x = x
        self.y = y
        self.home = (x, y)
        self.city_rect = city_rect
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
        self.wandering_target = None 

    def update_behavior(self, hour):
        # Cette fonction décide OÙ on veut aller (self.final_target)
        # J'ai remplacé tous les 'self.target =' par 'self.final_target ='
        
        # PHASE 1 : JOURNÉE (8h - 17h)
        if 8 <= hour < 17:
            self.speed = self.base_speed
            
            if self.is_employed:
                if self.city_rect.collidepoint(self.x, self.y):
                    if self.is_mobile_worker:
                        dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                        if dist < 10: # On recalcule si on est arrivé
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
                        if dist < 10:
                            rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                            ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                            self.final_target = (rx, ry)
                
                elif self.wanders_locally_today:
                    self.speed = self.base_speed / 2
                    dist = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
                    if dist < 10:
                        rx = self.home[0] + random.randint(-60, 60)
                        ry = self.home[1] + random.randint(-60, 60)
                        self.final_target = (rx, ry)
                else:
                    self.final_target = self.home

        # PHASE 2 : SOIRÉE
        elif 17 <= hour < 23:
            if self.is_employed and self.stay_tonight:
                self.speed = self.base_speed * 0.3
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

    
    def update(self, hour, game_speed_multiplier):
        # 1. On décide où on veut aller au final
        self.update_behavior(hour)

        # 2. LOGIQUE GPS AUTOMATIQUE
        # Si on est loin de l'objectif (> 100px) et qu'on n'a pas de chemin, on en calcule un
        dist_to_final = math.hypot(self.final_target[0] - self.x, self.final_target[1] - self.y)
        
        if dist_to_final > 100 and not self.path:
            # OPTIMISATION : Si le trajet est 100% urbain (départ ET arrivée dans la ville), on n'utilise pas le GPS
            in_city_start = self.city_rect.collidepoint(self.x, self.y)
            in_city_end = self.city_rect.collidepoint(*self.final_target)

            if not (in_city_start and in_city_end):
                # On demande la route au GPS seulement si on sort ou rentre
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


        real_speed = (self.base_speed * road_boost + random.uniform(-0.5, 0.5)) * game_speed_multiplier
        
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