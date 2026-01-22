import random
import math

class Job:
    """Interface de base pour un métier"""
    def apply_behavior(self, person, hour):
        pass

    def is_in_work_mode(self, person, hour):
        return False

class SupermarketManager:
    """Gère l'état global du supermarché (qui est aux caisses ?)"""
    def __init__(self, checkouts):
        self.checkouts = checkouts
        # Dict : {person_instance: checkout_index} (None si pas à la caisse)
        self.assignments = {} 

    def assign_checkout(self, person):
        """Assigne une caisse disponible ou force une si nécessaire"""
        # Si personne n'est assigné à une caisse, on force
        allocated_indices = [idx for idx in self.assignments.values() if idx is not None]
        
        if not allocated_indices and len(self.checkouts) > 0:
            # Force la caisse 0 si personne ne travaille
            target_idx = 0
            self.assignments[person] = target_idx
            return self.checkouts[target_idx]
        
        # Sinon, aléatoire : soit caisse libre, soit rayon
        # On va dire 50% de chance d'aller en caisse si dispo
        if random.random() < 0.5:
            # Chercher caisse libre
            free_indices = [i for i in range(len(self.checkouts)) if i not in allocated_indices]
            if free_indices:
                idx = random.choice(free_indices)
                self.assignments[person] = idx
                return self.checkouts[idx]
        
        # Sinon rayon (None)
        self.assignments[person] = None
        return None

    def release_checkout(self, person):
        if person in self.assignments:
             del self.assignments[person]


class SupermarketJob(Job):
    def __init__(self, manager, store_rect):
        self.manager = manager
        self.store_rect = store_rect
        self.current_state = "IDLE" # CHECKOUT, WANDER, IDLE
        self.current_target = None
        self.wait_timer = 0 # Compteur pour les pauses (frames)

    def apply_behavior(self, person, hour):
        # Pendant les heures de travail (7h-20h), ils sont au magasin
        if 7 <= hour < 20: 
            # PHASE 1 : TRAJET VERS LE MAGASIN
            # Si on n'est pas encore attribué (IDLE) et qu'on est loin
            if self.current_state == "IDLE":
                if not self.store_rect.collidepoint(person.x, person.y):
                     # On va vers le magasin
                     person.final_target = self.store_rect.center
                     person.speed = person.base_speed
                     return
                else:
                    # On est arrivé ! On prend notre poste pour la journée
                    checkout_pos = self.manager.assign_checkout(person)
                    if checkout_pos:
                        self.current_state = "CHECKOUT"
                        self.current_target = checkout_pos
                    else:
                        self.current_state = "WANDER"
                        self.current_target = self._pick_random_spot()

            # PHASE 2 : DANS LE MAGASIN (AU TRAVAIL)
            if self.current_state == "CHECKOUT":
                 # On reste planté à la caisse
                 person.final_target = self.current_target
                 person.speed = person.base_speed # Vitesse normale pour y aller (ou O une fois sur place mais le update gère)
            
            elif self.current_state == "WANDER":
                 # GESTION DE LA PAUSE
                 if self.wait_timer > 0:
                     self.wait_timer -= 1
                     person.speed = 0 # On s'arrête
                     person.final_target = (person.x, person.y) # On fige EXACTEMENT sur place
                     return # On ne fait rien d'autre

                 # On se balade LENTEMENT
                 person.speed = person.base_speed * 0.4 
                 
                 # Si on a atteint la cible, on change
                 dist = math.hypot(self.current_target[0] - person.x, self.current_target[1] - person.y)
                 if dist < 10:
                     # On lance une pause de 2 à 4 secondes (120 à 240 frames à 60 FPS)
                     self.wait_timer = random.randint(120, 240)
                     self.current_target = self._pick_random_spot()

                 person.final_target = self.current_target

        else:
            # Fin de journée / Matin
            if self.current_state != "IDLE":
                self.manager.release_checkout(person)
                self.current_state = "IDLE"
                self.current_target = None
            
            # Rentrer à la maison
            person.final_target = person.home
            person.speed = person.base_speed

    def _pick_random_spot(self):
        rx = random.randint(self.store_rect.left + 20, self.store_rect.right - 20)
        ry = random.randint(self.store_rect.top + 20, self.store_rect.bottom - 20)
        return (rx, ry)

    def is_in_work_mode(self, person, hour):
        # On désactive le GPS si on est dans le magasin pendant les heures de travail
        if 7 <= hour < 20: 
            if self.store_rect.collidepoint(person.x, person.y):
                # On est dedans, on bouge localement -> Pas de GPS
                return True
        return False


class MedicalJob(Job):
    def __init__(self, medical_rect):
        self.medical_rect = medical_rect
        self.current_target = None
        self.wait_timer = 0
    
    def apply_behavior(self, person, hour):
        # Horaires : 7h - 20h
        if 7 <= hour < 20:
            if not self.medical_rect.collidepoint(person.x, person.y):
                # Aller au travail
                person.final_target = self.medical_rect.center
                person.speed = person.base_speed
                return
            
            # Dans le centre médical : Balade avec pauses
            if self.wait_timer > 0:
                self.wait_timer -= 1
                person.speed = 0
                person.final_target = (person.x, person.y)
                return

            person.speed = person.base_speed * 0.4
            
            # Si pas de cible ou atteinte
            dist_to_target = 0
            if self.current_target:
                dist_to_target = math.hypot(self.current_target[0] - person.x, self.current_target[1] - person.y)
            
            if not self.current_target or dist_to_target < 10:
                self.wait_timer = random.randint(120, 240)
                # Nouvelle cible aléatoire dans le rect
                rx = random.randint(self.medical_rect.left + 10, self.medical_rect.right - 10)
                ry = random.randint(self.medical_rect.top + 10, self.medical_rect.bottom - 10)
                self.current_target = (rx, ry)
            
            person.final_target = self.current_target
        
        else:
            # Rentrer
            person.final_target = person.home
            person.speed = person.base_speed

    def is_in_work_mode(self, person, hour):
        if 7 <= hour < 20:
            if self.medical_rect.collidepoint(person.x, person.y):
                return True
        return False
