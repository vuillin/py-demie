import pygame
from settings import *
from person import Person
from map import Map

# Initialisation
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Py-Démie")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

# --- SETUP ---

# 1. Génération de la Carte
game_map = Map(WIDTH, HEIGHT, POPULATION_SIZE)

# 2. Création de la Population
population = []
for _ in range(POPULATION_SIZE):
    x, y = game_map.get_valid_spawn_point()
    population.append(Person(x, y, game_map.city_rect))
    game_map.add_house(x, y)

# Variables de temps
current_hour = 6.0 

# --- VARIABLES CAMERA / ZOOM ---
zoom = 1.0
min_zoom = 1.0
max_zoom = 4.0
zoom_speed = 0.1

# Variables de déplacement (Pan)
pan_x = 0
pan_y = 0
is_panning = False # Est-ce qu'on est en train de déplacer la map ?
last_mouse_pos = (0, 0)

# --- BOUCLE DE JEU ---
running = True
while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # A. GESTION DU ZOOM (Vers la souris)
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # 1. Où est la souris dans le "Monde" AVANT de zoomer ?
            # Formule inverse : World = (Screen - Pan) / Zoom
            world_x = (mouse_x - pan_x) / zoom
            world_y = (mouse_y - pan_y) / zoom
            
            # 2. On change le zoom
            zoom += event.y * zoom_speed
            zoom = max(min_zoom, min(max_zoom, zoom))
            
            # 3. On recalcule le Pan pour que le point sous la souris reste au même endroit
            # Formule : Pan = Screen - (World * NouveauZoom)
            pan_x = mouse_x - (world_x * zoom)
            pan_y = mouse_y - (world_y * zoom)

        # B. GESTION DU DÉPLACEMENT (Clic Gauche maintenu)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic gauche enfoncé
                is_panning = True
                last_mouse_pos = pygame.mouse.get_pos()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Clic gauche relâché
                is_panning = False
                
        elif event.type == pygame.MOUSEMOTION:
            if is_panning:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # On calcule de combien la souris a bougé
                dx = mouse_x - last_mouse_pos[0]
                dy = mouse_y - last_mouse_pos[1]
                
                # On applique ce mouvement à la caméra
                pan_x += dx
                pan_y += dy
                
                last_mouse_pos = (mouse_x, mouse_y)

    # --- CLAMPING (Garde-fou) ---
    # Pour éviter de perdre la map si on déplace trop loin
    # On s'assure qu'on voit toujours au moins un bout de la map
    # (Logique simple : on ne peut pas aller plus loin que les bords * zoom)
    # Tu peux commenter ces lignes si tu veux une liberté totale
    map_w_zoomed = WIDTH * zoom
    map_h_zoomed = HEIGHT * zoom
    pan_x = min(0, max(pan_x, WIDTH - map_w_zoomed))
    pan_y = min(0, max(pan_y, HEIGHT - map_h_zoomed))

    # 2. Update
    current_hour += 0.05 * TIME_SPEED
    if current_hour >= 24:
        current_hour = 0

    for person in population:
        person.update(current_hour)

    # 3. Draw
    screen.fill(BG_COLOR)

    # A. On dessine la map
    game_map.draw(screen, zoom, pan_x, pan_y)

    # B. On dessine les gens
    for person in population:
        person.draw(screen, zoom, pan_x, pan_y)

    # C. UI
    time_text = font.render(f"Heure: {int(current_hour)}h", True, WHITE)
    screen.blit(time_text, (10, 10))
    
    zoom_text = font.render(f"Zoom: x{zoom:.1f}", True, WHITE)
    screen.blit(zoom_text, (10, 35))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()