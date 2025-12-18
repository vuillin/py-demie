import pygame 
import random
import math
from settings import *

class Person:

    def __init__(self, x, y, city_rect):
        self.x = x
        self.y = y
        self.home = (x, y) # sa maison est son point de départ
        self.city_rect = city_rect
        self.radius = 5

        # Identité 
        self.gender = random.choice(["M", "F"])
        self.color = BLUE if self.gender == "M" else PINK
        self.age = random.randint(18, 90)

        # Calcul de la fragilité
        # Soit par hasard (5%), Soit parce qu'on est vieux (> 70 ans)
        self.is_fragile = (random.random() < FRAGILITY_RATE) or (self.age > 70)

        # Rôle : 60% d'employés, 40% sans emploi
        self.is_employed = random.random() < 0.6

        # 50% des employés sont "mobiles" en ville, les autres sont statiques
        self.is_mobile_worker = random.random() < 0.5

        # La personne reste en ville
        self.stay_tonight = False

        # Décision quotidienne pour les sans-emploi
        self.goes_to_city_today = False

        # Décision de balade autour de chez soi
        self.wanders_locally_today = False

        # Mouvement
        self.target = (x, y)
        self.base_speed = BASE_WALK_SPEED + random.uniform(-0.2, 0.2)
        self.speed = self.base_speed # Vitesse actuelle
        self.wandering_target = None # pour se balader un peu
    

    def move(self):
        # Logique de déplacement fluide vers la cible (self.target)
        tx, ty = self.target
        dist = math. hypot(tx - self.x, ty - self.y)

        # Si la distance restante est plus petite que ma vitesse, je me colle direct au but
        if dist < self.speed:
            self.x = tx
            self.y = ty
        else:
            # Sinon, j'avance normalement
            angle = math.atan2(ty - self.y, tx - self.x)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed

    
    def update_behavior(self, hour):
        # PHASE 1 : JOURNÉE (8h - 17h)
        if 8 <= hour < 17:
            # Par défaut, tout le monde est à vitesse normale
            self.speed = self.base_speed
            
            if self.is_employed:
                # --- Logique Employés ---
                if self.city_rect.collidepoint(self.x, self.y):
                    if self.is_mobile_worker:
                        dist_to_target = math.hypot(self.target[0] - self.x, self.target[1] - self.y)
                        if dist_to_target < 5:
                            rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                            ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                            self.target = (rx, ry)
                else:
                    if self.wandering_target is None:
                        rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                        ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                        self.target = (rx, ry)
                        self.wandering_target = True 
                        self.stay_tonight = (random.random() < 0.1)
            
            else:
                # --- Logique Sans Emploi ---
                
                # 1. Prise de décision du matin
                if self.wandering_target is None:
                    self.wandering_target = True 
                    
                    if random.random() < 0.2:
                        self.goes_to_city_today = True
                        self.wanders_locally_today = False
                        rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                        ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                        self.target = (rx, ry)
                    else:
                        self.goes_to_city_today = False
                        if random.random() < 0.5:
                            self.wanders_locally_today = True
                            rx = self.home[0] + random.randint(-60, 60)
                            ry = self.home[1] + random.randint(-60, 60)
                            self.target = (rx, ry)
                        else:
                            self.wanders_locally_today = False
                            self.target = self.home

                # 2. Comportement actif
                if self.goes_to_city_today:
                    if self.city_rect.collidepoint(self.x, self.y):
                        dist_to_target = math.hypot(self.target[0] - self.x, self.target[1] - self.y)
                        if dist_to_target < 5:
                            rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                            ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                            self.target = (rx, ry)
                
                elif self.wanders_locally_today:
                    # CORRECTION ICI : Vitesse divisée par 2
                    self.speed = self.base_speed / 2
                    
                    dist_to_target = math.hypot(self.target[0] - self.x, self.target[1] - self.y)
                    if dist_to_target < 5:
                        rx = self.home[0] + random.randint(-60, 60)
                        ry = self.home[1] + random.randint(-60, 60)
                        rx = max(10, min(WIDTH-10, rx))
                        ry = max(10, min(HEIGHT-10, ry))
                        self.target = (rx, ry)
                
                else:
                    self.target = self.home

        # PHASE 2 : SOIRÉE (17h - 23h)
        elif 17 <= hour < 23:
            if self.is_employed and self.stay_tonight:
                self.speed = self.base_speed * 0.3
                if self.city_rect.collidepoint(self.x, self.y):
                     dist_to_target = math.hypot(self.target[0] - self.x, self.target[1] - self.y)
                     if dist_to_target < 5:
                        rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                        ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                        self.target = (rx, ry)
                elif self.wandering_target is None:
                     rx = random.randint(self.city_rect.left + 10, self.city_rect.right - 10)
                     ry = random.randint(self.city_rect.top + 10, self.city_rect.bottom - 10)
                     self.target = (rx, ry)
                     self.wandering_target = True 
            else:
                self.speed = self.base_speed
                self.target = self.home

        # PHASE 3 : RESET (23h - 8h)
        else:
            self.target = self.home
            self.wandering_target = None
            self.stay_tonight = False
            self.speed = self.base_speed
            self.goes_to_city_today = False
            self.wanders_locally_today = False

    
    def update(self, hour, game_speed_multiplier):

            self.update_behavior(hour)

            real_speed = (self.base_speed + random.uniform(-0.5, 0.5)) * game_speed_multiplier

            # Calcul de la distance vers la cible
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                move_dist = min(dist, real_speed)
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist


    def draw(self, screen, zoom, pan_x, pan_y):
        # Calcul de la position à l'écran avec le zoom
        cx = int(self.x * zoom + pan_x)
        cy = int(self.y * zoom + pan_y)
        
        # Le rayon change aussi avec le zoom (min 2 pixels pour qu'on les voie toujours)
        screen_radius = int(max(2, self.radius * zoom))

        # 1. Dessiner le corps
        pygame.draw.circle(screen, self.color, (cx, cy), screen_radius)
        
        # 2. Cercle intérieur pour fragile (TON STYLE)
        if self.is_fragile:
            # On calcule la taille du point blanc en fonction du zoom
            inner_radius = screen_radius // 2
            
            # Sécurité : on s'assure qu'il fait au moins 1 pixel pour être visible
            if inner_radius < 1: 
                inner_radius = 1
                
            pygame.draw.circle(screen, WHITE, (cx, cy), inner_radius)
