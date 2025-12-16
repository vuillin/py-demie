import pygame
import random
import math
from settings import *

class Map:
    def __init__(self, width, height, population_size):
        self.width = width
        self.height = height
        
        # Définition de la zone Ville
        self.city_size = 240
        self.city_rect = pygame.Rect(
            (width // 2 - self.city_size // 2, height // 2 - self.city_size // 2), 
            (self.city_size, self.city_size)
        )
        
        self.roads = []
        self.city_elements = []
        self.houses = []
        
        # NOUVEAU : Liste des points de spawn pré-calculés
        self.spawn_slots = [] 
        
        # Lancement des générateurs
        self._generate_roads()
        self._generate_city_architecture()
        
        # On génère les quartiers résidentiels en fonction de la population
        self._generate_villages(population_size)

    def _generate_roads(self):
        BLOCK_SIZE_MAP = 120  
        ROAD_WIDTH = 12   
        margin = 20

        # Périphérique
        self.roads.append(pygame.Rect(0, self.city_rect.top - margin, self.width, 16))
        self.roads.append(pygame.Rect(0, self.city_rect.bottom + margin - 16, self.width, 16))
        self.roads.append(pygame.Rect(self.city_rect.left - margin, 0, 16, self.height))
        self.roads.append(pygame.Rect(self.city_rect.right + margin - 16, 0, 16, self.height))

        # Grille de fond
        for x in range(0, self.width, BLOCK_SIZE_MAP):
            offset = random.randint(-5, 5)
            rect = pygame.Rect(x + offset, 0, ROAD_WIDTH, self.height)
            if not rect.colliderect(self.city_rect): self.roads.append(rect)

        for y in range(0, self.height, BLOCK_SIZE_MAP):
            offset = random.randint(-5, 5)
            rect = pygame.Rect(0, y + offset, self.width, ROAD_WIDTH)
            if not rect.colliderect(self.city_rect): self.roads.append(rect)

    def _generate_city_architecture(self):
        block_count = 4
        block_size = self.city_size // block_count
        padding = 5

        for row in range(block_count):
            for col in range(block_count):
                bx = self.city_rect.x + (col * block_size)
                by = self.city_rect.y + (row * block_size)
                rect = pygame.Rect(bx + padding, by + padding, block_size - 2*padding, block_size - 2*padding)
                
                # A. LE PARC (Haut-Droit)
                if row in [0, 1] and col in [2, 3]:
                    if row == 0 and col == 2:
                        park_rect = pygame.Rect(bx + padding, by + padding, (block_size*2) - 2*padding, (block_size*2) - 2*padding)
                        park_details = {"trees": [], "pond": None, "paths": []}
                        pond_w, pond_h = park_rect.width // 2.5, park_rect.height // 3
                        park_details["pond"] = pygame.Rect(park_rect.x + park_rect.width*0.6, park_rect.y + park_rect.height*0.15, pond_w, pond_h)
                        park_details["paths"].append([(park_rect.left, park_rect.top), (park_rect.right, park_rect.bottom)])
                        park_details["paths"].append([(park_rect.right, park_rect.top), (park_rect.left, park_rect.bottom)])
                        for _ in range(40):
                            tx, ty = random.randint(park_rect.left + 5, park_rect.right - 5), random.randint(park_rect.top + 5, park_rect.bottom - 5)
                            if not park_details["pond"].collidepoint(tx, ty): park_details["trees"].append((tx, ty))
                        self.city_elements.append({"type": "park", "rect": park_rect, "color": (60, 160, 70), "details": park_details})
                    continue 

                # B. LA PLACE (Bas-Gauche)
                elif row in [2, 3] and col in [0, 1]:
                    if row == 2 and col == 0:
                        plaza_margin = 20
                        plaza_rect = pygame.Rect(bx + plaza_margin, by + plaza_margin, (block_size*2) - 2*plaza_margin, (block_size*2) - 2*plaza_margin)
                        plaza_details = {"tiles": [], "fountain_center": plaza_rect.center}
                        tile_size = 10
                        for tx in range(plaza_rect.left, plaza_rect.right, tile_size):
                            for ty in range(plaza_rect.top, plaza_rect.bottom, tile_size):
                                if (tx + ty) % 20 == 0: plaza_details["tiles"].append(pygame.Rect(tx, ty, tile_size-1, tile_size-1))
                        self.city_elements.append({"type": "plaza", "rect": plaza_rect, "color": (200, 190, 180), "details": plaza_details})
                    continue
                    
                # C. IMMEUBLES
                else:
                    shade = random.randint(40, 70) 
                    color = (shade, shade, shade + 10)
                    windows = []
                    w_size, w_gap = 6, 4
                    for wx in range(rect.left + 4, rect.right - 4, w_size + w_gap):
                        for wy in range(rect.top + 4, rect.bottom - 4, w_size + w_gap):
                            if random.random() < 0.8:
                                win_color = (20, 20, 30)
                                if random.random() < 0.3: win_color = (200, 200, 100)
                                windows.append({"rect": pygame.Rect(wx, wy, w_size, w_size), "color": win_color})
                    self.city_elements.append({"type": "building", "rect": rect, "color": color, "details": {"windows": windows}})

    def _generate_villages(self, population_size):
        """Génère des quartiers résidentiels organiques"""
        
        # Configuration
        village_count = 6 
        houses_per_row = 6 
        base_spacing = 45   
        row_stagger = 20    
        random_jitter = 12  
        
        houses_per_village = (population_size // village_count) + 8
        
        villages_origins = []
        
        # 1. Trouver des points d'origine
        attempts = 0
        min_dist_between_villages = 250 
        
        while len(villages_origins) < village_count and attempts < 200:
            vx = random.randint(50, self.width - 300)
            vy = random.randint(50, self.height - 300)
            
            safe_city_zone = self.city_rect.inflate(150, 150)
            
            # On vérifie juste l'origine du village ici
            village_w = houses_per_row * base_spacing
            village_h = (houses_per_village // houses_per_row) * base_spacing
            village_rect = pygame.Rect(vx, vy, village_w, village_h)
            
            if not safe_city_zone.colliderect(village_rect):
                overlap = False
                for other_v in villages_origins:
                    if math.hypot(vx - other_v[0], vy - other_v[1]) < min_dist_between_villages:
                        overlap = True
                        break
                if not overlap:
                    villages_origins.append((vx, vy))
            attempts += 1

        # Si on n'a pas trouvé assez de places (map trop petite), on garde ce qu'on a
        if not villages_origins:
             villages_origins.append((100, 100)) # Fallback

        # 2. Remplir les villages
        current_counts = [0] * len(villages_origins)
        
        for i in range(population_size + 15): 
            v_idx = i % len(villages_origins)
            origin = villages_origins[v_idx]
            count = current_counts[v_idx]
            
            row = count // houses_per_row
            col = count % houses_per_row
            
            # Calcul de position
            slot_x = origin[0] + (col * base_spacing)
            slot_y = origin[1] + (row * base_spacing)
            
            if row % 2 == 1:
                slot_x += row_stagger
            
            slot_x += random.randint(-random_jitter, random_jitter)
            slot_y += random.randint(-random_jitter, random_jitter)
            slot_x += row * random.randint(-5, 5)

            # --- CORRECTION ICI : LE GARDE-FOU (CLAMPING) ---
            # On force la maison à rester dans l'écran quoi qu'il arrive
            # Marge de 30 pixels pour pas qu'elle soit coupée
            slot_x = max(30, min(self.width - 30, slot_x))
            slot_y = max(30, min(self.height - 30, slot_y))

            self.spawn_slots.append((slot_x, slot_y))
            current_counts[v_idx] += 1
        """Génère des quartiers résidentiels organiques"""
        
        # Configuration des quartiers
        village_count = 6  # Un peu moins de villages, mais plus gros/étalés
        
        # NOUVEAU : Paramètres pour casser la grille
        houses_per_row = 6 
        base_spacing = 45   # Beaucoup plus large (avant c'était ~22)
        row_stagger = 20    # Décalage d'une ligne sur deux (quinconce)
        random_jitter = 12  # Déplacement aléatoire fort pour chaque maison
        
        # Calcul du nombre de maisons par village
        houses_per_village = (population_size // village_count) + 8
        
        villages_origins = []
        
        # 1. Trouver des points d'origine (Loin de la ville)
        attempts = 0
        # On augmente la distance de sécurité entre villages car ils sont plus larges maintenant
        min_dist_between_villages = 250 
        
        while len(villages_origins) < village_count and attempts < 200:
            vx = random.randint(50, self.width - 300)
            vy = random.randint(50, self.height - 300)
            
            # Zone de sécurité Ville (On l'élargit aussi)
            safe_city_zone = self.city_rect.inflate(150, 150)
            
            # Rectangle théorique du village (pour éviter collisions)
            village_w = houses_per_row * base_spacing
            village_h = (houses_per_village // houses_per_row) * base_spacing
            village_rect = pygame.Rect(vx, vy, village_w, village_h)
            
            if not safe_city_zone.colliderect(village_rect):
                overlap = False
                for other_v in villages_origins:
                    if math.hypot(vx - other_v[0], vy - other_v[1]) < min_dist_between_villages:
                        overlap = True
                        break
                
                if not overlap:
                    villages_origins.append((vx, vy))
            attempts += 1

        # 2. Remplir les villages (Distribution organique)
        current_counts = [0] * len(villages_origins)
        
        for i in range(population_size + 15): 
            v_idx = i % len(villages_origins)
            origin = villages_origins[v_idx]
            count = current_counts[v_idx]
            
            # Position Grille théorique
            row = count // houses_per_row
            col = count % houses_per_row
            
            # --- C'EST ICI QUE LA MAGIE OPÈRE ---
            
            # 1. Calcul de base
            slot_x = origin[0] + (col * base_spacing)
            slot_y = origin[1] + (row * base_spacing)
            
            # 2. Effet Quinconce (Une ligne sur deux est décalée vers la droite)
            if row % 2 == 1:
                slot_x += row_stagger
            
            # 3. Chaos contrôlé (Jitter)
            # On décale fortement chaque maison individuellement
            slot_x += random.randint(-random_jitter, random_jitter)
            slot_y += random.randint(-random_jitter, random_jitter)
            
            # 4. Petite rotation subtile du village (optionnel mais sympa)
            # On décale légèrement les lignes pour que le village ne soit pas parfaitement droit
            slot_x += row * random.randint(-5, 5)

            self.spawn_slots.append((slot_x, slot_y))
            current_counts[v_idx] += 1

    def add_house(self, x, y):
        """Génère une maison aléatoire à la position x, y"""
        hx = x - HOUSE_SIZE // 2
        hy = y - HOUSE_SIZE // 2
        style = random.choice([1, 2, 3])
        house_parts = [] 
        door_w = HOUSE_SIZE // 3
        door_h = HOUSE_SIZE // 2.5
        door_rect = pygame.Rect(hx + (HOUSE_SIZE-door_w)//2, hy + HOUSE_SIZE - door_h, door_w, door_h)

        if style == 1: # Classique
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_BEIGE, "data": body})
            roof_h = HOUSE_SIZE // 1.5
            roof_pts = [(x, hy - roof_h), (hx, hy), (hx + HOUSE_SIZE, hy)]
            house_parts.append({"shape": "poly", "color": C_RED, "data": roof_pts})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

        elif style == 2: # Moderne
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_GREY, "data": body})
            roof_rect = pygame.Rect(hx - 1, hy - 3, HOUSE_SIZE + 2, 3)
            house_parts.append({"shape": "rect", "color": C_DARK, "data": roof_rect})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

        elif style == 3: # Cottage
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_BRICK, "data": body})
            roof_h = HOUSE_SIZE 
            roof_pts = [(x, hy - roof_h), (hx - 1, hy), (hx + HOUSE_SIZE + 1, hy)]
            house_parts.append({"shape": "poly", "color": C_DARK, "data": roof_pts})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

        self.houses.append(house_parts)

    def get_valid_spawn_point(self):
        """Retourne un point de spawn depuis la liste pré-calculée"""
        if self.spawn_slots:
            return self.spawn_slots.pop(0) # On prend le premier dispo et on l'enlève
        else:
            # Fallback de sécurité si on a plus de slots (ne devrait pas arriver)
            return random.randint(20, self.width), random.randint(20, self.height)

    def draw(self, screen, zoom, pan_x, pan_y):
        # Fonction utilitaire pour convertir un Rect du monde vers l'écran
        def to_screen_rect(rect):
            return pygame.Rect(
                int(rect.x * zoom + pan_x),
                int(rect.y * zoom + pan_y),
                int(rect.width * zoom),
                int(rect.height * zoom)
            )

        # 1. Routes
        for road in self.roads:
            pygame.draw.rect(screen, ROAD_COLOR, to_screen_rect(road))

        # 2. Maisons
        for house in self.houses:
            for part in house:
                if part["shape"] == "rect":
                    # Conversion du rectangle
                    sr = to_screen_rect(part["data"])
                    pygame.draw.rect(screen, part["color"], sr)
                    
                elif part["shape"] == "poly":
                    # Conversion de la liste de points (pour les toits)
                    screen_points = []
                    for pt in part["data"]:
                        screen_points.append((int(pt[0] * zoom + pan_x), int(pt[1] * zoom + pan_y)))
                    pygame.draw.polygon(screen, part["color"], screen_points)
                    
                elif part["shape"] == "circle":
                    # Conversion cercle
                    center, radius = part["data"]
                    sx = int(center[0] * zoom + pan_x)
                    sy = int(center[1] * zoom + pan_y)
                    sr = int(radius * zoom)
                    pygame.draw.circle(screen, part["color"], (sx, sy), sr)

        # 3. Sol Ville
        pygame.draw.rect(screen, (30, 30, 40), to_screen_rect(self.city_rect)) 

        # 4. Éléments Ville
        for elem in self.city_elements:
            # On dessine le bloc principal
            screen_elem_rect = to_screen_rect(elem["rect"])
            pygame.draw.rect(screen, elem["color"], screen_elem_rect)
            
            details = elem["details"]

            if elem["type"] == "park":
                for path in details["paths"]:
                    # Lignes des chemins
                    p1 = (int(path[0][0] * zoom + pan_x), int(path[0][1] * zoom + pan_y))
                    p2 = (int(path[1][0] * zoom + pan_x), int(path[1][1] * zoom + pan_y))
                    pygame.draw.line(screen, (210, 200, 160), p1, p2, int(8 * zoom))
                
                pygame.draw.ellipse(screen, (50, 150, 220), to_screen_rect(details["pond"]))
                
                for tree_pos in details["trees"]:
                    tx = int(tree_pos[0] * zoom + pan_x)
                    ty = int(tree_pos[1] * zoom + pan_y)
                    tr = int(5 * zoom) # Rayon arbre
                    pygame.draw.circle(screen, (30, 80, 40), (tx+1, ty+2), tr)
                    pygame.draw.circle(screen, (40, 100, 50), (tx, ty), tr)

            elif elem["type"] == "plaza":
                for tile in details["tiles"]:
                    pygame.draw.rect(screen, (180, 170, 160), to_screen_rect(tile))
                
                # Fontaine
                cx = int(details["fountain_center"][0] * zoom + pan_x)
                cy = int(details["fountain_center"][1] * zoom + pan_y)
                pygame.draw.circle(screen, (100, 100, 100), (cx, cy), int(12 * zoom))
                pygame.draw.circle(screen, (50, 150, 220), (cx, cy), int(10 * zoom))
                pygame.draw.circle(screen, (200, 200, 255), (cx, cy), int(3 * zoom))

            elif elem["type"] == "building":
                for win in details["windows"]:
                    pygame.draw.rect(screen, win["color"], to_screen_rect(win["rect"]))
                
                # Petit relief toit
                r = screen_elem_rect
                pygame.draw.line(screen, (80, 80, 90), (r.left, r.top), (r.right, r.top), int(3 * zoom))

            # Contour global
            pygame.draw.rect(screen, (20, 20, 20), screen_elem_rect, 1)

        # 5. Bordure Ville
        pygame.draw.rect(screen, ORANGE, to_screen_rect(self.city_rect), max(1, int(2 * zoom)))