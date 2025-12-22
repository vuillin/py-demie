import pygame
import random
from settings import *
from . import data
from . import generators
from . import renderer

class Map:
    def __init__(self, width, height, population_size):
        self.width = width
        self.height = height
        
        # 1. La Ville

        self.city_w = 300 
        self.city_h = 240
        offset_y = 30

        self.city_rect = pygame.Rect(
            (width // 2 - self.city_w // 2, (height // 2 - self.city_h // 2) + offset_y), 
            (self.city_w, self.city_h)
        )
        
        # Listes de données
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
        self.grass_tiles = generators.generate_grass(width, height)
        self.city_elements = generators.generate_city_architecture(self.city_rect, self.city_w, self.city_h)
        self.supermarket = generators.generate_fixed_supermarket(width, height)
        self.medical_center = generators.generate_medical_center()
        self.sports_complex = generators.generate_sports_complex(width)

        self.roads = []
        self._build_roads()

        self._define_house_slots()
        self._define_vegetation_slots()

    def _build_roads(self):
        self.roads = data.get_road_network()

    def _define_house_slots(self):
        """
        Définit les positions exactes des 250 maisons.
        """
        self.house_slots = data.get_house_slots()

    def _define_vegetation_slots(self):
        """
        Définit les positions de la végétation.
        """
        veg_data = data.get_vegetation_slots()
        self.manual_trees_1 = veg_data["trees_1"]
        self.manual_trees_2 = veg_data["trees_2"]
        self.manual_bushes = veg_data["bushes"]
        self.manual_flowers = veg_data["flowers"]

    def get_valid_spawn_point(self):
        """Distribue les places définies une par une"""
        if self.house_slots:
            return self.house_slots.pop(0) # On prend la première dispo et on l'enlève
        else:
            # Sécurité si ta liste est plus courte que la population
            return random.randint(20, self.width), random.randint(20, self.height)

    def add_house(self, x, y):
        self.houses.append(generators.create_house_parts(x, y))

    def draw(self, screen, zoom, pan_x, pan_y, label_font):
        renderer.draw_map(self, screen, zoom, pan_x, pan_y, label_font)
