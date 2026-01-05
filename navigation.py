import math
import heapq

class NavigationGraph:
    def __init__(self):
        # 1. DÉFINITION DES NOEUDS
        self.nodes = {
            "A": (596, 311),
            "B": (747, 431),
            "C": (583, 548),
            "D": (450, 432),
            "E": (596, 282),
            "F": (785, 282),
            "G": (785, 431),
            "H": (785, 573),
            "I": (583, 573),
            "J": (415, 573),
            "K": (415, 432),
            "L": (415, 282),
            "M": (415, 689),
            "N": (490, 689),
            "O": (785, 690),
            "P": (709, 690),
            "Q": (232, 432),
            "R": (232, 209),
            "S": (832, 282),
            "T": (832, 166),
            "U": (868, 166),
            "V": (415,770),
            "W": (285,770),
            "X": (165,770),
            "Y": (25,770),
            "Z": (60,770),
            "A1": (60, 660),
            "B1": (415, 660),
            "C1": (232, 390),
            "D1": (50, 390),
            "E1": (50, 485),
            "F1": (180, 485),
            "G1": (180, 660),
            "H1": (232, 485),
            "I1": (180, 575),
            "J1": (300, 660),
            "K1": (832, 248),
            "L1": (987, 248),
            "M1": (923, 248),
            "N1": (923, 340),
            "O1": (785, 340),
            "P1": (920, 431),
            "Q1": (890, 490),
            "R1": (785, 490)

        }

        # 2. DÉFINITION DES CONNEXIONS 
        self.connections = [
            ("L", "E"), ("E", "F"),
            ("H", "I"), ("I", "J"), ("J", "K"), ("K", "L"),
            ("M", "N"),("H", "O"),("O", "P"),
            ("Q", "K"),
            ("F", "S"),("T", "U"),
            ("M", "V"),("V", "W"),("W", "X"),
            ("X", "Z"),("Z", "Y"),("Z", "A1"),("B1", "M"),("B1", "J"),
            ("A1", "G1"),("A1", "G1"),("F1", "H1"),("H1", "Q"),
            ("Q", "C1"),("C1", "R"),("E1", "F1"),("E1", "D1"),("D1", "C1"),
            ("G1", "I1"),("I1", "F1"),("G1", "J1"),("J1", "B1"),
            ("S", "K1"), ("K1", "T"), ("K1", "M1"), ("M1", "L1"),("M1", "N1"),
            ("G", "O1"), ("O1", "F"), ("O1", "N1"),
            ("P1", "G"), ("R1", "Q1"), ("H", "R1"), ("R1", "G"),
            
            ("A", "E"), # Nord
            ("B", "G"), # Est
            ("C", "I"), # Sud
            ("D", "K")  # Ouest
        ]

        # 3. CONSTRUCTION DU GRAPHE
        self.graph = {node: {} for node in self.nodes}
        self._build_graph()

    def _dist(self, p1, p2):
        """Calcul distance pythagore simple"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _build_graph(self):
        """Remplit le graphe avec les voisins et le coût (distance) de chaque route"""
        for n1, n2 in self.connections:
            d = self._dist(self.nodes[n1], self.nodes[n2])
            # C'est une route à double sens, on ajoute dans les deux directions
            self.graph[n1][n2] = d
            self.graph[n2][n1] = d

    def get_closest_node(self, pos):
        """Trouve le point noir le plus proche d'une position donnée (x, y)"""
        closest_node = None
        min_dist = float('inf')
        
        for node_id, node_pos in self.nodes.items():
            d = self._dist(pos, node_pos)
            if d < min_dist:
                min_dist = d
                closest_node = node_id
        
        return closest_node

    def get_shortest_path(self, start_node, end_node):
        """
        ALGORITHME DE DIJKSTRA
        Trouve la suite de points la plus courte entre deux noeuds du réseau.
        """
        # File d'attente prioritaire : (coût_total, noeud_actuel)
        queue = [(0, start_node)]
        distances = {node: float('inf') for node in self.nodes}
        distances[start_node] = 0
        came_from = {node: None for node in self.nodes} # Pour reconstruire le chemin

        while queue:
            current_dist, current_node = heapq.heappop(queue)

            # Si on est arrivé, on arrête
            if current_node == end_node:
                break

            # Si on a trouvé un chemin plus long que ce qu'on connait déjà, on ignore
            if current_dist > distances[current_node]:
                continue

            # On regarde les voisins
            for neighbor, weight in self.graph[current_node].items():
                distance = current_dist + weight
                
                # Si on a trouvé un raccourci vers ce voisin
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    came_from[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

        # Reconstruction du chemin (en partant de la fin)
        path = []
        curr = end_node
        if came_from[curr] is None and curr != start_node:
            return [] # Pas de chemin trouvé (impossible ici mais bon)
            
        while curr:
            path.append(self.nodes[curr]) # On ajoute les coordonnées
            curr = came_from[curr]
        
        path.reverse() # On remet dans le bon sens
        return path

    def calculate_route(self, start_pos, end_pos):
        """
        FONCTION PRINCIPALE
        Calcule tout le trajet : Position -> Entrée Réseau -> Chemin -> Sortie Réseau -> Destination
        """
        # 1. Trouver l'entrée et la sortie du réseau
        node_entry = self.get_closest_node(start_pos)
        node_exit = self.get_closest_node(end_pos)

        # 2. Calculer le chemin sur le réseau
        network_path = self.get_shortest_path(node_entry, node_exit)

        # 3. Assembler le tout
        full_route = []

        full_route.extend(network_path)
        
        # destination finale
        full_route.append(end_pos)

        return full_route