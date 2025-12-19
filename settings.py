
# Dimensions de l'écran 
WIDTH = 1200 
HEIGHT = 800
FPS = 60

# Couleurs RGB
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)     # Obstacles
ORANGE = (230, 120, 0)  # La ville (bordure)
BLUE = (50, 100, 200)   # Homme
PINK = (220, 100, 180)  # Femme
RED = (255, 50, 50)     
ROAD_COLOR = (45, 45, 55)
BG_COLOR = (20, 20, 25) 

# --- PALETTE DE COULEURS MAISONS ---
C_BEIGE = (230, 210, 170)
C_BRICK = (160, 80, 60)
C_GREY  = (180, 180, 190)
C_DARK  = (50, 50, 60)
C_RED   = (180, 60, 60)
C_BLUE  = (100, 180, 220) # Pour les vitres
C_WOOD  = (100, 70, 40)   # Pour les portes
HOUSE_SIZE = 14 

# --- DECOR HERBE ---
C_GRASS_1 = (120, 160, 120)
C_GRASS_2 = (110, 150, 110)

# --- SUPERMARCHÉ ---
C_SM_WALL = (100, 120, 140)  
C_SM_ROOF = (70, 80, 90)     
C_SM_GLASS = (160, 210, 250) 
C_SM_SIGN = (220, 60, 60) 
C_SM_FLOOR = (220, 220, 230)
C_SM_FLOOR_ALT = (200, 200, 210)
C_SM_SHELF = (60, 80, 100)    
C_SM_PRODUCT = (200, 200, 200)
C_SM_CHECKOUT = (40, 40, 40)  
C_SM_DESK = (180, 180, 190)   
SM_SIZE = (220, 140) 

# --- CENTRE MÉDICAL ---
MC_SIZE = (160, 110)          
C_MC_FLOOR = (255, 255, 255)
C_MC_FLOOR_ALT = (240, 240, 240)
C_MC_WALL = (150, 160, 170)   
C_MC_CROSS = (230, 60, 60)    
C_MC_BED = (100, 200, 220)    
C_MC_FURNITURE = (200, 200, 210)

# --- COMPLEXE SPORTIF ---
SC_SIZE = (180, 140)
C_SC_GROUND = (200, 200, 200)   
C_SC_TRACK = (205, 92, 92)      
C_SC_GRASS = (60, 160, 60)      
C_SC_GRASS_DARK = (50, 140, 50) 
C_SC_LINES = (240, 240, 240)    
C_SC_WATER = (30, 144, 255)    
C_SC_LANE = (100, 180, 255)     
C_SC_SEATS = (100, 100, 120)    

# --- VÉGÉTATION ---
# Arbre Type 1
TREE_1_RADIUS = 10
C_TREE_1_TOP = (60, 180, 60)
C_TREE_1_BASE = (30, 120, 30)

# Arbre Type 2 (Sombre - Type Pin/Sapin)
TREE_2_RADIUS = 10
C_TREE_2_TOP = (40, 100, 50)   
C_TREE_2_BASE = (30, 80, 40) 

# Buissons
BUSH_RADIUS = 5
C_BUSH_MAIN = (100, 180, 40)    
C_BUSH_LIGHT = (140, 220, 80)

# Parterre de Fleurs
FLOWERBED_SIZE = (24, 12)      
C_SOIL = (100, 70, 40)         
C_FLOWER_RED = (200, 50, 50)
C_FLOWER_YEL = (220, 220, 50)
C_FLOWER_PRP = (150, 50, 150)

# --- BOSQUETS (Groupes d'arbres) ---
GROVE_TREE_COUNT = 6 
GROVE_SPREAD = 20      

# Paramètres de la simulation 
POPULATION_SIZE = 213
FRAGILITY_RATE = 0.05
BASE_CLOCK_SPEED = 0.005  
BASE_WALK_SPEED = 1
HOUSE_MARGIN = 5