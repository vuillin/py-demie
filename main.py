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
font_btn = pygame.font.SysFont("Arial", 25, bold=True)
font_label = pygame.font.SysFont("Arial", 15, bold=True)

# --- SETUP ---
# 1. Génération de la Carte
game_map = Map(WIDTH, HEIGHT, POPULATION_SIZE)

# 2. Création de la Population
population = []
for _ in range(POPULATION_SIZE):
    # On récupère un point aléatoire valide (hors ville, hors supermarché)
    x, y = game_map.get_valid_spawn_point()
    
    # On crée la personne
    population.append(Person(x, y, game_map.city_rect))
    
    # On ajoute sa maison visuelle à cet endroit
    game_map.add_house(x, y)

# Variables de temps
current_hour = 6.0 
game_speed = 1.0 

# Variables Caméra
zoom = 1.0
min_zoom = 1.0
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

# --- BOUCLE DE JEU ---
running = True
while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
                mouse_pos = pygame.mouse.get_pos()
                if btn_slow.collidepoint(mouse_pos):
                    game_speed = max(0.5, game_speed - 0.5)
                elif btn_fast.collidepoint(mouse_pos):
                    game_speed = min(10.0, game_speed + 0.5)
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
    map_w_zoomed = WIDTH * zoom
    map_h_zoomed = HEIGHT * zoom
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

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()