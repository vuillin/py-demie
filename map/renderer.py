import pygame
from settings import *

def nuance(col, v):
    return (max(0, min(255, col[0] + v)), max(0, min(255, col[1] + v)), max(0, min(255, col[2] + v)))

def to_screen_rect(rect, zoom, pan_x, pan_y, screen_bounds):
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

def draw_map(game_map, screen, zoom, pan_x, pan_y, label_font):
    # --- 1. OPTIMISATION : GESTION CAMÉRA ---
    # On récupère la taille de l'écran pour savoir si on est dedans
    screen_w, screen_h = screen.get_size()
    screen_bounds = pygame.Rect(0, 0, screen_w, screen_h)

    # Helper local binding for cleaner code
    def _tsr(r):
        return to_screen_rect(r, zoom, pan_x, pan_y, screen_bounds)

    # --- 2. DESSIN DU SOL (HERBE) ---
    # On remplit d'abord avec la couleur de base
    screen.fill(C_GRASS_1) 
    
    # On dessine les tuiles texturées
    for tile in game_map.grass_tiles:
        r = _tsr(tile["rect"])
        if r: 
            pygame.draw.rect(screen, tile["color"], r)

    # --- 3. ROUTES ---
    _draw_roads(game_map, screen, zoom, pan_x, pan_y, screen_bounds)

    
    # --- 4. VÉGÉTATION BASSE (FLEURS & BUISSONS) ---
    # Parterres de fleurs
    w_flow, h_flow = FLOWERBED_SIZE
    for (fx, fy) in game_map.manual_flowers:
        # On vérifie si c'est dans l'écran
        r = _tsr(pygame.Rect(fx - w_flow//2, fy - h_flow//2, w_flow, h_flow))
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
    for (bx, by) in game_map.manual_bushes:
        sx = int(bx * zoom + pan_x)
        sy = int(by * zoom + pan_y)
        # Vérif écran rapide
        if -50 < sx < screen_w + 50 and -50 < sy < screen_h + 50:
            br = int(BUSH_RADIUS * zoom)
            pygame.draw.circle(screen, C_BUSH_MAIN, (sx, sy), br)
            pygame.draw.circle(screen, C_BUSH_LIGHT, (sx - int(1*zoom), sy - int(1*zoom)), int(br*0.6))

    # --- 5. MAISONS ---
    for house in game_map.houses:
        for part in house:
            if part["shape"] == "rect":
                r = _tsr(part["data"])
                if r: pygame.draw.rect(screen, part["color"], r)
            elif part["shape"] == "poly": 
                # Note : avec les toits plats, on n'utilise plus trop poly, mais on garde au cas où
                pts = [(int(pt[0]*zoom+pan_x), int(pt[1]*zoom+pan_y)) for pt in part["data"]]
                # Vérif sommaire si un point est dans l'écran
                if any(0 <= p[0] <= screen_w and 0 <= p[1] <= screen_h for p in pts):
                    pygame.draw.polygon(screen, part["color"], pts)
    
    # --- 6. BÂTIMENTS SPÉCIAUX ---
    for building, name in [(game_map.supermarket, "SUPERMARCHÉ"), (game_map.medical_center, "CENTRE MÉDICAL"), (game_map.sports_complex, "COMPLEXE SPORTIF")]:
        if building:
            # On vérifie si le bâtiment est visible globalement
            b_rect = _tsr(building["rect"])
            if b_rect: # Si le rectangle principal est visible
                for part in building["details"]:
                    if part["shape"] == "rect": 
                        pr = _tsr(part["data"])
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
    city_r = _tsr(game_map.city_rect)
    if city_r:
        # 1. FOND CHANGÉ ICI (C_CITY_GROUND au lieu de (30, 30, 40))
        pygame.draw.rect(screen, C_CITY_GROUND, city_r) 
        
        for elem in game_map.city_elements:
            r = _tsr(elem["rect"])
            if r: # Si l'élément de ville est visible
                if elem["type"] == "building":
                    # D'abord on remplit le bâtiment (sinon il est transparent)
                    pygame.draw.rect(screen, elem["color"], r)
                    
                    for win in elem["details"]["windows"]: 
                        wr = _tsr(win["rect"])
                        if wr: pygame.draw.rect(screen, win["color"], wr)
                    
                    pygame.draw.line(screen, (140, 140, 150), (r.left, r.top), (r.right, r.top), int(3 * zoom))
                    # Contour léger du batiment
                    pygame.draw.rect(screen, (100, 100, 100), r, 1)
                else:
                        pygame.draw.rect(screen, elem["color"], r)
                
                # Détails Parc (Ton code d'origine inchangé)
                if elem["type"] == "park":
                    for path in elem["details"]["paths"]:
                            p1 = (int(path[0][0]*zoom+pan_x), int(path[0][1]*zoom+pan_y))
                            p2 = (int(path[1][0]*zoom+pan_x), int(path[1][1]*zoom+pan_y))
                            pygame.draw.line(screen, (210, 200, 160), p1, p2, int(8*zoom))
                    pr = _tsr(elem["details"]["pond"])
                    if pr: pygame.draw.ellipse(screen, (50, 150, 220), pr)
                    for t in elem["details"]["trees"]:
                        tx, ty = int(t[0]*zoom+pan_x), int(t[1]*zoom+pan_y)
                        tr = int(5*zoom)
                        pygame.draw.circle(screen, (30, 80, 40), (tx+1, ty+2), tr)
                        pygame.draw.circle(screen, (40, 100, 50), (tx, ty), tr)
                # Détails Plaza (Ton code d'origine inchangé)
                elif elem["type"] == "plaza":
                    for tile in elem["details"]["tiles"]: 
                        tr = _tsr(tile)
                        if tr: pygame.draw.rect(screen, (180, 170, 160), tr)
                    c = elem["details"]["fountain_center"]
                    cx, cy = int(c[0]*zoom+pan_x), int(c[1]*zoom+pan_y)
                    pygame.draw.circle(screen, (100, 100, 100), (cx, cy), int(12*zoom))
                    pygame.draw.circle(screen, (50, 150, 220), (cx, cy), int(10*zoom))

        # 2. BORDURE CHANGÉE ICI (C_CITY_BORDER au lieu de ORANGE)
        pygame.draw.rect(screen, C_CITY_BORDER, city_r, max(2, int(4 * zoom)))

    # --- 8. VÉGÉTATION HAUTE (ARBRES) ---
    # Arbres Type 1 (Verts)
    for (tx, ty) in game_map.manual_trees_1:
        sx = int(tx * zoom + pan_x)
        sy = int(ty * zoom + pan_y)
        
        # Vérif écran
        if -50 < sx < screen_w + 50 and -50 < sy < screen_h + 50:
            tr = int(TREE_1_RADIUS * zoom)
            
            # ASTUCE : Variation de couleur basée sur la position (stable, ne clignote pas)
            # On génère un nombre entre -15 et +15 qui dépend de x et y
            var = ((tx * 7 + ty * 13) % 30) - 15
            
            # On applique cette nuance aux couleurs de base
            col_b = nuance(C_TREE_1_BASE, var)
            col_t = nuance(C_TREE_1_TOP, var)

            # 1. Base (Ombre) décalée
            pygame.draw.circle(screen, col_b, (sx + int(1*zoom), sy + int(2*zoom)), tr)
            
            # 2. Haut (Feuillage) centré
            pygame.draw.circle(screen, col_t, (sx, sy), tr)
        
    # Arbres Type 2 (Sombres)
    for (tx, ty) in game_map.manual_trees_2:
        sx = int(tx * zoom + pan_x)
        sy = int(ty * zoom + pan_y)
        
        if -50 < sx < screen_w + 50 and -50 < sy < screen_h + 50:
            tr = int(TREE_2_RADIUS * zoom)
            
            # Astuce mathématique pour la nuance (sans clignotement)
            var = ((tx * 5 + ty * 11) % 30) - 15
            
            # On utilise les couleurs définies pour le Type 2 (TOP et BASE)
            col_b = nuance(C_TREE_2_BASE, var)
            col_t = nuance(C_TREE_2_TOP, var)

            # 1. Base (Ombre) décalée
            pygame.draw.circle(screen, col_b, (sx + int(1*zoom), sy + int(2*zoom)), tr)
            
            # 2. Haut (Feuillage) centré
            pygame.draw.circle(screen, col_t, (sx, sy), tr)


def _draw_roads(game_map, screen, zoom, pan_x, pan_y, screen_bounds):
    
    # Largeurs ajustées au zoom
    w_total = int(ROAD_WIDTH * zoom)
    w_inner = int((ROAD_WIDTH - 2 * SIDEWALK_WIDTH) * zoom)
    
    # Si trop petit, on ne dessine pas les détails
    if w_total < 2: return

    # Pré-calcul des chemins visibles pour éviter de refaire la boucle
    visible_paths = []
    for path in game_map.roads:
        screen_points = []
        visible = False
        for p in path:
            sx = int(p[0] * zoom + pan_x)
            sy = int(p[1] * zoom + pan_y)
            screen_points.append((sx, sy))
        
        # Check rapid de visibilité (bounding box du path)
        if not screen_points: continue
        min_x = min(p[0] for p in screen_points)
        max_x = max(p[0] for p in screen_points)
        min_y = min(p[1] for p in screen_points)
        max_y = max(p[1] for p in screen_points)
        
        if (max_x >= 0 and min_x <= screen.get_width() and
            max_y >= 0 and min_y <= screen.get_height()):
             if len(screen_points) >= 2:
                visible_paths.append(screen_points)

    def draw_layer(color, width):
        half_w = width // 2
        
        for pts in visible_paths:
            # 1. Dessiner les segments
            for i in range(len(pts) - 1):
                p1 = pts[i]
                p2 = pts[i+1]
                
                # On détermine le rectangle du segment
                # Si orthogonal (horizontal ou vertical), on utilise un Rect parfait
                # ce qui évite les artefacts des "fat lines"
                
                if p1[0] == p2[0]: # Vertical
                    top = min(p1[1], p2[1])
                    height = abs(p1[1] - p2[1])
                    # Le rect est centré en X sur p1[0]
                    rect = pygame.Rect(p1[0] - half_w, top, width, height)
                    pygame.draw.rect(screen, color, rect)
                    
                elif p1[1] == p2[1]: # Horizontal
                    left = min(p1[0], p2[0])
                    length = abs(p1[0] - p2[0])
                    # Le rect est centré en Y sur p1[1]
                    rect = pygame.Rect(left, p1[1] - half_w, length, width)
                    pygame.draw.rect(screen, color, rect)
                    
                else: # Diagonale (Fallback sur draw.line si jamais)
                    pygame.draw.line(screen, color, p1, p2, width)

            # 2. Dessiner les joints (Carrés)
            for sp in pts:
                # On centre manuellement le rect pour être cohérent avec le segment
                # Rect(left, top, w, h)
                r_joint = pygame.Rect(sp[0] - half_w, sp[1] - half_w, width, width)
                pygame.draw.rect(screen, color, r_joint)

    # 1. DESSINER TOUS LES TROTTOIRS (LAYER 0)
    draw_layer(C_SIDEWALK, w_total)

    # 2. DESSINER TOUTES LES ROUTES (LAYER 1)
    draw_layer(ROAD_COLOR, w_inner)
