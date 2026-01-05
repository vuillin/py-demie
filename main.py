import pygame
from settings import *
from person import Person
from map import Map
from navigation import NavigationGraph

# Initialisation
pygame.init()
is_fullscreen = True
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size() # On récupère la taille réelle de l'écran
pygame.display.set_caption("Py-Démie")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)
font_btn = pygame.font.SysFont("Arial", 25, bold=True)
font_label = pygame.font.SysFont("Arial", 15, bold=True)

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
    population.append(Person(x, y, game_map.city_rect, nav))
    
    # On ajoute sa maison visuelle à cet endroit
    game_map.add_house(x, y)

# Variables de temps
current_hour = 6.0 
game_speed = 1.0 

# Variables Caméra
zoom = min(WIDTH / WORLD_WIDTH, HEIGHT / WORLD_HEIGHT) # Auto-fit
min_zoom = 0.5
max_zoom = 4.0
zoom_speed = 0.1
pan_x, pan_y = 0, 0
is_panning = False
last_mouse_pos = (0, 0)

# Boutons UI
btn_w, btn_h = 40, 30
margin = 10
btn_slow = pygame.Rect(WIDTH - (btn_w * 2) - (margin * 2), margin, btn_w, btn_h)
btn_fast = pygame.Rect(WIDTH - btn_w - margin, margin, btn_w, btn_h)
btn_screen = pygame.Rect(WIDTH - (btn_w * 3) - (margin * 3), margin, btn_w, btn_h)

def update_ui_layout():
    """Recalcule la position des éléments d'interface selon la taille d'écran"""
    global btn_slow, btn_fast, btn_screen
    btn_slow = pygame.Rect(WIDTH - (btn_w * 2) - (margin * 2), margin, btn_w, btn_h)
    btn_fast = pygame.Rect(WIDTH - btn_w - margin, margin, btn_w, btn_h)
    btn_screen = pygame.Rect(WIDTH - (btn_w * 3) - (margin * 3), margin, btn_w, btn_h)

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
                elif btn_screen.collidepoint(mouse_pos):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT))
                    
                    # Mise à jour des dimensions et de l'interface
                    WIDTH, HEIGHT = screen.get_size()
                    zoom = min(WIDTH / WORLD_WIDTH, HEIGHT / WORLD_HEIGHT) # Re-fit auto
                    update_ui_layout()
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
    if current_hour >= 24: current_hour = 0

    # Mise à jour population
    for person in population:
        person.update(current_hour, game_speed)

    # 3. Draw
    screen.fill(BG_COLOR)

    # A. Monde
    game_map.draw(screen, zoom, pan_x, pan_y, font_label) # On passe la font pour le supermarché
    for person in population:
        person.draw(screen, zoom, pan_x, pan_y)




    # ==================================================
    # --- DEBUG : AFFICHER LE RÉSEAU (Graphe) ---
    # ==================================================
    if True: # Mets False ici pour cacher le graphe sans supprimer le code
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



    # B. UI
    ui_bg = pygame.Surface((150, 60))
    ui_bg.set_alpha(150)
    ui_bg.fill((0, 0, 0))
    screen.blit(ui_bg, (5, 5))

    time_text = font.render(f"Heure: {int(current_hour)}h", True, WHITE)
    screen.blit(time_text, (10, 10))
    
    speed_text = font.render(f"Vitesse: x{game_speed:.1f}", True, (200, 200, 100))
    screen.blit(speed_text, (10, 35))

    # Boutons
    pygame.draw.rect(screen, (70, 70, 80), btn_slow)
    pygame.draw.rect(screen, (200, 200, 200), btn_slow, 2)
    text_slow = font_btn.render("-", True, WHITE)
    screen.blit(text_slow, (btn_slow.centerx - text_slow.get_width()//2, btn_slow.centery - text_slow.get_height()//2))

    pygame.draw.rect(screen, (70, 70, 80), btn_fast)
    pygame.draw.rect(screen, (200, 200, 200), btn_fast, 2)
    text_fast = font_btn.render("+", True, WHITE)
    screen.blit(text_fast, (btn_fast.centerx - text_fast.get_width()//2, btn_fast.centery - text_fast.get_height()//2))

    pygame.draw.rect(screen, (70, 70, 80), btn_screen)
    pygame.draw.rect(screen, (200, 200, 200), btn_screen, 2)
    # Icone simple pour l'écran (un rectangle ou des crochets)
    text_screen = font_btn.render("[]", True, WHITE)
    screen.blit(text_screen, (btn_screen.centerx - text_screen.get_width()//2, btn_screen.centery - text_screen.get_height()//2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()