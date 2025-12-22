import math
import heapq

class NavigationGraph:
    def __init__(self):
        # 1. DÉFINITION DES NOEUDS
        self.nodes = {
            "A": (594, 281),
            "B": (717, 417),
            "C": (599, 518),
            "D": (481, 400),
            "E": (598, 262),
            "F": (775, 263),
            "G": (780, 398),
            "H": (778, 544),
            "I": (605, 551),
            "J": (437, 549),
            "K": (428, 381),
            "L": (420, 261)
        }

        # 2. DÉFINITION DES CONNEXIONS 
        # Format : ("Point1", "Point2")
        self.connections = [
            # L'Anneau extérieur
            ("L", "E"), ("E", "F"), ("F", "G"), ("G", "H"),
            ("H", "I"), ("I", "J"), ("J", "K"), ("K", "L"),
            
            # Les Rayons (Spokes) vers l'intérieur
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