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
        
        # Listes de données
        self.roads = []
        self.city_elements = []
        self.houses = []
        self.house_slots = [] 
        self.grass_tiles = []

        self.manual_trees_1 = []   
        self.manual_trees_2 = []   
        self.manual_bushes = [] 
        self.manual_flowers = []
        
        self.supermarket = None
        self.medical_center = None
        self.sports_complex = None
        
        # 2. Générations
        self._generate_grass()
        self._generate_roads()
        self._generate_city_architecture()
        self._generate_fixed_supermarket()
        self._generate_medical_center()
        self._generate_sports_complex()

        self._define_house_slots()
        self._define_vegetation_slots()

    
    def _generate_grass(self):
        """Génère un sol en damier uniforme et doux"""
        self.grass_tiles = []
        
        # Taille fixe pour tous les carrés (60px est un bon équilibre)
        tile_size = 60 
        
        # On calcule combien de carrés il faut pour remplir la largeur et hauteur
        # On ajoute +1 pour être sûr de couvrir les bords si la division n'est pas ronde
        cols = (self.width // tile_size) + 1
        rows = (self.height // tile_size) + 1

        for col in range(cols):
            for row in range(rows):
                x = col * tile_size
                y = row * tile_size
                
                # --- LOGIQUE DU DAMIER ---
                # Si la somme de la colonne et de la ligne est paire -> Couleur 1
                # Sinon -> Couleur 2
                if (col + row) % 2 == 0:
                    color = C_GRASS_1
                else:
                    color = C_GRASS_2
                
                # On crée le rectangle
                rect = pygame.Rect(x, y, tile_size, tile_size)
                self.grass_tiles.append({"rect": rect, "color": color})

    def _generate_roads(self):
        BLOCK_SIZE_MAP = 120  
        ROAD_WIDTH = 12   
        margin = 20
        self.roads.append(pygame.Rect(0, self.city_rect.top - margin, self.width, 16))
        self.roads.append(pygame.Rect(0, self.city_rect.bottom + margin - 16, self.width, 16))
        self.roads.append(pygame.Rect(self.city_rect.left - margin, 0, 16, self.height))
        self.roads.append(pygame.Rect(self.city_rect.right + margin - 16, 0, 16, self.height))
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
                
                if row in [0, 1] and col in [2, 3]: # Parc
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
                elif row in [2, 3] and col in [0, 1]: # Plaza
                    if row == 2 and col == 0:
                        plaza_margin = 20
                        plaza_rect = pygame.Rect(bx + plaza_margin, by + plaza_margin, (block_size*2) - 2*plaza_margin, (block_size*2) - 2*plaza_margin)
                        plaza_details = {"tiles": [], "fountain_center": plaza_rect.center}
                        for tx in range(plaza_rect.left, plaza_rect.right, 10):
                            for ty in range(plaza_rect.top, plaza_rect.bottom, 10):
                                if (tx + ty) % 20 == 0: plaza_details["tiles"].append(pygame.Rect(tx, ty, 9, 9))
                        self.city_elements.append({"type": "plaza", "rect": plaza_rect, "color": (200, 190, 180), "details": plaza_details})
                    continue
                else: # Immeubles
                    shade = random.randint(40, 70) 
                    color = (shade, shade, shade + 10)
                    windows = []
                    for wx in range(rect.left + 4, rect.right - 4, 10):
                        for wy in range(rect.top + 4, rect.bottom - 4, 10):
                            if random.random() < 0.8:
                                win_color = (20, 20, 30)
                                if random.random() < 0.3: win_color = (200, 200, 100)
                                windows.append({"rect": pygame.Rect(wx, wy, 6, 6), "color": win_color})
                    self.city_elements.append({"type": "building", "rect": rect, "color": color, "details": {"windows": windows}})

    def _define_house_slots(self):
        """
        Définit les positions exactes des 250 maisons.
        Format : (x, y)
        """
        self.house_slots = [
            
            # --- QUARTIER BAS-GAUCHE (~80 maisons) ---
            (30, 750), (60, 750), (90, 750), (120, 750), (150, 750), (180, 750), (210, 750), (240, 750), (270, 750), (300, 750), (330, 750),
            (30, 720), (30, 690), (30, 660), (30, 630), (30, 600), (30, 570), (30, 540),
            (60, 540), (90, 540), (120, 540), (150, 540), (180, 540), (210, 540), (240, 540),
            (120, 570), (120, 600), (120, 630), (120, 660), (120, 690), (120, 720),
            (60, 630), (90, 630),
            (150, 630), (180, 630), (210, 630), (240, 630), (270, 630), (300, 630),
            (330, 630), (330, 600), (330, 570), 
            (300, 570), (270, 570), (240, 570), 
            (240, 600), 
            (180, 690), (210, 690), (240, 690), (270, 690),
            (270, 720), (240, 720), (210, 720), (180, 720),
            (60, 600), (90, 600),
            (150, 660), (150, 690),
            (300, 660), (300, 690), (300, 720),
            (330, 660), (330, 690), (330, 720),
            (30, 510), (60, 510), (90, 510),
            (360, 750), (360, 720), (360, 690), (360, 660), (360, 630),      


            # --- QUARTIER EST (Étendu vers le bas) ---
            (950, 310), (950, 340), (950, 370), (950, 400), (950, 430), (950, 460), (950, 490), (950, 520), (950, 550),
            (950, 580), (950, 610), (950, 640), 
            (860, 370), (890, 370), (920, 370), 
            (980, 370), (1010, 370), (1040, 370), (1070, 370),
            (1040, 400), (1040, 430), (1040, 460), 
            (1070, 460), (1100, 460),
            (1100, 430), (1100, 400), 
            (1070, 400),
            (920, 460), (890, 460), (860, 460), 
            (860, 490), (860, 520),
            (890, 520), (920, 520),
            (890, 400), (890, 430),
            (920, 550), (980, 550), (1010, 550), (1040, 550),
            (860, 550), (890, 550),
            (860, 580), (890, 580), (920, 580),
            (890, 610), (920, 610),
            (980, 580), (1010, 580), (1040, 580),
            (980, 610), (1010, 610), (1040, 610),
            (950, 280), 
            (920, 280), (980, 280), (1010, 280),
            (1010, 250), (1010, 310),
            (1130, 350), (1130, 380), (1130, 410), (1130, 440), (1130, 470),
            (1130, 500), (1130, 530),
            (980, 400), (980, 430), (980, 460), (980, 490), (980, 520),
            (1010, 400), (1010, 430), (1010, 460), (1010, 490), (1010, 520),
            (920, 490),     


            # --- QUARTIER NORD (Centré sur 550, 100) ---
            (340, 70), (370, 70), (400, 70), (430, 70), (460, 70), (490, 70), (520, 70),
            (550, 70),
            (580, 70), (610, 70), (640, 70), (670, 70), (700, 70), (730, 70), (760, 70),
            (550, 100), (550, 130), (550, 160), (550, 190), (550, 220),
            (400, 100), (400, 130), (400, 160), (400, 190),
            (430, 190), (460, 190), (490, 190), (520, 190),
            (700, 100), (700, 130), (700, 160), (700, 190), 
            (670, 190), (640, 190), (610, 190), (580, 190),
            (460, 100), (460, 130), (460, 160),
            (640, 100), (640, 130), (640, 160),
            (430, 250), (460, 250), (490, 250), (520, 250), 
            (550, 250), 
            (580, 250), (610, 250), (640, 250), (670, 250),
            (520, 40), (550, 40), (580, 40),
            (370, 220), (340, 220), (340, 250),
            (730, 220), (760, 220), (760, 250),
            (490, 130), (610, 130),
            (520, 130), (580, 130),

        ]

    def get_valid_spawn_point(self):
        """Distribue les places définies une par une"""
        if self.house_slots:
            return self.house_slots.pop(0) # On prend la première dispo et on l'enlève
        else:
            # Sécurité si ta liste est plus courte que la population
            return random.randint(20, self.width), random.randint(20, self.height)

    def add_house(self, x, y):
        hx = x - HOUSE_SIZE // 2
        hy = y - HOUSE_SIZE // 2
        style = random.choice([1, 2, 3])
        house_parts = [] 
        
        # Dimensions communes
        door_w, door_h = HOUSE_SIZE // 3, HOUSE_SIZE // 2.5
        door_rect = pygame.Rect(hx + (HOUSE_SIZE-door_w)//2, hy + HOUSE_SIZE - door_h, door_w, door_h)
        
        # Géométrie du toit plat (Une bande rectangle juste au dessus du corps)
        # x-1 et width+2 pour dépasser légèrement sur les côtés (débord de toiture)
        roof_rect = pygame.Rect(hx - 1, hy - 3, HOUSE_SIZE + 2, 4)

        if style == 1: # Style Beige (Toit plat Rouge)
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_BEIGE, "data": body})
            house_parts.append({"shape": "rect", "color": C_RED, "data": roof_rect}) # C'était un polygone avant
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

        elif style == 2: # Style Moderne Gris (Toit plat Foncé)
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_GREY, "data": body})
            house_parts.append({"shape": "rect", "color": C_DARK, "data": roof_rect})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

        elif style == 3: # Style Brique (Toit plat Foncé)
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_BRICK, "data": body})
            house_parts.append({"shape": "rect", "color": C_DARK, "data": roof_rect}) # C'était un polygone avant
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})
        
        self.houses.append(house_parts)

        # --- BATIMENTS SPECIAUX ---
    
    def _generate_fixed_supermarket(self):
        sm_w, sm_h = SM_SIZE
        sx, sy = (self.width - sm_w) // 2, self.height - sm_h - 40 
        sm_rect = pygame.Rect(sx, sy, sm_w, sm_h)
        details = []

        # 1. Sol Damier
        tile_size = 10
        for x in range(sx, sx + sm_w, tile_size):
            for y in range(sy, sy + sm_h, tile_size):
                col = C_SM_FLOOR if ((x - sx)//10 + (y - sy)//10) % 2 == 0 else C_SM_FLOOR_ALT
                w = min(tile_size, sx + sm_w - x)
                h = min(tile_size, sy + sm_h - y)
                details.append({"shape": "rect", "color": col, "data": pygame.Rect(x, y, w, h)})
        
        # 2. Murs extérieurs
        for r in [pygame.Rect(sx, sy, sm_w, 4), pygame.Rect(sx, sy + sm_h - 4, sm_w, 4), pygame.Rect(sx, sy, 4, sm_h), pygame.Rect(sx + sm_w - 4, sy, 4, sm_h)]:
            details.append({"shape": "rect", "color": C_SM_WALL, "data": r})

        # 3. Rayons Verticaux (Gauche et Centre)
        # On laisse de la place à droite pour les nouveaux rayons horizontaux
        limit_vertical = sx + sm_w - 70 
        current_x = sx + 15
        while current_x < limit_vertical:
            details.append({"shape": "rect", "color": C_SM_SHELF, "data": pygame.Rect(current_x, sy + 15, 12, sm_h - 60)})
            for py in range(sy + 17, sy + sm_h - 45, 4):
                 details.append({"shape": "rect", "color": (random.randint(100,255),random.randint(100,255),random.randint(100,255)), "data": pygame.Rect(current_x + 2, py, 8, 2)})
            current_x += 25 

        # 4. NOUVEAU : Rayons Horizontaux (Zone Droite)
        # On les empile verticalement
        right_zone_x = sx + sm_w - 55
        shelf_w_horiz = 40
        shelf_h_horiz = 10
        for hy in range(sy + 15, sy + sm_h - 50, 20): # Ecartement de 20px
            # L'étagère
            details.append({"shape": "rect", "color": C_SM_SHELF, "data": pygame.Rect(right_zone_x, hy, shelf_w_horiz, shelf_h_horiz)})
            # Les produits dessus (petits carrés alignés horizontalement)
            for px in range(right_zone_x + 2, right_zone_x + shelf_w_horiz - 2, 6):
                prod_col = (random.randint(100,255),random.randint(100,255),random.randint(100,255))
                details.append({"shape": "rect", "color": prod_col, "data": pygame.Rect(px, hy + 2, 4, 6)})

        # 5. Caisses (5 caisses)
        for i in range(5):
            cx = sx + 30 + (i * 35)
            if cx + 25 < sx + sm_w:
                details.append({"shape": "rect", "color": C_SM_DESK, "data": pygame.Rect(cx, sy + sm_h - 35, 20, 12)})
                details.append({"shape": "rect", "color": C_SM_CHECKOUT, "data": pygame.Rect(cx + 2, sy + sm_h - 33, 16, 8)})

        # 6. Entrée
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(sx + sm_w - 70, sy + sm_h - 4, 25, 4)})
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(sx + sm_w - 35, sy + sm_h - 4, 25, 4)})
        
        self.supermarket = {"rect": sm_rect, "details": details}

    def _generate_medical_center(self):
        mc_w, mc_h = MC_SIZE
        mx, my = 100, 100
        mc_rect = pygame.Rect(mx, my, mc_w, mc_h)
        details = []

        # 1. Sol
        for x in range(mx, mx + mc_w, 10):
            for y in range(my, my + mc_h, 10):
                col = C_MC_FLOOR if ((x - mx)//10 + (y - my)//10) % 2 == 0 else C_MC_FLOOR_ALT
                w = min(10, mx + mc_w - x)
                h = min(10, my + mc_h - y)
                details.append({"shape": "rect", "color": col, "data": pygame.Rect(x, y, w, h)})
        
        # 2. Cloison interne
        partition_x = mx + mc_w - 60
        details.append({"shape": "rect", "color": C_MC_WALL, "data": pygame.Rect(partition_x, my, 3, mc_h - 30)})

        # 3. Zone Gauche : Les Lits
        bed_w, bed_h = 20, 12
        # On définit exactement où finissent les lits pour placer la croix après
        max_bed_x = 0 
        for col in range(2):
            for row in range(3):
                bx = mx + 10 + (col * 35)
                by = my + 15 + (row * 25)
                max_bed_x = max(max_bed_x, bx + bed_w)
                details.append({"shape": "rect", "color": C_MC_BED, "data": pygame.Rect(bx, by, bed_w, bed_h)})
                details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(bx, by + 1, 4, bed_h - 2)})

        # 4. Zone Droite : Bureau
        desk_x = partition_x + 15
        desk_y = my + 20
        details.append({"shape": "rect", "color": (100, 100, 100), "data": pygame.Rect(desk_x, desk_y, 30, 15)})
        details.append({"shape": "rect", "color": (50, 50, 50), "data": pygame.Rect(desk_x + 32, desk_y + 2, 8, 8)})

        # 5. CORRECTION CROIX ROUGE
        # On la place pile entre la fin des lits (max_bed_x) et le mur de séparation (partition_x)
        # Et on la centre verticalement
        center_zone_x = (max_bed_x + partition_x) // 2
        center_zone_y = my + mc_h // 2
        
        details.append({"shape": "rect", "color": C_MC_CROSS, "data": pygame.Rect(center_zone_x - 5, center_zone_y - 15, 10, 30)})
        details.append({"shape": "rect", "color": C_MC_CROSS, "data": pygame.Rect(center_zone_x - 15, center_zone_y - 5, 30, 10)})

        # 6. Salle d'attente
        for i in range(3):
            details.append({"shape": "rect", "color": C_MC_FURNITURE, "data": pygame.Rect(mx + mc_w - 15, my + mc_h - 40 + (i*10), 8, 8)})

        # 7. Murs et Porte
        for r in [pygame.Rect(mx, my, mc_w, 3), pygame.Rect(mx, my + mc_h - 3, mc_w, 3), pygame.Rect(mx, my, 3, mc_h), pygame.Rect(mx + mc_w - 3, my, 3, mc_h)]:
            details.append({"shape": "rect", "color": C_MC_WALL, "data": r})
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(mx + mc_w - 40, my + mc_h - 3, 25, 3)})

        self.medical_center = {"rect": mc_rect, "details": details}

    def _generate_sports_complex(self):
        sc_w, sc_h = SC_SIZE
        sx, sy = self.width - sc_w - 150, 50
        sc_rect = pygame.Rect(sx, sy, sc_w, sc_h)
        details = []
        details.append({"shape": "rect", "color": C_SC_GROUND, "data": sc_rect})
        # Stade
        stadium_y = sy + 25 
        for i in range(3): details.append({"shape": "rect", "color": C_SC_SEATS, "data": pygame.Rect(sx + 10, sy + 5 + i*6, sc_w - 20, 4)})
        track_rect = pygame.Rect(sx + 5, stadium_y, sc_w - 10, 75)
        details.append({"shape": "rect", "color": C_SC_TRACK, "data": track_rect})
        field_rect = pygame.Rect(track_rect.x + 8, track_rect.y + 8, track_rect.w - 16, track_rect.h - 16)
        cx = field_rect.x
        idx = 0
        while cx < field_rect.right:
            w = min(10, field_rect.right - cx)
            col = C_SC_GRASS if idx % 2 == 0 else C_SC_GRASS_DARK
            details.append({"shape": "rect", "color": col, "data": pygame.Rect(cx, field_rect.y, w, field_rect.h)})
            cx += 10; idx += 1
        # Lignes
        for r in [pygame.Rect(field_rect.x, field_rect.y, field_rect.w, 1), pygame.Rect(field_rect.x, field_rect.bottom-1, field_rect.w, 1), pygame.Rect(field_rect.x, field_rect.y, 1, field_rect.h), pygame.Rect(field_rect.right-1, field_rect.y, 1, field_rect.h), pygame.Rect(field_rect.centerx, field_rect.y, 1, field_rect.h)]:
            details.append({"shape": "rect", "color": C_SC_LINES, "data": r})
        details.append({"shape": "circle", "color": C_SC_LINES, "data": (field_rect.center, 10)})
        details.append({"shape": "circle", "color": C_SC_GRASS_DARK, "data": (field_rect.center, 9)})
        # Piscine
        pool_y = stadium_y + 75 + 10
        pool_x = sx + (sc_w - 70) // 2
        details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(pool_x - 3, pool_y - 3, 76, 26)})
        details.append({"shape": "rect", "color": C_SC_WATER, "data": pygame.Rect(pool_x, pool_y, 70, 20)})
        for i in range(4):
            details.append({"shape": "rect", "color": C_SC_LANE, "data": pygame.Rect(pool_x, pool_y + i*5, 70, 1)})
            details.append({"shape": "rect", "color": BLACK, "data": pygame.Rect(pool_x - 2, pool_y + i*5 + 1, 2, 3)})
        self.sports_complex = {"rect": sc_rect, "details": details}

    def _define_vegetation_slots(self):
        """
        Définit les positions de la végétation.
        Format : (x, y)
        """
        # 1. ARBRES TYPE 1 (Classiques)
        self.manual_trees_1 = [
            (275, 110), (275, 135), (275, 160), (275, 185),
        ]

        # 2. ARBRES TYPE 2 (Pins / Sombres)
        self.manual_trees_2 = [
            (600, 600), (620, 610), (610, 630),
        ]

        # 3. BUISSONS (Petits cercles verts)
        self.manual_bushes = [
            (100, 150), (110, 150),
        ]

        # 4. PARTERRES DE FLEURS (Rectangles de terre colorés)
        self.manual_flowers = [
            (500, 700),
        ]

    def draw(self, screen, zoom, pan_x, pan_y, label_font):
        # --- 1. OPTIMISATION : GESTION CAMÉRA ---
        # On récupère la taille de l'écran pour savoir si on est dedans
        screen_w, screen_h = screen.get_size()
        screen_bounds = pygame.Rect(0, 0, screen_w, screen_h)

        def to_screen_rect(rect):
            # Calcul de la position écran avec le zoom et le pan
            screen_x = int(rect.x * zoom + pan_x)
            screen_y = int(rect.y * zoom + pan_y)
            screen_w = int(rect.width * zoom)
            screen_h = int(rect.height * zoom)
            
            final_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)
            
            # Si le rectangle ne touche pas l'écran, on renvoie None (on ne dessine pas)
            if not final_rect.colliderect(screen_bounds):
                return None
            return final_rect

        # --- 2. DESSIN DU SOL (HERBE) ---
        # On remplit d'abord avec la couleur de base
        screen.fill(C_GRASS_1) 
        
        # On dessine les tuiles texturées
        for tile in self.grass_tiles:
            r = to_screen_rect(tile["rect"])
            if r: 
                pygame.draw.rect(screen, tile["color"], r)

        # --- 3. ROUTES ---
        for road in self.roads:
            r = to_screen_rect(road)
            if r: pygame.draw.rect(screen, ROAD_COLOR, r)
        
        # --- 4. VÉGÉTATION BASSE (FLEURS & BUISSONS) ---
        # Parterres de fleurs
        w_flow, h_flow = FLOWERBED_SIZE
        for (fx, fy) in self.manual_flowers:
            # On vérifie si c'est dans l'écran
            r = to_screen_rect(pygame.Rect(fx - w_flow//2, fy - h_flow//2, w_flow, h_flow))
            if r:
                pygame.draw.rect(screen, C_SOIL, r)
                # Petits points colorés (simulés)
                for i in range(5):
                    dot_x = fx - w_flow//2 + ((fx * i * 7) % w_flow)
                    dot_y = fy - h_flow//2 + ((fy * i * 3) % h_flow)
                    col = [C_FLOWER_RED, C_FLOWER_YEL, C_FLOWER_PRP][(fx+fy+i)%3]
                    sx = int(dot_x * zoom + pan_x)
                    sy = int(dot_y * zoom + pan_y)
                    # On dessine le point seulement s'il est dans l'écran
                    if 0 <= sx < screen_w and 0 <= sy < screen_h:
                        pygame.draw.circle(screen, col, (sx, sy), max(1, int(2*zoom)))

        # Buissons
        for (bx, by) in self.manual_bushes:
            sx = int(bx * zoom + pan_x)
            sy = int(by * zoom + pan_y)
            # Vérif écran rapide
            if -50 < sx < screen_w + 50 and -50 < sy < screen_h + 50:
                br = int(BUSH_RADIUS * zoom)
                pygame.draw.circle(screen, C_BUSH_MAIN, (sx, sy), br)
                pygame.draw.circle(screen, C_BUSH_LIGHT, (sx - int(1*zoom), sy - int(1*zoom)), int(br*0.6))

        # --- 5. MAISONS ---
        for house in self.houses:
            for part in house:
                if part["shape"] == "rect":
                    r = to_screen_rect(part["data"])
                    if r: pygame.draw.rect(screen, part["color"], r)
                elif part["shape"] == "poly": 
                    # Note : avec les toits plats, on n'utilise plus trop poly, mais on garde au cas où
                    pts = [(int(pt[0]*zoom+pan_x), int(pt[1]*zoom+pan_y)) for pt in part["data"]]
                    # Vérif sommaire si un point est dans l'écran
                    if any(0 <= p[0] <= screen_w and 0 <= p[1] <= screen_h for p in pts):
                        pygame.draw.polygon(screen, part["color"], pts)
        
        # --- 6. BÂTIMENTS SPÉCIAUX ---
        for building, name in [(self.supermarket, "SUPERMARCHÉ"), (self.medical_center, "CENTRE MÉDICAL"), (self.sports_complex, "COMPLEXE SPORTIF")]:
            if building:
                # On vérifie si le bâtiment est visible globalement
                b_rect = to_screen_rect(building["rect"])
                if b_rect: # Si le rectangle principal est visible
                    for part in building["details"]:
                        if part["shape"] == "rect": 
                            pr = to_screen_rect(part["data"])
                            if pr: pygame.draw.rect(screen, part["color"], pr)
                        elif part["shape"] == "circle":
                            c, r = part["data"]
                            sx = int(c[0]*zoom+pan_x)
                            sy = int(c[1]*zoom+pan_y)
                            sr = int(r*zoom)
                            pygame.draw.circle(screen, part["color"], (sx, sy), sr)
                    
                    # Texte
                    txt = label_font.render(name, True, WHITE)
                    screen.blit(txt, (b_rect.centerx - txt.get_width()//2, b_rect.top - 20))

        # --- 7. VILLE CENTRALE ---
        city_r = to_screen_rect(self.city_rect)
        if city_r:
            pygame.draw.rect(screen, (30, 30, 40), city_r) 
            for elem in self.city_elements:
                r = to_screen_rect(elem["rect"])
                if r: # Si l'élément de ville est visible
                    if elem["type"] == "building":
                        for win in elem["details"]["windows"]: 
                            wr = to_screen_rect(win["rect"])
                            if wr: pygame.draw.rect(screen, win["color"], wr)
                        
                        pygame.draw.line(screen, (80, 80, 90), (r.left, r.top), (r.right, r.top), int(3 * zoom))
                        pygame.draw.rect(screen, elem["color"], r, 1)
                    else:
                         pygame.draw.rect(screen, elem["color"], r)
                    
                    # Détails Parc
                    if elem["type"] == "park":
                        for path in elem["details"]["paths"]:
                             p1 = (int(path[0][0]*zoom+pan_x), int(path[0][1]*zoom+pan_y))
                             p2 = (int(path[1][0]*zoom+pan_x), int(path[1][1]*zoom+pan_y))
                             pygame.draw.line(screen, (210, 200, 160), p1, p2, int(8*zoom))
                        pr = to_screen_rect(elem["details"]["pond"])
                        if pr: pygame.draw.ellipse(screen, (50, 150, 220), pr)
                        for t in elem["details"]["trees"]:
                            tx, ty = int(t[0]*zoom+pan_x), int(t[1]*zoom+pan_y)
                            tr = int(5*zoom)
                            pygame.draw.circle(screen, (30, 80, 40), (tx+1, ty+2), tr)
                            pygame.draw.circle(screen, (40, 100, 50), (tx, ty), tr)
                    # Détails Plaza
                    elif elem["type"] == "plaza":
                        for tile in elem["details"]["tiles"]: 
                            tr = to_screen_rect(tile)
                            if tr: pygame.draw.rect(screen, (180, 170, 160), tr)
                        c = elem["details"]["fountain_center"]
                        cx, cy = int(c[0]*zoom+pan_x), int(c[1]*zoom+pan_y)
                        pygame.draw.circle(screen, (100, 100, 100), (cx, cy), int(12*zoom))
                        pygame.draw.circle(screen, (50, 150, 220), (cx, cy), int(10*zoom))

            # Cadre Orange Ville
            pygame.draw.rect(screen, ORANGE, city_r, max(1, int(2 * zoom)))

        # --- 8. VÉGÉTATION HAUTE (ARBRES) ---
        # Arbres Type 1 (Verts)
        for (tx, ty) in self.manual_trees_1:
            sx = int(tx * zoom + pan_x)
            sy = int(ty * zoom + pan_y)
            # Optimisation simple (box)
            if -50 < sx < screen_w + 50 and -50 < sy < screen_h + 50:
                tr = int(TREE_1_RADIUS * zoom)
                pygame.draw.circle(screen, C_TREE_1_MAIN, (sx, sy), tr)
                pygame.draw.circle(screen, C_TREE_1_LIGHT, (sx - int(3*zoom), sy - int(3*zoom)), int(tr * 0.6))
            
        # Arbres Type 2 (Sombres)
        for (tx, ty) in self.manual_trees_2:
            sx = int(tx * zoom + pan_x)
            sy = int(ty * zoom + pan_y)
            if -50 < sx < screen_w + 50 and -50 < sy < screen_h + 50:
                tr = int(TREE_2_RADIUS * zoom)
                pygame.draw.circle(screen, C_TREE_2_MAIN, (sx, sy), tr)
                pygame.draw.circle(screen, C_TREE_2_LIGHT, (sx, sy - int(3*zoom)), int(tr * 0.5))