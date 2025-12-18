import pygame
import random
from settings import *

class Map:
    def __init__(self, width, height, population_size):
        self.width = width
        self.height = height
        
        # 1. La Ville (Au centre)
        self.city_size = 240
        self.city_rect = pygame.Rect(
            (width // 2 - self.city_size // 2, height // 2 - self.city_size // 2), 
            (self.city_size, self.city_size)
        )
        
        self.roads = []
        self.city_elements = []
        self.houses = []
        self.existing_house_rects = []

        self.supermarket = None
        self.medical_center = None
        self.sports_complex = None
        
        # 2. Générations
        self._generate_roads()
        self._generate_city_architecture()
        self._generate_fixed_supermarket()
        self._generate_medical_center()
        self._generate_sports_complex()

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
                
                # Parc
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

                # Plaza
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
                    
                # Immeubles
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

    def _generate_fixed_supermarket(self):
        """Génère le supermarché (Vue de dessus avec Damier)"""
        sm_w, sm_h = SM_SIZE
        sx = (self.width - sm_w) // 2
        sy = self.height - sm_h - 85
        
        sm_rect = pygame.Rect(sx, sy, sm_w, sm_h)
        details = []

        # 1. SOL EN DAMIER
        tile_size = 10
        for x in range(sx, sx + sm_w, tile_size):
            for y in range(sy, sy + sm_h, tile_size):
                col_idx = (x - sx) // tile_size
                row_idx = (y - sy) // tile_size
                
                # Alternance des couleurs
                if (col_idx + row_idx) % 2 == 0:
                    color = C_SM_FLOOR
                else:
                    color = C_SM_FLOOR_ALT
                
                # Gestion des bords
                w = min(tile_size, sx + sm_w - x)
                h = min(tile_size, sy + sm_h - y)
                details.append({"shape": "rect", "color": color, "data": pygame.Rect(x, y, w, h)})
        
        # 2. MURS
        wall_thick = 4
        details.append({"shape": "rect", "color": C_SM_WALL, "data": pygame.Rect(sx, sy, sm_w, wall_thick)})
        details.append({"shape": "rect", "color": C_SM_WALL, "data": pygame.Rect(sx, sy + sm_h - wall_thick, sm_w, wall_thick)})
        details.append({"shape": "rect", "color": C_SM_WALL, "data": pygame.Rect(sx, sy, wall_thick, sm_h)})
        details.append({"shape": "rect", "color": C_SM_WALL, "data": pygame.Rect(sx + sm_w - wall_thick, sy, wall_thick, sm_h)})

        # 3. RAYONS
        margin_left = 15
        margin_top = 15
        shelf_w, shelf_h = 12, sm_h - 50 
        aisle_gap = 18    
        current_x = sx + margin_left
        while current_x < sx + sm_w - 20:
            shelf_rect = pygame.Rect(current_x, sy + margin_top, shelf_w, shelf_h)
            details.append({"shape": "rect", "color": C_SM_SHELF, "data": shelf_rect})
            for py in range(shelf_rect.top + 2, shelf_rect.bottom - 2, 4):
                prod_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                details.append({"shape": "rect", "color": prod_color, "data": pygame.Rect(current_x + 2, py, shelf_w - 4, 2)})
            current_x += shelf_w + aisle_gap

        # 4. CAISSES
        checkout_y = sy + sm_h - 25
        checkout_w, checkout_h = 20, 10
        checkout_gap = 30
        start_checkouts = sx + 30
        for i in range(3):
            cx = start_checkouts + (i * checkout_gap)
            if cx + checkout_w > sx + sm_w: break
            details.append({"shape": "rect", "color": C_SM_DESK, "data": pygame.Rect(cx, checkout_y, checkout_w, checkout_h)})
            details.append({"shape": "rect", "color": C_SM_CHECKOUT, "data": pygame.Rect(cx + 2, checkout_y + 2, checkout_w - 4, checkout_h - 4)})

        # 5. ENTRÉE (Portes vitrées)
        door_color = (150, 200, 255)
        details.append({"shape": "rect", "color": door_color, "data": pygame.Rect(sx + sm_w - 50, sy + sm_h - 4, 18, 4)})
        details.append({"shape": "rect", "color": door_color, "data": pygame.Rect(sx + sm_w - 22, sy + sm_h - 4, 18, 4)})
        details.append({"shape": "rect", "color": (150, 150, 150), "data": pygame.Rect(sx + sm_w - 50, sy + sm_h, 46, 3)})

        self.supermarket = {"rect": sm_rect, "details": details}

    def _generate_medical_center(self):
        """Génère le centre médical (Vue de dessus avec Damier)"""
        mc_w, mc_h = MC_SIZE
        mx, my = 135, 50
        
        mc_rect = pygame.Rect(mx, my, mc_w, mc_h)
        details = []

        # 1. SOL EN DAMIER
        tile_size = 10 
        for x in range(mx, mx + mc_w, tile_size):
            for y in range(my, my + mc_h, tile_size):
                col_idx = (x - mx) // tile_size
                row_idx = (y - my) // tile_size
                
                # Alternance des couleurs (Vérifie settings.py pour les couleurs !)
                if (col_idx + row_idx) % 2 == 0:
                    color = C_MC_FLOOR
                else:
                    color = C_MC_FLOOR_ALT
                
                w = min(tile_size, mx + mc_w - x)
                h = min(tile_size, my + mc_h - y)
                details.append({"shape": "rect", "color": color, "data": pygame.Rect(x, y, w, h)})

        # 2. CROIX ROUGE
        cross_thick, cross_size = 8, 24
        cx, cy = mx + mc_w // 2, my + mc_h // 2
        details.append({"shape": "rect", "color": C_MC_CROSS, "data": pygame.Rect(cx - cross_thick//2, cy - cross_size//2, cross_thick, cross_size)})
        details.append({"shape": "rect", "color": C_MC_CROSS, "data": pygame.Rect(cx - cross_size//2, cy - cross_thick//2, cross_size, cross_thick)})

        # 3. LITS
        bed_w, bed_h = 20, 12
        margin_left, spacing = 6, 18
        start_y = my + 10
        for i in range(3):
            bx = mx + margin_left
            by = start_y + (i * spacing)
            details.append({"shape": "rect", "color": C_MC_BED, "data": pygame.Rect(bx, by, bed_w, bed_h)})
            details.append({"shape": "rect", "color": (255, 255, 255), "data": pygame.Rect(bx, by + 1, 4, bed_h - 2)})

        # 4. SALLE D'ATTENTE
        chair_size = 8
        chair_x = mx + mc_w - 15
        for i in range(4):
            cy = my + 10 + (i * 12)
            details.append({"shape": "rect", "color": C_MC_FURNITURE, "data": pygame.Rect(chair_x, cy, chair_size, chair_size)})

        # 5. MURS
        wall_thick = 3
        details.append({"shape": "rect", "color": C_MC_WALL, "data": pygame.Rect(mx, my, mc_w, wall_thick)}) 
        details.append({"shape": "rect", "color": C_MC_WALL, "data": pygame.Rect(mx, my + mc_h - wall_thick, mc_w, wall_thick)}) 
        details.append({"shape": "rect", "color": C_MC_WALL, "data": pygame.Rect(mx, my, wall_thick, mc_h)}) 
        details.append({"shape": "rect", "color": C_MC_WALL, "data": pygame.Rect(mx + mc_w - wall_thick, my, wall_thick, mc_h)}) 

        # 6. ENTRÉE
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(mx + mc_w - 30, my + mc_h - 3, 20, 3)})

        self.medical_center = {"rect": mc_rect, "details": details}

    def _generate_sports_complex(self):
        """Génère le complexe sportif (Stade + Piscine)"""
        sc_w, sc_h = SC_SIZE
        
        # Position : Haut-Droite (avec une marge de 50px)
        sx = self.width - sc_w - 50
        sy = 50
        
        sc_rect = pygame.Rect(sx, sy, sc_w, sc_h)
        details = []

        # 1. SOL GLOBAL (Béton/Pavé)
        details.append({"shape": "rect", "color": C_SC_GROUND, "data": sc_rect})

        # --- ZONE STADE (Partie Haute) ---
        stadium_margin = 10
        stadium_h = 80 # Hauteur réservée au stade
        
        # 2. PISTE D'ATHLÉTISME (Rectangle rouge aux coins arrondis simulés)
        track_rect = pygame.Rect(sx + stadium_margin, sy + stadium_margin, sc_w - 2*stadium_margin, stadium_h)
        details.append({"shape": "rect", "color": C_SC_TRACK, "data": track_rect})
        
        # 3. TERRAIN DE FOOT (Au milieu de la piste)
        field_margin = 10 # Épaisseur de la piste
        field_rect = pygame.Rect(track_rect.left + field_margin, track_rect.top + field_margin, 
                                 track_rect.width - 2*field_margin, track_rect.height - 2*field_margin)
        details.append({"shape": "rect", "color": C_SC_GRASS, "data": field_rect})

        # 4. MARQUAGE TERRAIN (Lignes blanches)
        # Ligne médiane
        center_x = field_rect.centerx
        details.append({"shape": "rect", "color": C_SC_LINES, "data": pygame.Rect(center_x - 1, field_rect.top, 2, field_rect.height)})
        
        # Rond central (Cercle blanc + Cercle vert plus petit pour faire un anneau)
        details.append({"shape": "circle", "color": C_SC_LINES, "data": ((center_x, field_rect.centery), 12)})
        details.append({"shape": "circle", "color": C_SC_GRASS, "data": ((center_x, field_rect.centery), 10)})
        
        # Cages de but (petits rectangles blancs aux extrémités)
        goal_w, goal_h = 4, 16
        details.append({"shape": "rect", "color": C_SC_LINES, "data": pygame.Rect(field_rect.left + 2, field_rect.centery - goal_h//2, goal_w, goal_h)})
        details.append({"shape": "rect", "color": C_SC_LINES, "data": pygame.Rect(field_rect.right - 2 - goal_w, field_rect.centery - goal_h//2, goal_w, goal_h)})

        # --- ZONE PISCINE (Partie Basse) ---
        pool_area_y = sy + stadium_h + 15
        pool_w = 80
        pool_h = 25
        # On centre la piscine horizontalement par rapport au complexe
        pool_x = sx + (sc_w - pool_w) // 2
        
        # 5. BASSIN (Bleu foncé)
        pool_rect = pygame.Rect(pool_x, pool_area_y, pool_w, pool_h)
        details.append({"shape": "rect", "color": C_SC_WATER, "data": pool_rect})
        
        # 6. LIGNES D'EAU (Lignes horizontales bleu clair)
        lane_height = 5
        for ly in range(pool_rect.top + lane_height, pool_rect.bottom, lane_height):
             details.append({"shape": "rect", "color": C_SC_LANE, "data": pygame.Rect(pool_x, ly, pool_w, 1)})
             
        # 7. BORDURE PISCINE (Dalles blanches autour)
        border_thick = 2
        # Juste 4 rectangles pour faire le contour
        details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(pool_x - border_thick, pool_area_y - border_thick, pool_w + 2*border_thick, border_thick)}) # Haut
        details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(pool_x - border_thick, pool_area_y + pool_h, pool_w + 2*border_thick, border_thick)}) # Bas
        details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(pool_x - border_thick, pool_area_y, border_thick, pool_h)}) # Gauche
        details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(pool_x + pool_w, pool_area_y, border_thick, pool_h)}) # Droite

        # 8. MUR D'ENCEINTE (Optionnel, pour finir propre)
        wall_thick = 2
        details.append({"shape": "rect", "color": (100, 100, 100), "data": pygame.Rect(sx, sy, sc_w, wall_thick)})
        details.append({"shape": "rect", "color": (100, 100, 100), "data": pygame.Rect(sx, sy + sc_h - wall_thick, sc_w, wall_thick)})
        details.append({"shape": "rect", "color": (100, 100, 100), "data": pygame.Rect(sx, sy, wall_thick, sc_h)})
        details.append({"shape": "rect", "color": (100, 100, 100), "data": pygame.Rect(sx + sc_w - wall_thick, sy, wall_thick, sc_h)})

        self.sports_complex = {"rect": sc_rect, "details": details}
        

    def get_valid_spawn_point(self):

        attempts = 0
        max_attempts = 1000 # pour éviter de boucler si map pleine
        
        while attempts < max_attempts:

            attempts += 1

            x = random.randint(20, self.width - 20)
            y = random.randint(20, self.height - 20)

            house_rect = pygame.Rect(x - HOUSE_SIZE//2, y - HOUSE_SIZE//2, HOUSE_SIZE, HOUSE_SIZE)
            
            if self.city_rect.inflate(20, 20).colliderect(house_rect): continue
            if self.supermarket and self.supermarket["rect"].inflate(200, 200).colliderect(house_rect): continue
            if self.medical_center and self.medical_center["rect"].inflate(200, 200).colliderect(house_rect): continue
            if self.sports_complex:
                if self.sports_complex["rect"].inflate(150, 150).colliderect(house_rect): continue

            collision_index = house_rect.inflate(15, 15).collidelist(self.existing_house_rects)
            if collision_index != -1:
                continue
            
            return x, y
        
        print("Attention : Map trop chargée, spawn forcé.")
        return random.randint(20, self.width - 20), random.randint(20, self.height - 20)

    def add_house(self, x, y):
        hx = x - HOUSE_SIZE // 2
        hy = y - HOUSE_SIZE // 2

        house_footprint = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
        self.existing_house_rects.append(house_footprint)

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

    def draw(self, screen, zoom, pan_x, pan_y, label_font):
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
                    pygame.draw.rect(screen, part["color"], to_screen_rect(part["data"]))
                elif part["shape"] == "poly":
                    screen_points = [(int(pt[0] * zoom + pan_x), int(pt[1] * zoom + pan_y)) for pt in part["data"]]
                    pygame.draw.polygon(screen, part["color"], screen_points)
                elif part["shape"] == "circle":
                    center, radius = part["data"]
                    sx = int(center[0] * zoom + pan_x)
                    sy = int(center[1] * zoom + pan_y)
                    sr = int(radius * zoom)
                    pygame.draw.circle(screen, part["color"], (sx, sy), sr)

        # 3. Supermarché
        if self.supermarket:
            for part in self.supermarket["details"]:
                 pygame.draw.rect(screen, part["color"], to_screen_rect(part["data"]))
            
            text_surf = label_font.render("SUPERMARCHÉ", True, WHITE)
            sm_rect = self.supermarket["rect"]
            text_x = (sm_rect.centerx * zoom + pan_x) - (text_surf.get_width() // 2)
            text_y = (sm_rect.top * zoom + pan_y) - 25
            screen.blit(text_surf, (text_x, text_y))

        # 4. Centre Médical
        if self.medical_center:
            for part in self.medical_center["details"]:
                 pygame.draw.rect(screen, part["color"], to_screen_rect(part["data"]))
            
            text_surf = label_font.render("CENTRE MÉDICAL", True, WHITE)
            mc_rect = self.medical_center["rect"]
            text_x = (mc_rect.centerx * zoom + pan_x) - (text_surf.get_width() // 2)
            text_y = (mc_rect.top * zoom + pan_y) - 20
            screen.blit(text_surf, (text_x, text_y))


        # 4.bis Complexe Sportif
        if self.sports_complex:
            # Bâtiment
            for part in self.sports_complex["details"]:
                if part["shape"] == "rect":
                    pygame.draw.rect(screen, part["color"], to_screen_rect(part["data"]))
                elif part["shape"] == "circle":
                    # Pour les cercles (rond central du terrain)
                    center, radius = part["data"]
                    sx = int(center[0] * zoom + pan_x)
                    sy = int(center[1] * zoom + pan_y)
                    sr = int(radius * zoom)
                    pygame.draw.circle(screen, part["color"], (sx, sy), sr)

            # Texte "COMPLEXE SPORTIF"
            text_surf = label_font.render("COMPLEXE SPORTIF", True, WHITE)
            sc_rect = self.sports_complex["rect"]
            text_x = (sc_rect.centerx * zoom + pan_x) - (text_surf.get_width() // 2)
            text_y = (sc_rect.top * zoom + pan_y) - 20
            screen.blit(text_surf, (text_x, text_y))

        # 5. Ville
        pygame.draw.rect(screen, (30, 30, 40), to_screen_rect(self.city_rect)) 
        for elem in self.city_elements:
            pygame.draw.rect(screen, elem["color"], to_screen_rect(elem["rect"]))
            details = elem["details"]
            
            if elem["type"] == "park":
                for path in details["paths"]:
                    p1 = (int(path[0][0] * zoom + pan_x), int(path[0][1] * zoom + pan_y))
                    p2 = (int(path[1][0] * zoom + pan_x), int(path[1][1] * zoom + pan_y))
                    pygame.draw.line(screen, (210, 200, 160), p1, p2, int(8 * zoom))
                pygame.draw.ellipse(screen, (50, 150, 220), to_screen_rect(details["pond"]))
                for tree_pos in details["trees"]:
                    tx = int(tree_pos[0] * zoom + pan_x)
                    ty = int(tree_pos[1] * zoom + pan_y)
                    tr = int(5 * zoom)
                    pygame.draw.circle(screen, (30, 80, 40), (tx+1, ty+2), tr)
                    pygame.draw.circle(screen, (40, 100, 50), (tx, ty), tr)

            elif elem["type"] == "plaza":
                for tile in details["tiles"]:
                    pygame.draw.rect(screen, (180, 170, 160), to_screen_rect(tile))
                cx = int(details["fountain_center"][0] * zoom + pan_x)
                cy = int(details["fountain_center"][1] * zoom + pan_y)
                pygame.draw.circle(screen, (100, 100, 100), (cx, cy), int(12 * zoom))
                pygame.draw.circle(screen, (50, 150, 220), (cx, cy), int(10 * zoom))
                pygame.draw.circle(screen, (200, 200, 255), (cx, cy), int(3 * zoom))

            elif elem["type"] == "building":
                for win in details["windows"]:
                    pygame.draw.rect(screen, win["color"], to_screen_rect(win["rect"]))
                r = to_screen_rect(elem["rect"])
                pygame.draw.line(screen, (80, 80, 90), (r.left, r.top), (r.right, r.top), int(3 * zoom))

            pygame.draw.rect(screen, (20, 20, 20), to_screen_rect(elem["rect"]), 1)

        pygame.draw.rect(screen, ORANGE, to_screen_rect(self.city_rect), max(1, int(2 * zoom)))