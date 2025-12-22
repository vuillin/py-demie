import pygame
import random
from settings import *

def generate_grass(width, height):
    """Génère un sol en damier uniforme et doux"""
    grass_tiles = []
    
    # Taille fixe pour tous les carrés (60px est un bon équilibre)
    tile_size = 20
    
    # On calcule combien de carrés il faut pour remplir la largeur et hauteur
    # On ajoute +1 pour être sûr de couvrir les bords si la division n'est pas ronde
    cols = (width // tile_size) + 1
    rows = (height // tile_size) + 1

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
            grass_tiles.append({"rect": rect, "color": color})
    return grass_tiles

def generate_city_architecture(city_rect, city_w, city_h):
    city_elements = []
    
    # On définit la grille : 5 colonnes (largeur) x 4 lignes (hauteur)
    cols_count = 5
    rows_count = 4
    
    # Taille d'un bloc (60px)
    block_w = city_w // cols_count
    block_h = city_h // rows_count
    padding = 5

    for row in range(rows_count):
        for col in range(cols_count):
            bx = city_rect.x + (col * block_w)
            by = city_rect.y + (row * block_h)
            
            # Le rectangle de base du bloc
            rect = pygame.Rect(bx + padding, by + padding, block_w - 2*padding, block_h - 2*padding)
            
            # --- LOGIQUE DE ZONAGE (Décalée vers la droite pour laisser la col 0 en immeubles) ---
            
            # PARC (En haut à droite) -> Était cols 2,3 -> Devient cols 3,4
            if row in [0, 1] and col in [3, 4]: 
                # On ne crée le parc qu'une seule fois, au début du bloc "maître" (row 0, col 3)
                if row == 0 and col == 3:
                    # Le parc prend 2x2 blocs
                    park_rect = pygame.Rect(bx + padding, by + padding, (block_w*2) - 2*padding, (block_h*2) - 2*padding)
                    
                    park_details = {"trees": [], "pond": None, "paths": []}
                    pond_w, pond_h = park_rect.width // 2.5, park_rect.height // 3
                    park_details["pond"] = pygame.Rect(park_rect.x + park_rect.width*0.6, park_rect.y + park_rect.height*0.15, pond_w, pond_h)
                    
                    # Chemins en croix
                    park_details["paths"].append([(park_rect.left, park_rect.top), (park_rect.right, park_rect.bottom)])
                    park_details["paths"].append([(park_rect.right, park_rect.top), (park_rect.left, park_rect.bottom)])
                    
                    # Arbres du parc
                    for _ in range(40):
                        tx, ty = random.randint(park_rect.left + 5, park_rect.right - 5), random.randint(park_rect.top + 5, park_rect.bottom - 5)
                        if not park_details["pond"].collidepoint(tx, ty): 
                            park_details["trees"].append((tx, ty))
                    
                    city_elements.append({"type": "park", "rect": park_rect, "color": (60, 160, 70), "details": park_details})
                
                # Si on est dans les autres cases du parc (0,4 ou 1,3 ou 1,4), on ne fait rien (le gros rect couvre tout)
                continue 

            # PLAZA (En bas, un peu à gauche mais pas tout au bord) -> Était cols 0,1 -> Devient cols 1,2
            elif row in [2, 3] and col in [1, 2]: 
                if row == 2 and col == 1:
                    plaza_margin = 20
                    plaza_rect = pygame.Rect(bx + plaza_margin, by + plaza_margin, (block_w*2) - 2*plaza_margin, (block_h*2) - 2*plaza_margin)
                    plaza_details = {"tiles": [], "fountain_center": plaza_rect.center}
                    
                    # Dallage
                    for tx in range(plaza_rect.left, plaza_rect.right, 10):
                        for ty in range(plaza_rect.top, plaza_rect.bottom, 10):
                            if (tx + ty) % 20 == 0: 
                                plaza_details["tiles"].append(pygame.Rect(tx, ty, 9, 9))
                    
                    city_elements.append({"type": "plaza", "rect": plaza_rect, "color": (200, 190, 180), "details": plaza_details})
                continue

            # TOUT LE RESTE (Y compris la nouvelle colonne 0) -> IMMEUBLES
            else: 
                v = random.randint(-20, 20)
                color = (
                    max(0, min(255, C_BUILDING_BASE[0] + v)),
                    max(0, min(255, C_BUILDING_BASE[1] + v)),
                    max(0, min(255, C_BUILDING_BASE[2] + v + 10)) # Un peu bleuté
                )

                windows = []
                # Génération des fenêtres (Inchangé)
                for wx in range(rect.left + 4, rect.right - 4, 10):
                    for wy in range(rect.top + 4, rect.bottom - 4, 10):
                        if random.random() < 0.8:
                            win_color = (40, 40, 50) # Fenêtres sombres pour contraster
                            if random.random() < 0.3: win_color = (255, 255, 200) # Lumière
                            windows.append({"rect": pygame.Rect(wx, wy, 6, 6), "color": win_color})
                
                city_elements.append({"type": "building", "rect": rect, "color": color, "details": {"windows": windows}})
    
    return city_elements

def generate_fixed_supermarket(width, height):
    sm_w, sm_h = SM_SIZE
    sx, sy = (width - sm_w) // 2, height - sm_h - 40 
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
    
    return {"rect": sm_rect, "details": details}

def generate_medical_center():
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

    return {"rect": mc_rect, "details": details}

def generate_sports_complex(width):
    sc_w, sc_h = SC_SIZE
    sx, sy = width - sc_w - 150, 50
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
    
    return {"rect": sc_rect, "details": details}

def create_house_parts(x, y):
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
        house_parts.append({"shape": "rect", "color": C_RED, "data": roof_rect})
        house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

    elif style == 2: # Style Moderne Gris (Toit plat Foncé)
        body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
        house_parts.append({"shape": "rect", "color": C_GREY, "data": body})
        house_parts.append({"shape": "rect", "color": C_DARK, "data": roof_rect})
        house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})

    elif style == 3: # Style Brique (Toit plat Foncé)
        body = pygame.Rect(hx, hy, HOUSE_SIZE, HOUSE_SIZE)
        house_parts.append({"shape": "rect", "color": C_BRICK, "data": body})
        house_parts.append({"shape": "rect", "color": C_DARK, "data": roof_rect})
        house_parts.append({"shape": "rect", "color": C_WOOD, "data": door_rect})
    
    return house_parts
