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
        
        # --- C'EST ICI QUE TU VAS TRAVAILLER ---
        self.house_slots = [] 
        
        self.supermarket = None
        self.medical_center = None
        self.sports_complex = None
        
        # 2. Générations
        self._generate_roads()
        self._generate_city_architecture()
        self._generate_fixed_supermarket()
        self._generate_medical_center()
        self._generate_sports_complex()
        
        # 3. Chargement de tes positions manuelles
        self._define_house_slots()

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

    # ==========================================
    # ZONE DE TRAVAIL MANUEL
    # ==========================================
    def _define_house_slots(self):
        """
        Définit les positions exactes des 250 maisons.
        Format : (x, y)
        """
        self.house_slots = [
            # Colle ta liste ici !
            (100, 100),
            (130, 100),
            (160, 100),
            
            # ... continue ici ...
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
        door_w, door_h = HOUSE_SIZE // 3, HOUSE_SIZE // 2.5
        door_rect = pygame.Rect(hx + (HOUSE_SIZE-door_w)//2, hy + HOUSE_SIZE - door_h, door_w, door_h)

        if style == 1: 
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_BEIGE, "data": body})
            house_parts.append({"shape": "poly", "color": C_RED, "data": [(x, hy - HOUSE_SIZE//1.5), (hx, hy), (hx + HOUSE_SIZE, hy)]})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})
        elif style == 2: 
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_GREY, "data": body})
            house_parts.append({"shape": "rect", "color": C_DARK, "data": pygame.Rect(hx - 1, hy - 3, HOUSE_SIZE + 2, 3)})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})
        elif style == 3: 
            body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
            house_parts.append({"shape": "rect", "color": C_BRICK, "data": body})
            house_parts.append({"shape": "poly", "color": C_DARK, "data": [(x, hy - HOUSE_SIZE), (hx - 1, hy), (hx + HOUSE_SIZE + 1, hy)]})
            house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})
        
        self.houses.append(house_parts)

    # --- BATIMENTS SPECIAUX ---
    def _generate_fixed_supermarket(self):
        sm_w, sm_h = SM_SIZE
        sx, sy = (self.width - sm_w) // 2, self.height - sm_h - 40 
        sm_rect = pygame.Rect(sx, sy, sm_w, sm_h)
        details = []
        # Sol Damier
        tile_size = 10
        for x in range(sx, sx + sm_w, tile_size):
            for y in range(sy, sy + sm_h, tile_size):
                col = C_SM_FLOOR if ((x - sx)//10 + (y - sy)//10) % 2 == 0 else C_SM_FLOOR_ALT
                w = min(tile_size, sx + sm_w - x)
                h = min(tile_size, sy + sm_h - y)
                details.append({"shape": "rect", "color": col, "data": pygame.Rect(x, y, w, h)})
        # Murs
        for r in [pygame.Rect(sx, sy, sm_w, 4), pygame.Rect(sx, sy + sm_h - 4, sm_w, 4), pygame.Rect(sx, sy, 4, sm_h), pygame.Rect(sx + sm_w - 4, sy, 4, sm_h)]:
            details.append({"shape": "rect", "color": C_SM_WALL, "data": r})
        # Rayons & Caisses
        current_x = sx + 15
        while current_x < sx + sm_w - 20:
            details.append({"shape": "rect", "color": C_SM_SHELF, "data": pygame.Rect(current_x, sy + 15, 12, sm_h - 50)})
            for py in range(sy + 17, sy + sm_h - 35, 4):
                 details.append({"shape": "rect", "color": (random.randint(100,255),random.randint(100,255),random.randint(100,255)), "data": pygame.Rect(current_x + 2, py, 8, 2)})
            current_x += 30
        for i in range(3):
            cx = sx + 30 + (i * 30)
            if cx + 20 < sx + sm_w:
                details.append({"shape": "rect", "color": C_SM_DESK, "data": pygame.Rect(cx, sy + sm_h - 25, 20, 10)})
                details.append({"shape": "rect", "color": C_SM_CHECKOUT, "data": pygame.Rect(cx + 2, sy + sm_h - 23, 16, 6)})
        # Entrée
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(sx + sm_w - 50, sy + sm_h - 4, 18, 4)})
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(sx + sm_w - 22, sy + sm_h - 4, 18, 4)})
        self.supermarket = {"rect": sm_rect, "details": details}

    def _generate_medical_center(self):
        mc_w, mc_h = MC_SIZE
        mx, my = 50, 50
        mc_rect = pygame.Rect(mx, my, mc_w, mc_h)
        details = []
        for x in range(mx, mx + mc_w, 10):
            for y in range(my, my + mc_h, 10):
                col = C_MC_FLOOR if ((x - mx)//10 + (y - my)//10) % 2 == 0 else C_MC_FLOOR_ALT
                w = min(10, mx + mc_w - x)
                h = min(10, my + mc_h - y)
                details.append({"shape": "rect", "color": col, "data": pygame.Rect(x, y, w, h)})
        cx, cy = mx + mc_w // 2, my + mc_h // 2
        details.append({"shape": "rect", "color": C_MC_CROSS, "data": pygame.Rect(cx - 4, cy - 12, 8, 24)})
        details.append({"shape": "rect", "color": C_MC_CROSS, "data": pygame.Rect(cx - 12, cy - 4, 24, 8)})
        for i in range(3):
            details.append({"shape": "rect", "color": C_MC_BED, "data": pygame.Rect(mx + 6, my + 10 + i*18, 20, 12)})
            details.append({"shape": "rect", "color": WHITE, "data": pygame.Rect(mx + 6, my + 11 + i*18, 4, 10)})
        for i in range(4):
            details.append({"shape": "rect", "color": C_MC_FURNITURE, "data": pygame.Rect(mx + mc_w - 15, my + 10 + i*12, 8, 8)})
        for r in [pygame.Rect(mx, my, mc_w, 3), pygame.Rect(mx, my + mc_h - 3, mc_w, 3), pygame.Rect(mx, my, 3, mc_h), pygame.Rect(mx + mc_w - 3, my, 3, mc_h)]:
            details.append({"shape": "rect", "color": C_MC_WALL, "data": r})
        details.append({"shape": "rect", "color": (150, 200, 255), "data": pygame.Rect(mx + mc_w - 30, my + mc_h - 3, 20, 3)})
        self.medical_center = {"rect": mc_rect, "details": details}

    def _generate_sports_complex(self):
        sc_w, sc_h = SC_SIZE
        sx, sy = self.width - sc_w - 50, 50
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

    def draw(self, screen, zoom, pan_x, pan_y, label_font):
        def to_screen_rect(rect):
            return pygame.Rect(int(rect.x * zoom + pan_x), int(rect.y * zoom + pan_y), int(rect.width * zoom), int(rect.height * zoom))

        for road in self.roads:
            pygame.draw.rect(screen, ROAD_COLOR, to_screen_rect(road))
        
        # 3. Maisons
        for house in self.houses:
            for part in house:
                if part["shape"] == "rect": pygame.draw.rect(screen, part["color"], to_screen_rect(part["data"]))
                elif part["shape"] == "poly": 
                    pts = [(int(pt[0]*zoom+pan_x), int(pt[1]*zoom+pan_y)) for pt in part["data"]]
                    pygame.draw.polygon(screen, part["color"], pts)
        
        # Batiments speciaux
        for building, name in [(self.supermarket, "SUPERMARCHÉ"), (self.medical_center, "CENTRE MÉDICAL"), (self.sports_complex, "COMPLEXE SPORTIF")]:
            if building:
                for part in building["details"]:
                    if part["shape"] == "rect": pygame.draw.rect(screen, part["color"], to_screen_rect(part["data"]))
                    elif part["shape"] == "circle":
                        c, r = part["data"]
                        pygame.draw.circle(screen, part["color"], (int(c[0]*zoom+pan_x), int(c[1]*zoom+pan_y)), int(r*zoom))
                txt = label_font.render(name, True, WHITE)
                screen.blit(txt, ((building["rect"].centerx*zoom+pan_x) - txt.get_width()//2, (building["rect"].top*zoom+pan_y) - 20))

        # Ville
        pygame.draw.rect(screen, (30, 30, 40), to_screen_rect(self.city_rect)) 
        for elem in self.city_elements:
            if elem["type"] == "building":
                for win in elem["details"]["windows"]: pygame.draw.rect(screen, win["color"], to_screen_rect(win["rect"]))
                r = to_screen_rect(elem["rect"])
                pygame.draw.line(screen, (80, 80, 90), (r.left, r.top), (r.right, r.top), int(3 * zoom))
                pygame.draw.rect(screen, elem["color"], r, 1)
            else:
                 pygame.draw.rect(screen, elem["color"], to_screen_rect(elem["rect"]))
            if elem["type"] == "park":
                for path in elem["details"]["paths"]:
                     pygame.draw.line(screen, (210, 200, 160), (int(path[0][0]*zoom+pan_x), int(path[0][1]*zoom+pan_y)), (int(path[1][0]*zoom+pan_x), int(path[1][1]*zoom+pan_y)), int(8*zoom))
                pygame.draw.ellipse(screen, (50, 150, 220), to_screen_rect(elem["details"]["pond"]))
                for t in elem["details"]["trees"]:
                    pygame.draw.circle(screen, (30, 80, 40), (int(t[0]*zoom+pan_x)+1, int(t[1]*zoom+pan_y)+2), int(5*zoom))
                    pygame.draw.circle(screen, (40, 100, 50), (int(t[0]*zoom+pan_x), int(t[1]*zoom+pan_y)), int(5*zoom))
            elif elem["type"] == "plaza":
                for tile in elem["details"]["tiles"]: pygame.draw.rect(screen, (180, 170, 160), to_screen_rect(tile))
                c = elem["details"]["fountain_center"]
                cx, cy = int(c[0]*zoom+pan_x), int(c[1]*zoom+pan_y)
                pygame.draw.circle(screen, (100, 100, 100), (cx, cy), int(12*zoom))
                pygame.draw.circle(screen, (50, 150, 220), (cx, cy), int(10*zoom))

        pygame.draw.rect(screen, ORANGE, to_screen_rect(self.city_rect), max(1, int(2 * zoom)))