import pygame
import random
from settings import *
from person import Person

# Initialisation Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Py-Démie")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

# --- SETUP ---

# Définition de la ville (carré central)
city_size = 200
city_rect = pygame.Rect((WIDTH//2 - city_size//2, HEIGHT//2 - city_size//2), (city_size, city_size))

# Création de la population
population = []
for _ in range(POPULATION_SIZE):
    # Position de départ aléatoire (Hors de la ville)
    while True:
        x = random.randint(20, WIDTH - 20)
        y = random.randint(20, HEIGHT - 20)
        # On s'assure qu'ils ne spawnent pas dans la ville au début
        if not city_rect.collidepoint(x, y):
            break

    population.append(Person(x, y, city_rect))

# Variables de temps
current_hour = 6.0 # On commence à 6h du mat

# --- BOUCLE DE JEU ---
running = True
while running:
    # 1. Gestion des événements (clavier/souris)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # 2. Mise à jour des données 
    current_hour += 0.05 * TIME_SPEED
    if current_hour >= 24:
        current_hour = 0

    for person in population:
        person.update(current_hour)

    # 3. Affichage 
    screen.fill(BG_COLOR)

    # Dessiner la ville
    pygame.draw.rect(screen, (30, 30, 40), city_rect) # Fond ville
    pygame.draw.rect(screen, ORANGE, city_rect, 2) # Bordure ville

    # Dessiner les gens 
    for person in population:
        person.draw(screen)

    # Afficher l'heure 
    time_text = font.render(f"Heure: {int(current_hour)}h", True, WHITE)
    screen.blit(time_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()