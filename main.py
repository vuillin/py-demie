import pygame
import random
from settings import *
from person import Person
from person import Person
from map import Map
from navigation import NavigationGraph
import jobs


# Initialisation
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size() # On récupère la taille réelle de l'écran
pygame.display.set_caption("Py-Démie")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI", 20)
font_title = pygame.font.SysFont("Segoe UI", 30, bold=True)
font_btn = pygame.font.SysFont("Segoe UI", 20, bold=True)
font_label = pygame.font.SysFont("Arial", 15, bold=True)
font_value = pygame.font.SysFont("Consolas", 28, bold=True)

# --- THEME HUD ---
SidebarColor     = (30, 32, 36)
PanelColor       = (45, 48, 55)
AccentColor      = (255, 190, 0) # Gold
TextColor        = (220, 220, 220)
BtnColor         = (60, 65, 75)
BtnHoverColor    = (80, 85, 95)
BtnActiveColor   = (100, 180, 100) # Greenish for active speed

# --- SETUP ---
# 1. Génération de la Carte
game_map = Map(WORLD_WIDTH, WORLD_HEIGHT, POPULATION_SIZE)

# GPS (graphe)
nav = NavigationGraph()

# 2. Création de la Population
population = []
for _ in range(POPULATION_SIZE):
    # On récupère un point aléatoire valide (hors ville, hors supermarché)
    x, y = game_map.get_valid_spawn_point()
    
    # On crée la personne
    # On passe le rectangle du supermarché (dispo depuis jobs.py ou on le récupère de game_map)
    # game_map.supermarket n'est pas encore garanti d'avoir "rect" ici ? Si, Map le crée dans son init.
    # On crée la personne
    # On passe le rectangle du supermarché ET du complexe sportif
    population.append(Person(x, y, game_map.city_rect, game_map.supermarket["rect"], game_map.sports_complex["rect"], nav))
    
    # On ajoute sa maison visuelle à cet endroit
    game_map.add_house(x, y)

# 3. Métiers (Supermarché)
checkouts = [
    (529, 740),
    (563, 740),
    (599, 740),
    (634, 740),
    (669, 740),
]
sm_manager = jobs.SupermarketManager(checkouts)

# On prend 3 personnes au hasard
workers = random.sample(population, 3)
for w in workers:
    w.job = jobs.SupermarketJob(sm_manager, game_map.supermarket["rect"])
    w.is_employed = True # Pour la stat

# 4. Métiers (Centre Médical)
# On prend 2 personnes qui NE SONT PAS déjà au supermarché
remaining_pop = [p for p in population if not p.is_employed]
if len(remaining_pop) >= 2:
    medics = random.sample(remaining_pop, 2)
    for m in medics:
        # On suppose que game_map.medical_center a une clé "rect" (comme supermarket)
        # Vérifions d'abord la structure dans core.py/generators.py si besoin, 
        # mais le code de renderer.py utilisait building["rect"] donc c'est bon.
        m.job = jobs.MedicalJob(game_map.medical_center["rect"])
        m.is_employed = True

# Variables de temps
current_hour = 6.0 
game_speed = 1.0 
current_day_index = 0 # 0 = Lundi
DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# Variables Caméra
zoom = min(WIDTH / WORLD_WIDTH, HEIGHT / WORLD_HEIGHT) # Auto-fit
min_zoom = 0.5
max_zoom = 4.0
zoom_speed = 0.1
pan_x, pan_y = 0, 0
is_panning = False
last_mouse_pos = (0, 0)

# State UI
sidebar_rect = pygame.Rect(0,0,0,0)
is_sidebar_visible = False
# Stats State
stats_open = False
stats_anim_cv = 0.0 # Current Value (0.0 -> 1.0)
target_stats_open = False

# Overlay Nuit
# On crée une surface qui couvre tout l'écran (ou au moins le max possible)
# On la remplit de bleu nuit/noir
day_night_overlay = pygame.Surface((WIDTH, HEIGHT))
day_night_overlay.fill((10, 15, 40)) 


def update_ui_layout():
    """Recalcule la position des éléments d'interface selon la taille d'écran"""
    global btn_slow, btn_fast, btn_stats, btn_close_stats, sidebar_rect, is_sidebar_visible
    
    # 1. Calcul Sidebar
    map_render_width = WORLD_WIDTH * zoom
    if WIDTH > map_render_width:
        sidebar_x = int(map_render_width)
        sidebar_w = WIDTH - sidebar_x
        sidebar_rect = pygame.Rect(sidebar_x, 0, sidebar_w, HEIGHT)
        is_sidebar_visible = True
    else:
        # Fallback si pas de place (ou très zoomé), on garde une mini barre ou on superpose ?
        # Pour l'instant on garde l'ancien système si pas de place, ou on affiche rien.
        # User a demandé "à droite du jeu, il y a tout un espace vide".
        # On va supposer qu'il y a toujours la sidebar si le zoom auto-fit le permet.
        sidebar_rect = pygame.Rect(WIDTH, 0, 0, HEIGHT)
        is_sidebar_visible = False

    if is_sidebar_visible:
        # Centre de la sidebar
        cx = sidebar_rect.centerx
        top = 100
        
        # Position des boutons DANS la sidebar
        btn_w, btn_h = 40, 40
        spacing = 10
        total_w = (btn_w * 2) + spacing
        start_x = cx - (total_w // 2)
        
        # Boutons Vitesse ( Sous l'heure )
        btn_slow = pygame.Rect(start_x, top + 150, btn_w, btn_h)
        btn_fast = pygame.Rect(start_x + btn_w + spacing, top + 150, btn_w, btn_h)

        # Bouton STATS (Plus bas)
        btn_stats = pygame.Rect(cx - 50, top + 220, 100, 30)
        
        # Bouton Fermer Stats (Il sera dans la sidebar stats, mais on peut le définir ici pour clic)
        # On suppose que la sidebar stats fait 300px de large
        stats_w = 300
        btn_close_stats = pygame.Rect(WIDTH - stats_w + 10, 10, 30, 30)

    else:
        # Fallback (Ancien layout flottant en haut à droite)
        margin = 10
        btn_w, btn_h = 40, 30
        btn_slow = pygame.Rect(WIDTH - (btn_w * 2) - (margin * 2), margin, btn_w, btn_h)
        btn_fast = pygame.Rect(WIDTH - btn_w - margin, margin, btn_w, btn_h)
        # Dummy stats btn for fallback to avoid crash
        btn_stats = pygame.Rect(-100, -100, 10, 10)
        btn_close_stats = pygame.Rect(-100, -100, 10, 10)


# Initial call to setup UI
def update_overlay_dims():
    global day_night_overlay
    if day_night_overlay.get_size() != (WIDTH, HEIGHT):
        day_night_overlay = pygame.Surface((WIDTH, HEIGHT))
        day_night_overlay.fill((10, 15, 40))

update_ui_layout()
update_overlay_dims()

# --- BOUCLE DE JEU ---
running = True
while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Touche ECHAP pour quitter le plein écran/jeu
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
        # Zoom (Molette)
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = (mouse_x - pan_x) / zoom
            world_y = (mouse_y - pan_y) / zoom
            
            zoom += event.y * zoom_speed
            zoom = max(min_zoom, min(max_zoom, zoom))
            
            pan_x = mouse_x - (world_x * zoom)
            pan_y = mouse_y - (world_y * zoom)

        # Clics (Boutons ou Pan)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                # --- AJOUT TEMPORAIRE ---
                # Affiche les coordonnées "monde" (en tenant compte du pan et du zoom)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = int((mouse_x - pan_x) / zoom)
                world_y = int((mouse_y - pan_y) / zoom)
                print(f"({world_x}, {world_y}),") # Affiche formaté prêt à copier
                # ------------------------

                mouse_pos = pygame.mouse.get_pos()
                if btn_slow.collidepoint(mouse_pos):
                    game_speed = max(0.5, game_speed - 0.5)
                elif btn_fast.collidepoint(mouse_pos):
                    game_speed = min(10.0, game_speed + 0.5)
                elif is_sidebar_visible and btn_stats.collidepoint(mouse_pos):
                    target_stats_open = True
                elif target_stats_open and stats_anim_cv > 0.5:
                    if btn_close_stats.collidepoint(mouse_pos):
                        target_stats_open = False

                else:
                    is_panning = True
                    last_mouse_pos = mouse_pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_panning = False
                
        elif event.type == pygame.MOUSEMOTION:
            if is_panning:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pan_x += mouse_x - last_mouse_pos[0]
                pan_y += mouse_y - last_mouse_pos[1]
                last_mouse_pos = (mouse_x, mouse_y)

    # Clamping Caméra
    map_w_zoomed = WORLD_WIDTH * zoom
    map_h_zoomed = WORLD_HEIGHT * zoom
    pan_x = min(0, max(pan_x, WIDTH - map_w_zoomed))
    pan_y = min(0, max(pan_y, HEIGHT - map_h_zoomed))

    # 2. Update
    # Mise à jour heure
    current_hour += BASE_CLOCK_SPEED * game_speed
    if current_hour >= 24:
        current_hour = 0
        current_day_index = (current_day_index + 1) % 7

    # Mise à jour population
    for person in population:
        person.update(current_hour, game_speed, current_day_index)

    # 3. Draw
    screen.fill(BG_COLOR)

    # A. Monde
    game_map.draw(screen, zoom, pan_x, pan_y, font_label) # On passe la font pour le supermarché
    for person in population:
        person.draw(screen, zoom, pan_x, pan_y)


    # --- CYCLE JOUR / NUIT (VISUEL) ---
    # Calcul de l'alpha (transparence) en fonction de l'heure
    # 8h - 18h : Jour (Alpha 0)
    # 18h - 21h : Crépuscule (0 -> 150)
    # 21h - 5h : Nuit (150)
    # 5h - 8h : Aube (150 -> 0)
    
    alpha = 0
    if 18 <= current_hour < 21:
        # Transition soir
        progress = (current_hour - 18) / 3 # 0.0 à 1.0
        alpha = int(progress * 150)
    elif 21 <= current_hour or current_hour < 5:
        # Nuit pleine
        alpha = 150
    elif 5 <= current_hour < 8:
        # Transition matin
        progress = (current_hour - 5) / 3 # 0.0 à 1.0
        alpha = int(150 - (progress * 150))
    else:
        alpha = 0
    
    if alpha > 0:
        day_night_overlay.set_alpha(alpha)
        screen.blit(day_night_overlay, (0, 0))


    # --- ANIMATION STATS SIDEBAR ---
    anim_speed = 0.1
    if target_stats_open:
        stats_anim_cv += anim_speed
        if stats_anim_cv > 1.0: stats_anim_cv = 1.0
    else:
        stats_anim_cv -= anim_speed
        if stats_anim_cv < 0.0: stats_anim_cv = 0.0



    # ==================================================
    # --- DEBUG : AFFICHER LE RÉSEAU (Graphe) ---
    # ==================================================
    if False: # Mets False ici pour cacher le graphe sans supprimer le code
        # 1. Dessiner les connexions (Lignes rouges)
        for start_id, end_id in nav.connections:
            # On récupère les positions réelles (x, y) des deux points
            p1 = nav.nodes[start_id]
            p2 = nav.nodes[end_id]
            
            # On applique le Zoom et le Pan (comme pour tout le reste)
            s1 = (int(p1[0] * zoom + pan_x), int(p1[1] * zoom + pan_y))
            s2 = (int(p2[0] * zoom + pan_x), int(p2[1] * zoom + pan_y))
            
            # On trace la ligne
            pygame.draw.line(screen, (255, 0, 0), s1, s2, 2) 

        # 2. Dessiner les noeuds (Points rouges)
        for node_id, pos in nav.nodes.items():
            sx = int(pos[0] * zoom + pan_x)
            sy = int(pos[1] * zoom + pan_y)
            pygame.draw.circle(screen, (255, 0, 0), (sx, sy), 5)
            
            # Afficher le nom du point
            lbl = font_label.render(node_id, True, (0, 0, 0))
            screen.blit(lbl, (sx, sy - 15))
    # ==================================================



    # --- RENDERING ATH ---
    
    if is_sidebar_visible:
        # 1. FOND
        pygame.draw.rect(screen, SidebarColor, sidebar_rect)
        pygame.draw.line(screen, (50, 50, 60), (sidebar_rect.left, 0), (sidebar_rect.left, HEIGHT), 2)
        
        cx = sidebar_rect.centerx
        
        # 2. TITRE
        title_surf = font_title.render("PY-DEMIE", True, AccentColor)
        screen.blit(title_surf, (cx - title_surf.get_width()//2, 30))
        
        # 3. PANNEAU DATE HEURE
        panel_rect = pygame.Rect(sidebar_rect.left + 20, 80, sidebar_rect.width - 40, 120)
        pygame.draw.rect(screen, PanelColor, panel_rect, border_radius=10)
        pygame.draw.rect(screen, (60, 60, 70), panel_rect, 2, border_radius=10)
        
        # Jour
        day_str = DAYS[current_day_index].upper()
        draw_day = font.render(day_str, True, TextColor)
        screen.blit(draw_day, (panel_rect.centerx - draw_day.get_width()//2, panel_rect.y + 15))
        
        # Heure
        hour_val = int(current_hour)
        hour_str = f"{hour_val:02d}:00"
        draw_hour = font_value.render(hour_str, True, WHITE)
        screen.blit(draw_hour, (panel_rect.centerx - draw_hour.get_width()//2, panel_rect.y + 45))
        
        # Vitesse LABEL
        spd_lbl = font_label.render(f"SPEED x{game_speed:.1f}", True, (150, 150, 150))
        screen.blit(spd_lbl, (panel_rect.centerx - spd_lbl.get_width()//2, panel_rect.y + 90))

        # BOUTONS VITESSE (Dessinés par dessus le panneau ou dessous)
        # On va les dessiner plus bas, hors du panneau, pour le style
        # Update layout a positionné btn_slow et btn_fast à top + 150 (donc panel.y + 70 + padding)
        # Ah wait, panel height is 120, starts at 80, ends at 200.
        # My clean layout calc in update_ui was: top=100, btns at top+150 -> 250. Good.
        
        # Bouton SLOW
        mouse_pos = pygame.mouse.get_pos()
        col_slow = BtnHoverColor if btn_slow.collidepoint(mouse_pos) else BtnColor
        pygame.draw.rect(screen, col_slow, btn_slow, border_radius=5)
        txt_s = font_btn.render("-", True, WHITE)
        screen.blit(txt_s, (btn_slow.centerx - txt_s.get_width()//2, btn_slow.centery - txt_s.get_height()//2))
        
        # Bouton FAST
        col_fast = BtnHoverColor if btn_fast.collidepoint(mouse_pos) else BtnColor
        pygame.draw.rect(screen, col_fast, btn_fast, border_radius=5)
        txt_f = font_btn.render("+", True, WHITE)
        screen.blit(txt_f, (btn_fast.centerx - txt_f.get_width()//2, btn_fast.centery - txt_f.get_height()//2))

        # Bouton STATS
        col_st = BtnHoverColor if btn_stats.collidepoint(mouse_pos) else BtnColor
        pygame.draw.rect(screen, col_st, btn_stats, border_radius=5)
        txt_st = font_label.render("STATS", True, WHITE)
        screen.blit(txt_st, (btn_stats.centerx - txt_st.get_width()//2, btn_stats.centery - txt_st.get_height()//2))

    else:
        # FALLBACK (Old UI)
        ui_bg = pygame.Surface((150, 60))
        ui_bg.set_alpha(150)
        ui_bg.fill((0, 0, 0))
        ui_bg.fill((0, 0, 0))
        screen.blit(ui_bg, (5, 5))

        day_text = font.render(f"Jour: {DAYS[current_day_index]}", True, WHITE)
        screen.blit(day_text, (10, 10))

        time_text = font.render(f"Heure: {int(current_hour)}h", True, WHITE)
        screen.blit(time_text, (10, 35))
        
        speed_text = font.render(f"Vitesse: x{game_speed:.1f}", True, (200, 200, 100))
        screen.blit(speed_text, (10, 60))

        pygame.draw.rect(screen, (70, 70, 80), btn_slow)
        pygame.draw.rect(screen, (200, 200, 200), btn_slow, 2)
        text_slow = font_btn.render("-", True, WHITE)
        screen.blit(text_slow, (btn_slow.centerx - text_slow.get_width()//2, btn_slow.centery - text_slow.get_height()//2))

        pygame.draw.rect(screen, (70, 70, 80), btn_fast)
        pygame.draw.rect(screen, (200, 200, 200), btn_fast, 2)
        text_fast = font_btn.render("+", True, WHITE)
        screen.blit(text_fast, (btn_fast.centerx - text_fast.get_width()//2, btn_fast.centery - text_fast.get_height()//2))
        



    
    # --- RENDERING STATS SIDEBAR (MOVED HERE) ---
    if stats_anim_cv > 0.01:
        # Width de 300px
        s_w = 300
        # Position X qui glisse (de WIDTH à WIDTH - 300)
        # Mais pour être "par dessus" la sidebar d'origine qui est à sidebar_rect.left
        # On peut dire qu'elle sort de la droite de l'écran par dessus tout
        final_x = WIDTH - s_w
        start_x = WIDTH
        curr_x = start_x - (start_x - final_x) * stats_anim_cv
        
        stats_rect = pygame.Rect(curr_x, 0, s_w, HEIGHT)
        
        # Fond + Ombre
        s = pygame.Surface((s_w, HEIGHT))
        s.fill((40, 42, 48))
        screen.blit(s, (curr_x, 0))
        pygame.draw.line(screen, (255, 190, 0), (curr_x, 0), (curr_x, HEIGHT), 2) # Ligne Gold
        
        # Mise à jour rect bouton close
        btn_close_stats.x = curr_x + 10
        btn_close_stats.y = 10
        
        # CLOSE BTN
        pygame.draw.rect(screen, (200, 60, 60), btn_close_stats, border_radius=5)
        txt_x = font_btn.render("X", True, WHITE)
        screen.blit(txt_x, (btn_close_stats.centerx - txt_x.get_width()//2, btn_close_stats.centery - txt_x.get_height()//2))

        # CONTENT
        # Titre
        title_s = font_title.render("STATISTIQUES", True, WHITE)
        screen.blit(title_s, (curr_x + s_w//2 - title_s.get_width()//2, 50))
        
        y_cursor = 100
        dx = curr_x + 20
        
        # Stats Values
        total_pop = len(population)
        nb_sportive = sum(1 for p in population if p.is_sportive)
        pct_sport = int(nb_sportive/total_pop*100) if total_pop > 0 else 0
        nb_workers = sum(1 for p in population if p.is_employed)
        shoppers = [p for p in population if p.shopping_day == current_day_index]
        nb_shoppers = len(shoppers)

        # DATA POUR CARDS
        stats_cards = [
            {"label": "POPULATION", "value": str(total_pop), "color": (100, 150, 240), "icon": "pop"},
            {"label": "SPORTIFS", "value": f"{nb_sportive} ({pct_sport}%)", "color": (240, 100, 100), "icon": "sport"},
            {"label": "TRAVAILLEURS", "value": str(nb_workers), "color": (240, 200, 80), "icon": "work"},
            {"label": "SHOPPING", "value": str(nb_shoppers), "color": (100, 220, 120), "icon": "shop"},
        ]

        card_h = 70
        card_w = s_w - 40
        gap = 15

        for i, card in enumerate(stats_cards):
            cy = y_cursor + (i * (card_h + gap))
            c_rect = pygame.Rect(dx, cy, card_w, card_h)
            
            # Fond Carte
            pygame.draw.rect(screen, (50, 52, 60), c_rect, border_radius=8)
            # Bordure colorée à gauche
            pygame.draw.rect(screen, card["color"], (dx, cy, 6, card_h), border_top_left_radius=8, border_bottom_left_radius=8)

            # Icone Area
            icon_center = (dx + 35, cy + card_h//2)
            
            # Dessin Icones Géométriques
            if card["icon"] == "pop":
                # Bonhomme
                pygame.draw.circle(screen, card["color"], (icon_center[0], icon_center[1]-8), 6)
                pygame.draw.polygon(screen, card["color"], [(icon_center[0], icon_center[1]+12), (icon_center[0]-8, icon_center[1]), (icon_center[0]+8, icon_center[1])]) # Corps triangle
                pygame.draw.polygon(screen, card["color"], [(icon_center[0], icon_center[1]-2), (icon_center[0]-8, icon_center[1]+10), (icon_center[0]+8, icon_center[1]+10)])

            elif card["icon"] == "sport":
                # Haltère
                c = card["color"]
                pygame.draw.line(screen, c, (icon_center[0]-10, icon_center[1]), (icon_center[0]+10, icon_center[1]), 4)
                pygame.draw.rect(screen, c, (icon_center[0]-12, icon_center[1]-5, 4, 10))
                pygame.draw.rect(screen, c, (icon_center[0]+8, icon_center[1]-5, 4, 10))

            elif card["icon"] == "work":
                # Valise
                c = card["color"]
                pygame.draw.rect(screen, c, (icon_center[0]-9, icon_center[1]-6, 18, 14))
                pygame.draw.arc(screen, c, (icon_center[0]-4, icon_center[1]-10, 8, 8), 0, 3.14, 2)

            elif card["icon"] == "shop":
                # Caddie / Panier
                c = card["color"]
                pygame.draw.polygon(screen, c, [(icon_center[0]-8, icon_center[1]-5), (icon_center[0]+8, icon_center[1]-5), (icon_center[0]+6, icon_center[1]+8), (icon_center[0]-6, icon_center[1]+8)])
                pygame.draw.arc(screen, c, (icon_center[0]-4, icon_center[1]-10, 8, 8), 0, 3.14, 2)

            # Textes (Centrage Vertical)
            lbl_s = font_label.render(card["label"], True, (180, 180, 190))
            val_s = font_title.render(card["value"], True, WHITE)
            
            total_text_h = lbl_s.get_height() + val_s.get_height()
            start_y = cy + (card_h - total_text_h) // 2
            
            screen.blit(lbl_s, (dx + 70, start_y)) # label
            screen.blit(val_s, (dx + 70, start_y + lbl_s.get_height() - 2)) # value (petit overlap de 2px pour resserrer)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()