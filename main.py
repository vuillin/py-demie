import pygame
import random
import math
from settings import *
from person import Person
from person import Person
from map import Map
from navigation import NavigationGraph
import jobs


# Initialisation
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size() 
pygame.display.set_caption("Py-Démie")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI", 20)
font_title = pygame.font.SysFont("Segoe UI", 30, bold=True)
font_btn = pygame.font.SysFont("Segoe UI", 20, bold=True)
font_btn_small = pygame.font.SysFont("Segoe UI", 13, bold=True)
font_label = pygame.font.SysFont("Arial", 15, bold=True)
font_value = pygame.font.SysFont("Segoe UI", 18, bold=True)
font_emoji = pygame.font.SysFont("Segoe UI Emoji", 20)
font_big_title = pygame.font.SysFont("Segoe UI", 48, bold=True)
font_subtitle = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_clock = pygame.font.SysFont("Segoe UI", 60, bold=True)
font_date = pygame.font.SysFont("Segoe UI", 24, bold=True)

# --- THEME HUD ---
SidebarColor     = (30, 32, 36)
PanelColor       = (45, 48, 55)
AccentColor      = (255, 190, 0) # Gold
TextColor        = (220, 220, 220)
BtnColor         = (60, 65, 75)
BtnHoverColor    = (80, 85, 95)
BtnActiveColor   = (100, 180, 100) # Greenish for active speed

# --- SETUP ---
# Carte
game_map = Map(WORLD_WIDTH, WORLD_HEIGHT, POPULATION_SIZE)

# GPS
nav = NavigationGraph()

# Population
population = []
for _ in range(POPULATION_SIZE):
    # Spawn valide
    x, y = game_map.get_valid_spawn_point()
    
    # Création personne
    population.append(Person(x, y, game_map.city_rect, game_map.supermarket["rect"], game_map.sports_complex["rect"], game_map.medical_center["rect"], nav))
    
    # Maison visuelle
    game_map.add_house(x, y)

# Métiers (Supermarché)
checkouts = [
    (529, 740),
    (563, 740),
    (599, 740),
    (634, 740),
    (669, 740),
]
sm_manager = jobs.SupermarketManager(checkouts)

# 3 employés au hasard
workers = random.sample(population, 3)
for w in workers:
    w.job = jobs.SupermarketJob(sm_manager, game_map.supermarket["rect"])
    w.is_employed = True 

# Métiers (Centre Médical)
remaining_pop = [p for p in population if not p.is_employed]
if len(remaining_pop) >= 2:
    medics = random.sample(remaining_pop, 2)
    for m in medics:
        m.job = jobs.MedicalJob(game_map.medical_center["rect"])
        m.is_employed = True

# Patient Zero
patient_zero = random.choice(population)
patient_zero.state = "I"

# Variables de temps
current_hour = 6.0 
game_speed = 1.0 
current_day_index = 0 # 0 = Lundi
day_count = 1 # Global day counter
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
show_graph = False
# Stats State
stats_open = False
stats_anim_cv = 0.0 # Current Value (0.0 -> 1.0)
target_stats_open = False

# Vaccination State
vaccination_active = False
daily_doses = 0

# R0 History
r0_history = []
last_recorded_hour = -1

# SIR History
sir_history = [] # Tuples (S, I, R)

# Heatmap State
infection_locations = [] # List of (x, y)
show_heatmap = False
btn_heatmap = pygame.Rect(0,0,0,0)

# Overlay Nuit
# On crée une surface qui couvre tout l'écran (ou au moins le max possible)
# On la remplit de bleu nuit/noir
day_night_overlay = pygame.Surface((WIDTH, HEIGHT))
day_night_overlay.fill((10, 15, 40)) 


def update_ui_layout():
    """Recalcule la position des éléments d'interface"""
    global btn_slow, btn_fast, btn_stats, btn_graph, btn_close_stats, sidebar_rect, is_sidebar_visible
    global btn_vaccination, btn_doses_minus, btn_doses_plus
    
    # Sidebar
    map_render_width = WORLD_WIDTH * zoom
    if WIDTH > map_render_width:
        sidebar_x = int(map_render_width)
        sidebar_w = WIDTH - sidebar_x
        sidebar_rect = pygame.Rect(sidebar_x, 0, sidebar_w, HEIGHT)
        is_sidebar_visible = True
    else:
        # Fallback si pas de place
        sidebar_rect = pygame.Rect(WIDTH, 0, 0, HEIGHT)
        is_sidebar_visible = False

    if is_sidebar_visible:
        # Centre de la sidebar
        cx = sidebar_rect.centerx
        sidebar_w = sidebar_rect.width
        top = 140
        
        # CONFIG BOUTONS
        # Dynamic sizing relative to sidebar width (base reference ~300px)
        # Scale factor based on width? Or just ratios.
        
        # Row 1: Clock Panel (Larger)
        # Height proportional to width to keep aspect ratio
        clock_panel_h = int(sidebar_w * 0.45) # ~135px for 300w
        
        # Row 2: Speed Controls (Directly below Clock Panel)
        r_controls = top + clock_panel_h + 20
        
        # Button Sizing
        # We want internal margin of 20px total (10 left 10 right) inside the sidebar? 
        # Actually sidebar has 20px padding for panel.
        panel_inner_w = sidebar_w - 40 
        
        # 3 elements: Button(20%) Gap(5%) Display(50%) Gap(5%) Button(20%) ?
        # Let's try: Btn(22%) Gap(10px) Display(Fill) Gap(10px) Btn(22%)
        
        gap_controls = 10
        btn_w = int(panel_inner_w * 0.22)
        btn_h = btn_w # Square buttons as per reference
        
        # Layout: [ < ] [ x1.0 ] [ > ]
        disp_w = panel_inner_w - (btn_w * 2) - (gap_controls * 2)
        
        total_ctrl_w = panel_inner_w # It fills the inner panel width
        start_x = cx - total_ctrl_w // 2
        
        btn_slow = pygame.Rect(start_x, r_controls, btn_w, btn_h)
        # Display rect (just for logic if needed, or purely visual)
        rect_speed = pygame.Rect(start_x + btn_w + gap_controls, r_controls, disp_w, btn_h)
        btn_fast = pygame.Rect(rect_speed.right + gap_controls, r_controls, btn_w, btn_h)
        
        # Next elements (Stats)
        r2 = r_controls + btn_h + 30
        
        # Stats Button (Full Width of inner panel)
        btn_stats = pygame.Rect(cx - panel_inner_w//2, r2, panel_inner_w, btn_h)
        
        # Stats Height estimation (Legend + Simple Panels)
        # Gap 25 + Legend(4*22=88) + Gap 35 + Stats(2*28=56) = ~204
        # Stats Height estimation
        # Reduced to avoid "giga space"
        stats_section_h = 180 
        
        # VACCINATION UI (Below Stats)
        vac_start_y = btn_stats.bottom + stats_section_h + 15
        
        # Button Main (Campaign)
        vac_btn_h = 40
        btn_vaccination = pygame.Rect(cx - panel_inner_w//2, vac_start_y, panel_inner_w, vac_btn_h)
        
        # Controls Row
        ctrl_h = 30
        btn_pm_w = 30
        ctrl_y = btn_vaccination.bottom + 10
        
        # Center dims for controls
        total_ctrl_w = 140
        start_ctrl_x = cx - total_ctrl_w // 2
        
        btn_doses_minus = pygame.Rect(start_ctrl_x, ctrl_y, btn_pm_w, ctrl_h)
        btn_doses_plus  = pygame.Rect(start_ctrl_x + total_ctrl_w - btn_pm_w, ctrl_y, btn_pm_w, ctrl_h)
        
        
        # Row Bottom: Graph (Below Vaccination)
        # Use simple wide button style
        graph_w = panel_inner_w
        graph_h = 40
        graph_y = ctrl_y + ctrl_h + 30
        btn_graph = pygame.Rect(cx - graph_w//2, graph_y, graph_w, graph_h)
        
        
        # Bouton Fermer Stats (Il sera dans la sidebar stats)
        stats_w = 300
        btn_close_stats = pygame.Rect(WIDTH - stats_w + 10, 10, 30, 30)

    else:
        # Fallback (Ancien layout flottant en haut à droite)
        margin = 10
        btn_w, btn_h = 40, 30
        btn_slow = pygame.Rect(WIDTH - (btn_w * 2) - (margin * 2), margin, btn_w, btn_h)
        btn_fast = pygame.Rect(WIDTH - btn_w - margin, margin, btn_w, btn_h)
        # Dummy stats/graph btn for fallback to avoid crash
        btn_stats = pygame.Rect(-100, -100, 10, 10)
        btn_graph = pygame.Rect(-100, -100, 10, 10)
        btn_close_stats = pygame.Rect(-100, -100, 10, 10)
        btn_vaccination = pygame.Rect(-100,-100,10,10)
        btn_doses_minus = pygame.Rect(-100,-100,10,10)
        btn_doses_plus = pygame.Rect(-100,-100,10,10)


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
                elif is_sidebar_visible and btn_graph.collidepoint(mouse_pos):
                    show_graph = not show_graph
                elif is_sidebar_visible and btn_vaccination.collidepoint(mouse_pos):
                    vaccination_active = not vaccination_active
                elif is_sidebar_visible and btn_doses_minus.collidepoint(mouse_pos):
                    daily_doses = max(0, daily_doses - 5)
                elif is_sidebar_visible and btn_doses_plus.collidepoint(mouse_pos):
                    daily_doses += 5
                elif is_sidebar_visible and btn_heatmap.collidepoint(mouse_pos):
                    show_heatmap = not show_heatmap
                
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

    # Update
    # Heure
    current_hour += BASE_CLOCK_SPEED * game_speed
    
    # R0 Sampling
    if int(current_hour) != last_recorded_hour:
        last_recorded_hour = int(current_hour)
        # Calcul R0 Instantané pour historique
        spreaders = [p for p in population if p.state in ["I", "R", "D"]]
        val = 0.0
        if len(spreaders) > 0:
            val = sum(p.infections_caused for p in spreaders) / len(spreaders)
        
        r0_history.append(val)
        if len(r0_history) > 50: # Garde les 50 dernières heures
            r0_history.pop(0)

        # SIR SAMPLING
        sir_s = sum(1 for p in population if p.state == "S")
        sir_i = sum(1 for p in population if p.state == "I")
        sir_r = sum(1 for p in population if p.state == "R")
        sir_history.append((sir_s, sir_i, sir_r))
        if len(sir_history) > 100: # Garde les 100 dernières heures (plus long)
            sir_history.pop(0)

    if current_hour >= 24:
        current_hour = 0
        current_day_index = (current_day_index + 1) % 7
        day_count += 1
        
        # Progression maladie
        for p in population:
            p.update_health()
            p.goes_to_vaccine_today = False 
        
        # Vaccination
        if vaccination_active and daily_doses > 0:
            # On cherche des candidats (Vivants, pas morts)
            # Priorité absolue demandée par l'utilisateur
            candidates = [p for p in population if p.state != "D"]
            
            # On en choisit 'daily_doses'
            nb_to_select = min(len(candidates), daily_doses)
            if nb_to_select > 0:
                selected_people = random.sample(candidates, nb_to_select)
                for p in selected_people:
                    p.goes_to_vaccine_today = True

    # Mise à jour population
    for person in population:
        person.update(current_hour, game_speed, current_day_index)
        
    # Transmission (Proximité)
    # Filtre: Pas ceux en voiture (path actif)
    infected = [p for p in population if p.state == "I" and not p.path]
    susceptible = [p for p in population if p.state == "S" and not p.path]
    
    # Contacts
    for i_person in infected:
        for s_person in susceptible:
            # Distance rapide (carrée) pour éviter racine
            dx = i_person.x - s_person.x
            dy = i_person.y - s_person.y
            dist_sq = dx*dx + dy*dy
            
            if dist_sq < EPI_RADIUS**2:
                # Contact !
                if random.random() < EPI_PROBABILITY:
                    s_person.state = "E" # Devient exposé
                    i_person.infections_caused += 1
                    infection_locations.append((s_person.x, s_person.y))


    # Draw
    screen.fill(BG_COLOR)

    # Monde
    game_map.draw(screen, zoom, pan_x, pan_y, font_label) 
    for person in population:
        person.draw(screen, zoom, pan_x, pan_y)


    # Cycle Jour / Nuit
    # 8h-18h Jour
    # 18h-21h Crépuscule
    # 21h-5h Nuit
    # 5h-8h Aube
    
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
    if show_graph:
        # A. Connexions
        for start_id, end_id in nav.connections:
            p1 = nav.nodes[start_id]
            p2 = nav.nodes[end_id]
            
            s1 = (int(p1[0] * zoom + pan_x), int(p1[1] * zoom + pan_y))
            s2 = (int(p2[0] * zoom + pan_x), int(p2[1] * zoom + pan_y))
            
            pygame.draw.line(screen, (255, 50, 50), s1, s2, 2) 

        # B. Noeuds
        for node_id, pos in nav.nodes.items():
            sx = int(pos[0] * zoom + pan_x)
            sy = int(pos[1] * zoom + pan_y)
            pygame.draw.circle(screen, (255, 50, 50), (sx, sy), 4)

    # ==================================================



    # --- RENDERING ATH ---
    
    if is_sidebar_visible:
        mouse_pos = pygame.mouse.get_pos()
        # 1. FOND
        pygame.draw.rect(screen, SidebarColor, sidebar_rect)
        pygame.draw.line(screen, (50, 50, 60), (sidebar_rect.left, 0), (sidebar_rect.left, HEIGHT), 2)
        
        cx = sidebar_rect.centerx
        
        # 2. TITRE
        # Main Title "PY-DÉMIE"
        title_surf = font_big_title.render("PY-DÉMIE", True, WHITE)
        # Resize if too big
        max_w = sidebar_rect.width - 30
        if title_surf.get_width() > max_w:
             ratio = max_w / title_surf.get_width()
             new_h = int(title_surf.get_height() * ratio)
             title_surf = pygame.transform.smoothscale(title_surf, (max_w, new_h))
        
        screen.blit(title_surf, (cx - title_surf.get_width()//2, 30))
        
        # Separator Line
        line_y = 30 + title_surf.get_height() + 5
        line_width = min(240, sidebar_rect.width - 50)
        pygame.draw.line(screen, (60, 60, 70), (cx - line_width//2, line_y), (cx + line_width//2, line_y), 2)

        # Subtitle "SIMULATEUR D'ÉPIDÉMIE"
        sub_surf = font_subtitle.render("SIMULATEUR D'ÉPIDÉMIE", True, WHITE)
        if sub_surf.get_width() > max_w:
             ratio = max_w / sub_surf.get_width()
             new_h = int(sub_surf.get_height() * ratio)
             sub_surf = pygame.transform.smoothscale(sub_surf, (max_w, new_h))

        screen.blit(sub_surf, (cx - sub_surf.get_width()//2, line_y + 10))
        
        # 3. PANNEAU DATE HEURE (NOUVEAU DESIGN 3D)
        # Dynamic height
        sidebar_w = sidebar_rect.width
        clock_panel_h = int(sidebar_w * 0.45)
        
        # Base/Shadow (Effet 3D)
        shadow_depth = 10
        # On dessine le fond (PanelColor) décalé vers le bas
        base_rect = pygame.Rect(sidebar_rect.left + 20, 140 + shadow_depth, sidebar_rect.width - 40, clock_panel_h)
        pygame.draw.rect(screen, (40, 40, 40), base_rect, border_radius=12) # Couleur #282828
        
        # Fond Noir (Face avant)
        panel_rect = pygame.Rect(sidebar_rect.left + 20, 140, sidebar_rect.width - 40, clock_panel_h)
        pygame.draw.rect(screen, BLACK, panel_rect, border_radius=12)
        # Légère bordure grise sombre
        pygame.draw.rect(screen, (49, 49, 49), panel_rect, 3, border_radius=12) # Couleur #313131
        
        # Heure (Grande, Blanche)
        hour_val = int(current_hour)
        minute_val = 0 # On reste sur des heures pleines pour l'instant
        time_str = f"{hour_val:02d} : {minute_val:02d}"
        
        draw_time = font_clock.render(time_str, True, WHITE)
        # Scale Time (Max 75% of panel width)
        max_time_w = panel_rect.width * 0.75
        if draw_time.get_width() > max_time_w:
            ratio = max_time_w / draw_time.get_width()
            new_h = int(draw_time.get_height() * ratio)
            draw_time = pygame.transform.smoothscale(draw_time, (int(max_time_w), new_h))
            
        # Center vertically in upper part
        # Center point roughly at 35% height
        time_y = panel_rect.y + int(clock_panel_h * 0.35) - draw_time.get_height()//2
        screen.blit(draw_time, (panel_rect.centerx - draw_time.get_width()//2, time_y))
        
        # Date (Gris, LUNDI - JOUR X)
        day_str = f"{DAYS[current_day_index].upper()} - JOUR {day_count}"
        draw_date = font_date.render(day_str, True, (150, 150, 160))
        
        # Scale Date (Max 90% of panel width)
        if draw_date.get_width() > max_time_w:
            ratio = max_time_w / draw_date.get_width()
            new_h = int(draw_date.get_height() * ratio)
            draw_date = pygame.transform.smoothscale(draw_date, (int(max_time_w), new_h))

        # Position below time (roughly 75% height)
        date_y = panel_rect.y + int(clock_panel_h * 0.75) - draw_date.get_height()//2
        screen.blit(draw_date, (panel_rect.centerx - draw_date.get_width()//2, date_y))


        # 4. SPEED CONTROLS (3D BUTTONS)
        # Helper pour bouton 3D (Shifted Base approach)
        def draw_3d_btn(rect, color_top, color_shadow, icon_str, pressed=False):
            # shadow_h = fixed depth (e.g. 6)
            depth = 6
            
            # Pressed state: Move TOP rect down by half depth
            # Unpressed state: Top rect is at original pos
            if pressed: 
                y_offset = depth // 2
            else:
                y_offset = 0
            
            # Base Rect (Shadow) - Always at rect.y + depth
            # Note: rect is assumed to be the "layout slot" for the top face.
            # To avoid layout overlap, we draw base slightly below.
            base_rect = pygame.Rect(rect.x, rect.y + depth, rect.width, rect.height)
            pygame.draw.rect(screen, color_shadow, base_rect, border_radius=10)
            
            # Top Rect (Face)
            top_rect = pygame.Rect(rect.x, rect.y + y_offset, rect.width, rect.height)
            pygame.draw.rect(screen, color_top, top_rect, border_radius=10)
            
            # Icon (< ou >)
            ic = font_clock.render(icon_str, True, WHITE)
            # Scale Icon to fit button (30% width?)
            max_ic_w = rect.width * 0.4
            if ic.get_width() > max_ic_w:
                 ratio = max_ic_w / ic.get_width()
                 new_h = int(ic.get_height() * ratio)
                 ic = pygame.transform.smoothscale(ic, (int(max_ic_w), new_h))
                 
            screen.blit(ic, (top_rect.centerx - ic.get_width()//2, top_rect.centery - ic.get_height()//2 - 2))

        # SLOW (<) - RED
        c_red_top = (180, 50, 50)
        c_red_bot = (130, 30, 30)
        c_green_top = (50, 180, 60)
        c_green_bot = (30, 130, 40)
        
        # Check interaction
        slow_pressed = btn_slow.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]
        fast_pressed = btn_fast.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]

        draw_3d_btn(btn_slow, c_red_top, c_red_bot, "<", pressed=slow_pressed)
        
        # Display Box (Center)
        # Recalcul position based on buttons
        space_between = btn_fast.left - btn_slow.right
        # Reducing width slightly as requested (bigger gap)
        display_w = space_between - 30 
        rect_speed = pygame.Rect(btn_slow.right + 15, btn_slow.top, display_w, btn_slow.height)
        
        # 3D Effect for Display (Shifted Base approach)
        c_speed_top = (40, 40, 40)    # Dark Grey
        c_speed_shadow = (25, 25, 25) # Darker Black/Grey
        
        # Base/Shadow
        depth = 6
        base_rect_speed = pygame.Rect(rect_speed.x, rect_speed.y + depth, rect_speed.width, rect_speed.height)
        pygame.draw.rect(screen, c_speed_shadow, base_rect_speed, border_radius=10)
        
        # Main Face
        pygame.draw.rect(screen, c_speed_top, rect_speed, border_radius=10)
        
        # Speed Text
        spd_str = f"x{game_speed:.1f}"
        spd_txt = font_title.render(spd_str, True, WHITE)
        # Scale to max 60% width of display box
        max_spd_w = rect_speed.width * 0.6
        if spd_txt.get_width() > max_spd_w:
            ratio = max_spd_w / spd_txt.get_width()
            new_h = int(spd_txt.get_height() * ratio)
            spd_txt = pygame.transform.smoothscale(spd_txt, (int(max_spd_w), new_h))
            
        screen.blit(spd_txt, (rect_speed.centerx - spd_txt.get_width()//2, rect_speed.centery - spd_txt.get_height()//2))

        # FAST (>) - GREEN
        draw_3d_btn(btn_fast, c_green_top, c_green_bot, ">", pressed=fast_pressed)

        # 4. (SUITE) BOUTONS STYLÉS (STATS, etc)
        
        # STATS BUTTON (Purple 3D with Text)
        c_stats_top = (138, 43, 226) # BlueViolet / Purple
        c_stats_bot = (75, 0, 130)   # Indigo / Darker Purple
        
        # Check interaction
        stats_pressed = btn_stats.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]
        
        # 3D Logic (Shifted Base)
        depth = 6
        if stats_pressed: y_offset = depth // 2
        else: y_offset = 0
            
        # Base
        base_rect_stats = pygame.Rect(btn_stats.x, btn_stats.y + depth, btn_stats.width, btn_stats.height)
        pygame.draw.rect(screen, c_stats_bot, base_rect_stats, border_radius=10)
        
        # Top
        top_rect_stats = pygame.Rect(btn_stats.x, btn_stats.y + y_offset, btn_stats.width, btn_stats.height)
        pygame.draw.rect(screen, c_stats_top, top_rect_stats, border_radius=10)
        
        # Text "STATISTIQUES"
        txt_stats = font_subtitle.render("STATISTIQUES", True, WHITE) # Using subtitle font (bold 16)
        screen.blit(txt_stats, (top_rect_stats.centerx - txt_stats.get_width()//2, top_rect_stats.centery - txt_stats.get_height()//2))


        # --- Helper Style (Restored for Graph/Vaccination if needed, though Graph is next) ---
        def draw_ctrl_btn(rect, color, icon_type, text=None, active=False):
            # Fond
            base_col = list(color)
            if active: base_col = [min(255, c + 40) for c in base_col]
            elif rect.collidepoint(mouse_pos): base_col = [min(255, c + 20) for c in base_col]
            
            pygame.draw.rect(screen, base_col, rect, border_radius=8)
            # Bordure basale
            pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=8)
            
            icx, icy = rect.centerx, rect.centery
            
            # Si texte, on decale l'icone a gauche
            if text:
                lbl = font_btn_small.render(text, True, WHITE)
                # Icone à gauche fixe (rect.left + 20)
                icx = rect.left + 20
                
                # Le text doit être centré dans l'espace restant (entre icx + 10 et rect.right)
                space_start = icx + 10
                space_width = rect.right - space_start
                text_x = space_start + (space_width - lbl.get_width()) // 2
                
                screen.blit(lbl, (text_x, rect.centery - lbl.get_height()//2))

            # Icon
            if icon_type == "minus":
                pygame.draw.rect(screen, WHITE, (icx-8, icy-2, 16, 4))
            elif icon_type == "plus":
                pygame.draw.rect(screen, WHITE, (icx-8, icy-2, 16, 4))
                pygame.draw.rect(screen, WHITE, (icx-2, icy-8, 4, 16))
            elif icon_type == "stats":
                # Histogramme petit
                pygame.draw.rect(screen, WHITE, (icx-6, icy+2, 3, 6))
                pygame.draw.rect(screen, WHITE, (icx-1, icy-2, 3, 10))
                pygame.draw.rect(screen, WHITE, (icx+4, icy-5, 3, 13))
            elif icon_type == "graph":
                # Noeuds
                pygame.draw.circle(screen, WHITE, (icx-6, icy+4), 3)
                pygame.draw.circle(screen, WHITE, (icx+6, icy-4), 3)
                pygame.draw.circle(screen, WHITE, (icx+5, icy+6), 3)
                pygame.draw.line(screen, WHITE, (icx-6, icy+4), (icx+6, icy-4), 2)
                pygame.draw.line(screen, WHITE, (icx+6, icy-4), (icx+5, icy+6), 2)

        
        # STATS (Purple) - Old call removed (Replaced by 3D version above)
        
        # --- MINI STATS EPIDEMIE (Sidebar) ---
        # On affiche 3 cartes "Widget" en colonne
        
        # Calculs
        nb_susceptible = sum(1 for p in population if p.state == "S")
        nb_exposed = sum(1 for p in population if p.state == "E")
        nb_infected = sum(1 for p in population if p.state == "I")
        nb_recovered = sum(1 for p in population if p.state == "R")
        nb_vaccinated = sum(1 for p in population if p.state == "V")
        nb_dead = sum(1 for p in population if p.state == "D")
        total_pop = len(population)
        
        # Zone disponible (Maintenant limitée par le bouton vaccin en bas)
        epi_y_start = btn_stats.bottom + 45 # Increased spacing from 15 to 45
        epi_y_end = btn_vaccination.top - 15
        epi_h_total = max(50, epi_y_end - epi_y_start)
        
        # 1. PIE CHART (REMOVED per user request)
        
        # Data (Keep needed visual logic vars)
        nb_susceptible = sum(1 for p in population if p.state == "S")
        nb_infected = sum(1 for p in population if p.state == "I")
        nb_recovered = sum(1 for p in population if p.state == "R")
        nb_vaccinated = sum(1 for p in population if p.state == "V")
        nb_exposed = sum(1 for p in population if p.state == "E") # Used later
        nb_dead = sum(1 for p in population if p.state == "D")    # Used later
        
        total_live = nb_susceptible + nb_infected + nb_recovered + nb_vaccinated
        if total_live == 0: total_live = 1
        
        # Colors 
        col_sains = (40, 160, 60)
        col_infecte = (180, 50, 50)
        col_vaccine = (40, 120, 180)
        col_gueri = (200, 160, 20)
        
        
        # 2. LÉGENDE
        leg_start_y = btn_stats.bottom + 25 # Moved up since Pie Chart is gone
        # Font for legend
        font_legend = pygame.font.SysFont("Segoe UI", 14, bold=True)
        # Numbers font
        font_leg_val = pygame.font.SysFont("Segoe UI", 14, bold=True)
        
        def draw_legend_item(x, y, color, label, val):
            # Square
            sq_size = 14
            pygame.draw.rect(screen, color, (x, y, sq_size, sq_size), border_radius=3)
            # Label
            lbl = font_legend.render(label, True, WHITE)
            screen.blit(lbl, (x + sq_size + 8, y - 2))
            # Value (Grey)
            v_s = font_leg_val.render(str(val), True, (150, 150, 160))
            screen.blit(v_s, (x + sq_size + 8 + lbl.get_width() + 4, y - 2))

        # Cols (Single Column)
        col_x = sidebar_rect.left + 35
        row_gap = 22
        
        draw_legend_item(col_x, leg_start_y,              col_sains, "Sains", nb_susceptible)
        draw_legend_item(col_x, leg_start_y + row_gap*1,  col_infecte, "Infecté", nb_infected)
        draw_legend_item(col_x, leg_start_y + row_gap*2,  col_vaccine, "Vacciné", nb_vaccinated)
        draw_legend_item(col_x, leg_start_y + row_gap*3,  col_gueri, "Guéri", nb_recovered)
        
        last_legend_y = leg_start_y + row_gap*3

        # 3. STATUTS SIMPLIFIÉS (Text + Emoji)
        
        stat_start_y = last_legend_y + 35
        
        # Helper Text
        def draw_simple_stat(x, y, emoji, label, count, color_val):
            # Emoji
            emo = font_emoji.render(emoji, True, WHITE)
            screen.blit(emo, (x, y))
            
            # Label
            lbl = font_legend.render(label, True, WHITE)
            # Position: Right of emoji
            lbl_x = x + 30 
            screen.blit(lbl, (lbl_x, y + 2))
            
            # Value ": X"
            val_s = font_leg_val.render(f": {count}", True, color_val)
            screen.blit(val_s, (lbl_x + lbl.get_width() + 2, y + 2))

        # Incubation (Orange/Coral text for number to pop?)
        # Use simple grey/white to match legend style or slightly colored.
        # User said "Like legend", legend has Grey numbers. 
        # But Incubation/Death is important. Let's use Light Grey/White.
        
        draw_simple_stat(col_x, stat_start_y, "🕰️", "En incubation", nb_exposed, (200, 200, 200))
        
        # Décès
        draw_simple_stat(col_x, stat_start_y + 28, "💀", "Décès", nb_dead, (180, 50, 50)) # Red number for deaths? Or just grey? 
        # Let's stick to Grey/White scaling. The user asked for "Like legend".
        # Legend uses: (150, 150, 160)
        # Let's use that.

        current_y = epi_y_start
        
        for i, p in enumerate([]): # Loop disabled for redesign
            # Ajout d'espaces entre les groupes
            # Groupe 2 commence à l'index 3 (S, V, R sont 0, 1, 2)
            if i == 3: 
                current_y += 25 # Espace avant "Incubation"
            
            # Groupe 3 commence à l'index 5 (S, V, R, E, I sont 0..4)
            if i == 5:
                current_y += 25 # Espace avant "Décès"

            w_rect = pygame.Rect(wx, current_y, widget_w, widget_h)
            wy = current_y # Alias pour le code de dessin existant
            
            # Fond
            pygame.draw.rect(screen, PanelColor, w_rect, border_radius=6)
            # Bordure gauche colorée
            pygame.draw.rect(screen, p["col"], (wx, wy, 8, widget_h), border_top_left_radius=6, border_bottom_left_radius=6)
            
            # Valeur (Gros)
            val_s = font_value.render(str(p["val"]), True, WHITE)
            screen.blit(val_s, (wx + 90 - val_s.get_width(), wy + widget_h//2 - val_s.get_height()//2))

            # Pourcentage (Petit et Gris)
            if total_pop > 0:
                pct = int((p["val"] / total_pop) * 100)
                pct_str = f"{pct}%"
            else:
                pct_str = "0%"

            pct_s = font_btn_small.render(pct_str, True, (150, 150, 150))
            # On affiche à droite de la valeur (wx + 95)
            screen.blit(pct_s, (wx + 95, wy + widget_h//2 - pct_s.get_height()//2 + 2))
            
            # EMOJI RENDERING
            # Note: Les emojis en couleur ne marchent pas toujours bien avec pygame.font.SysFont
            # Si ça rend en N&B, c'est une limitation Pygame/SDL sur Windows sans librairies externes (freetype/harfbuzz).
            # On essaye quand même.
            # On force la couleur blanche pour qu'ils soient visibles si le rendu est monochrome.
            emo = font_emoji.render(p["emoji"], True, WHITE) 
            screen.blit(emo, (wx + 25 - emo.get_width()//2, wy + widget_h//2 - emo.get_height()//2))
            
            # Increment Y pour le prochain
            current_y += widget_h + 8 
        
        
        # --- VACCINATION UI ---
        # --- VACCINATION UI (3D Style) ---
        
        # 1. Main Button (Toggle) - 3D
        # Active: Green / Inactive: Grey
        if vaccination_active:
            c_vac_top = (50, 160, 80)
            c_vac_bot = (30, 100, 50)
        else:
            c_vac_top = (70, 70, 75)
            c_vac_bot = (50, 50, 55)
            
        vac_pressed = btn_vaccination.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]
        # Use our 3D logic
        # We can reuse draw_3d_btn but it expects an icon string. 
        # We want "VACCINATION" text.
        # Let's inline the simplified 3D draw for text button.
        
        depth = 6
        v_offset = depth // 2 if vac_pressed else 0
        
        # Base
        pygame.draw.rect(screen, c_vac_bot, (btn_vaccination.x, btn_vaccination.y + depth, btn_vaccination.width, btn_vaccination.height), border_radius=8)
        # Top
        vac_top_rect = pygame.Rect(btn_vaccination.x, btn_vaccination.y + v_offset, btn_vaccination.width, btn_vaccination.height)
        pygame.draw.rect(screen, c_vac_top, vac_top_rect, border_radius=8)
        
        # Text
        v_txt = font_label.render("VACCINATION", True, WHITE)
        screen.blit(v_txt, (vac_top_rect.centerx - v_txt.get_width()//2, vac_top_rect.centery - v_txt.get_height()//2))
        
        
        # 2. Controls (+ / -) and Display
        # Minus
        minus_pressed = btn_doses_minus.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]
        draw_3d_btn(btn_doses_minus, (70, 70, 75), (50, 50, 55), "-", pressed=minus_pressed)
        
        # Plus
        plus_pressed = btn_doses_plus.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]
        draw_3d_btn(btn_doses_plus, (70, 70, 75), (50, 50, 55), "+", pressed=plus_pressed)
        
        # Number Display (3D Inset/Box style like Speed)
        val_area_rect = pygame.Rect(btn_doses_minus.right + 10, btn_doses_minus.top, btn_doses_plus.left - btn_doses_minus.right - 20, btn_doses_minus.height)
        
        # Base (Shadow)
        pygame.draw.rect(screen, (25, 25, 25), (val_area_rect.x, val_area_rect.y + 4, val_area_rect.width, val_area_rect.height), border_radius=6)
        # Face (Top)
        pygame.draw.rect(screen, (40, 40, 40), val_area_rect, border_radius=6)
        
        val_txt = font_label.render(f"{daily_doses} /j", True, WHITE)
        screen.blit(val_txt, (val_area_rect.centerx - val_txt.get_width()//2, val_area_rect.centery - val_txt.get_height()//2))
        

        # GRAPH (White 3D with Black Text)
        c_graph_top = (255, 255, 255) 
        c_graph_bot = (200, 200, 200)
        
        graph_pressed = btn_graph.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]
        
        # 3D Logic
        depth = 6
        g_offset = depth // 2 if graph_pressed else 0
        
        # Base
        base_rect_graph = pygame.Rect(btn_graph.x, btn_graph.y + depth, btn_graph.width, btn_graph.height)
        pygame.draw.rect(screen, c_graph_bot, base_rect_graph, border_radius=10)
        
        # Top
        top_rect_graph = pygame.Rect(btn_graph.x, btn_graph.y + g_offset, btn_graph.width, btn_graph.height)
        pygame.draw.rect(screen, c_graph_top, top_rect_graph, border_radius=10)
        
        # Text "GRAPHE" (Black)
        txt_graph = font_subtitle.render("GRAPHE", True, (20, 20, 20)) 
        screen.blit(txt_graph, (top_rect_graph.centerx - txt_graph.get_width()//2, top_rect_graph.centery - txt_graph.get_height()//2))

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
        
        # Stats Épidémie
        nb_infected = sum(1 for p in population if p.state == "I")
        nb_exposed = sum(1 for p in population if p.state == "E") # Invisible user-facing ou pas ? Montrons-le pour le debug/fun
        nb_recovered = sum(1 for p in population if p.state == "R")
        nb_dead = sum(1 for p in population if p.state == "D")

        shoppers = [p for p in population if p.shopping_day == current_day_index]
        nb_shoppers = len(shoppers)

        # DATA POUR CARDS
        stats_cards = [
            {"label": "POPULATION", "value": str(total_pop), "color": (100, 150, 240), "icon": "pop"},
            {"label": "SPORTIFS", "value": f"{nb_sportive} ({pct_sport}%)", "color": (240, 100, 100), "icon": "sport"},
            {"label": "TRAVAILLEURS", "value": str(nb_workers), "color": (240, 200, 80), "icon": "work"},
            {"label": "SHOPPING", "value": str(nb_shoppers), "color": (100, 220, 120), "icon": "shop"},
        ]

        card_h = 45
        card_w = s_w - 40
        gap = 8

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
            
            elif card["icon"] == "virus":
                # Cercle avec picots
                c = card["color"]
                pygame.draw.circle(screen, c, icon_center, 6)
                for i in range(8):
                    angle = i * (3.14159 * 2 / 8)
                    ex = icon_center[0] + math.cos(angle) * 10
                    ey = icon_center[1] + math.sin(angle) * 10
                    pygame.draw.line(screen, c, icon_center, (ex, ey), 2)

            elif card["icon"] == "shield":
                # Forme écu
                c = card["color"]
                pygame.draw.polygon(screen, c, [
                    (icon_center[0]-8, icon_center[1]-8),
                    (icon_center[0]+8, icon_center[1]-8),
                    (icon_center[0]+8, icon_center[1]),
                    (icon_center[0], icon_center[1]+10),
                    (icon_center[0]-8, icon_center[1])
                ])

            elif card["icon"] == "skull":
                # Crâne simple
                c = card["color"]
                pygame.draw.circle(screen, c, (icon_center[0], icon_center[1]-2), 7)
                pygame.draw.rect(screen, c, (icon_center[0]-4, icon_center[1]+2, 8, 6))
                pygame.draw.line(screen, (0,0,0), (icon_center[0]-2, icon_center[1]-2), (icon_center[0]-2, icon_center[1]), 2) # Yeux
                pygame.draw.line(screen, (0,0,0), (icon_center[0]+2, icon_center[1]-2), (icon_center[0]+2, icon_center[1]), 2)

            # Textes (Centrage Vertical)
            lbl_s = font_label.render(card["label"], True, (180, 180, 190))
            val_s = font_value.render(card["value"], True, WHITE)
            
            total_text_h = lbl_s.get_height() + val_s.get_height()
            start_y = cy + (card_h - total_text_h) // 2
            
            screen.blit(lbl_s, (dx + 70, start_y)) # label
            screen.blit(val_s, (dx + 70, start_y + lbl_s.get_height() - 2)) # value (petit overlap de 2px pour resserrer)

        # --- R0 DISPLAY ---
        # Calcul du R0
        # On prend tous ceux qui ont été infectieux (I, R, D)
        spreaders = [p for p in population if p.state in ["I", "R", "D"]]
        if len(spreaders) > 0:
            total_inf = sum(p.infections_caused for p in spreaders)
            r0_val = total_inf / len(spreaders)
        else:
            r0_val = 0.0
        
        # Positionnement : En dessous des widgets stats
        # On le place sous le panneau "DÉCÉDÉS" (panel_dead_y + panel_h + 15)
        # Mais on n'a pas accès facilement à ces variables locales ici car on est hors scope ?
        # Wait, lines 1107 are seemingly further down in the file.
        # Check if we are inside the same function scope.
        # Actually this looks like it might be stray code or a second pass?
        # Let's anchor it to btn_vaccination.top - 60 (above vaccination button) if possible?
        # OR just under the last known element.
        # Let's say relative to btn_stats.bottom + 300? No that's risky.
        # Safest: relative to btn_vaccination.top - 80 
        
        # Positionnement : Relative to last card (Compact)
        # 4 cards total. Cursor was at start y.
        # last card y = y_cursor + 3*(card_h+gap)
        # r0 should be below that.
        last_card_bottom = y_cursor + (4 * (card_h + gap))
        r0_y = last_card_bottom + 10 
        r0_rect = pygame.Rect(curr_x + 20, r0_y, s_w - 40, 45)
        
        # Fond R0 (Un peu différent pour ressortir ?)
        pygame.draw.rect(screen, (55, 50, 65), r0_rect, border_radius=8)
        # Bordure gauche (Violet/Rose)
        r0_col = (200, 100, 200)
        pygame.draw.rect(screen, r0_col, (r0_rect.x, r0_rect.y, 6, r0_rect.height), border_top_left_radius=8, border_bottom_left_radius=8)
        
        # Icone Biohazard/Chart
        # ic_center = (dx + 35, r0_y + card_h//2)
        emo_r0 = font_emoji.render("☣️", True, WHITE) # Biohazard
        screen.blit(emo_r0, (r0_rect.x + 25 - emo_r0.get_width()//2, r0_rect.centery - emo_r0.get_height()//2))

        # Texte
        lbl_r0 = font_label.render("TAUX R0", True, (180, 180, 190))
        val_r0 = font_value.render(f"{r0_val:.2f}", True, WHITE)
        
        # Centrage vertical text
        total_text_h_r0 = lbl_r0.get_height() + val_r0.get_height()
        start_y_r0 = r0_rect.y + (r0_rect.height - total_text_h_r0) // 2
        
        screen.blit(lbl_r0, (r0_rect.x + 70, start_y_r0))
        screen.blit(val_r0, (r0_rect.x + 70, start_y_r0 + lbl_r0.get_height() - 2))

        # --- GRAPH R0 ---
        # Zone Graph
        graph_h = 60
        g_y = r0_rect.bottom + 10
        g_rect = pygame.Rect(r0_rect.x, g_y, r0_rect.width, graph_h)
        
        # Fond Graph
        pygame.draw.rect(screen, (40, 40, 45), g_rect, border_radius=6)
        
        # Ligne seuil R0 = 1.0
        # Echelle : 0 en bas, Max dynaminc (min 2.0)
        max_val = max(2.0, max(r0_history) if r0_history else 0)
        
        def get_y(v):
            ratio = v / max_val
            return g_y + graph_h - (ratio * graph_h)
            
        # Draw Grids & Labels
        # Values to show: 0, 1.0, Max
        grid_vals = [0, 1.0, max_val]
        
        for val in grid_vals:
            y_pos = int(get_y(val))
            if g_y <= y_pos <= g_y + graph_h:
                # Grid Line
                col = (100, 100, 100) if val == 1.0 else (60, 60, 65)
                width = 1
                pygame.draw.line(screen, col, (dx, y_pos), (dx + card_w, y_pos), width)
                
                # Label
                if val == 1.0 or val == max_val or val == 0:
                    lbl = font_btn_small.render(f"{val:.1f}", True, (150, 150, 150))
                    # Align Right inside graph
                    screen.blit(lbl, (dx + card_w - lbl.get_width() - 2, y_pos - lbl.get_height() + 2))

        # Courbe
        if len(r0_history) > 1:
            points = []
            step_x = card_w / (len(r0_history) - 1)
            for i, val in enumerate(r0_history):
                px = dx + (i * step_x)
                py = get_y(val)
                points.append((px, py))
            
            if len(points) >= 2:
                pygame.draw.lines(screen, (200, 100, 200), False, points, 2)


        # --- SIR TRENDS GRAPH (BIG) ---
        # Position: Close below R0 Graph
        sir_y = g_rect.bottom + 60 # Increased spacing as requested (was 30)
        sir_h = 100
        sir_rect = pygame.Rect(dx, sir_y, card_w, sir_h)
        
        # Fond
        pygame.draw.rect(screen, (35, 38, 42), sir_rect, border_radius=6)
        
        # Titre Mini
        sir_title = font_label.render("EVOLUTION S-I-R", True, (150, 150, 150))
        screen.blit(sir_title, (dx, sir_y - 45)) # Remonté pour laisser place à la légende
        
        # LEGENDE
        leg_y = sir_y - 20
        # S (Bleu)
        pygame.draw.circle(screen, (100, 150, 240), (dx + 10, leg_y), 4)
        l_s = font_btn_small.render("Sains", True, (150, 150, 150))
        screen.blit(l_s, (dx + 20, leg_y - l_s.get_height()//2))
        
        # I (Rouge)
        lx_i = dx + 80
        pygame.draw.circle(screen, C_INFECTED, (lx_i, leg_y), 4)
        l_i = font_btn_small.render("Infectés", True, (150, 150, 150))
        screen.blit(l_i, (lx_i + 10, leg_y - l_i.get_height()//2))

        # R (Jaune)
        lx_r = dx + 160
        pygame.draw.circle(screen, C_RECOVERED, (lx_r, leg_y), 4)
        l_r = font_btn_small.render("Guéris", True, (150, 150, 150))
        screen.blit(l_r, (lx_r + 10, leg_y - l_r.get_height()//2))

        if len(sir_history) > 1:
            total_pop_count = len(population)
            step_x = card_w / (len(sir_history) - 1)
            
            # Helper points generator
            def get_points(idx): # idx 0=S, 1=I, 2=R
                pts = []
                for i, data in enumerate(sir_history):
                    val = data[idx]
                    px = dx + (i * step_x)
                    py = sir_y + sir_h - (val / total_pop_count * sir_h)
                    pts.append((px, py))
                return pts

            pts_s = get_points(0)
            pts_i = get_points(1)
            pts_r = get_points(2)
            
            # Draw Curves
            if len(pts_s) >= 2: pygame.draw.lines(screen, (100, 150, 240), False, pts_s, 2) # S - Blue
            if len(pts_r) >= 2: pygame.draw.lines(screen, C_RECOVERED, False, pts_r, 2)   # R - Yellow/Green
            if len(pts_i) >= 2: pygame.draw.lines(screen, C_INFECTED, False, pts_i, 2)    # I - Red (Au dessus)

        # --- BTN HEATMAP ---
        hm_y = sir_y + sir_h + 20
        btn_heatmap = pygame.Rect(dx, hm_y, card_w, 40)
        
        hm_col = (180, 50, 50) if show_heatmap else (70, 70, 75)
        if btn_heatmap.collidepoint(pygame.mouse.get_pos()):
             hm_col = [min(255, c+20) for c in hm_col]
        
        pygame.draw.rect(screen, hm_col, btn_heatmap, border_radius=6)
        
        # Texte / Icone
        hm_txt = font_label.render("HEATMAP", True, WHITE)
        screen.blit(hm_txt, (btn_heatmap.centerx - hm_txt.get_width()//2, btn_heatmap.centery - hm_txt.get_height()//2))

    # --- RENDERING HEATMAP OVERLAY (On top of map, below UI) ---
    # Need to be drawn BEFORE UI but AFTER Map. 
    # Oops, "draw" section structure:
    # 1. Map (done)
    # 2. People (done)
    # 3. Night Overlay (done)
    # 4. Sidebar (done)
    # We are here (End of loop).
    # If we draw here, it is ON TOP of the sidebar if overlapping (rare) but that is fine.
    
    if show_heatmap:
        # Create a surface for alpha blending
        # Optimization: Don't create surface every frame if many points?
        # For simple dots, direct drawing on screen with alpha is not directly supported by circle.
        # We need a surface with per-pixel alpha or use a transparent image.
        
        # Simple method: Draw circles on a transparent surface
        hm_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Draw spots
        # Red with alpha ~50
        spot_color = (255, 0, 0, 50) 
        radius = int(15 * zoom) # Scale spot with zoom
        if radius < 5: radius = 5
        
        for (hx, hy) in infection_locations:
            # Transform to screen coords
            sx = int(hx * zoom + pan_x)
            sy = int(hy * zoom + pan_y)
            
            # Draw only if onscreen
            if -radius < sx < WIDTH+radius and -radius < sy < HEIGHT+radius:
                pygame.draw.circle(hm_surf, spot_color, (sx, sy), radius)
                # Core
                pygame.draw.circle(hm_surf, (255, 50, 50, 100), (sx, sy), radius//2)
        
        screen.blit(hm_surf, (0,0))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()