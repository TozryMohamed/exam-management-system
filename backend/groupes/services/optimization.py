# groupes/services/optimization.py
from typing import List, Dict, Tuple
from ..models import GroupeEtudiant
from exams.models import Salle

class RepartitionOptimizer:
    """Optimiseur de répartition des étudiants"""
    
    def __init__(self, groupes: List[GroupeEtudiant], salles: List[Salle]):
        self.groupes = sorted(groupes, key=lambda g: g.effectif, reverse=True)
        self.salles = sorted(salles, key=lambda s: s.capacity, reverse=True)
    
    def get_statut_capacite(self, capacite_salle: int, effectif_groupe: int) -> Dict:
        """Retourne le statut d'occupation d'une salle"""
        pourcentage = (effectif_groupe / capacite_salle) * 100
        if effectif_groupe > capacite_salle:
            return {"status": "error", "icon": "❌", "message": "Dépassement de capacité"}
        elif pourcentage >= 90:
            return {"status": "warning", "icon": "⚠️", "message": f"Salle presque pleine ({pourcentage:.0f}%)"}
        elif pourcentage <= 50:
            return {"status": "info", "icon": "ℹ️", "message": f"Salle sous-utilisée ({pourcentage:.0f}%)"}
        else:
            return {"status": "success", "icon": "✅", "message": f"Occupation optimale ({pourcentage:.0f}%)"}
    
    def optimiser_repartition_simple(self) -> List[Dict]:
        """Algorithme simple: groupe + grand → salle + grande"""
        resultats = []
        groupes_restants = self.groupes.copy()
        salles_restantes = self.salles.copy()
        
        for groupe in groupes_restants:
            # Trouver la plus petite salle qui peut accueillir le groupe
            salle_trouvee = None
            for salle in salles_restantes:
                if salle.capacity >= groupe.effectif:
                    salle_trouvee = salle
                    break
            
            if salle_trouvee:
                resultats.append({
                    "groupe_id": groupe.id,
                    "groupe_nom": groupe.nom,
                    "effectif": groupe.effectif,
                    "salle_id": salle_trouvee.id,
                    "salle_nom": f"{salle_trouvee.type} {salle_trouvee.name}",
                    "capacite": salle_trouvee.capacity,
                    "statut": self.get_statut_capacite(salle_trouvee.capacity, groupe.effectif)
                })
                salles_restantes.remove(salle_trouvee)
            else:
                # Pas de salle assez grande
                resultats.append({
                    "groupe_id": groupe.id,
                    "groupe_nom": groupe.nom,
                    "effectif": groupe.effectif,
                    "salle_id": None,
                    "salle_nom": "Aucune salle disponible",
                    "capacite": 0,
                    "statut": {"status": "error", "icon": "❌", "message": "Aucune salle assez grande"}
                })
        
        return resultats
    
    def optimiser_repartition_avancee(self) -> List[Dict]:
        """Algorithme avancé: peut regrouper plusieurs groupes dans une même salle"""
        resultats = []
        groupes_restants = self.groupes.copy()
        salles_restantes = self.salles.copy()
        
        for salle in salles_restantes:
            capacite_restante = salle.capacity
            groupes_dans_salle = []
            
            # Prendre les plus petits groupes d'abord pour maximiser l'utilisation
            groupes_tries = sorted(groupes_restants, key=lambda g: g.effectif)
            
            for groupe in groupes_tries[:]:
                if groupe.effectif <= capacite_restante:
                    groupes_dans_salle.append(groupe)
                    capacite_restante -= groupe.effectif
                    groupes_restants.remove(groupe)
            
            if groupes_dans_salle:
                effectif_total = sum(g.effectif for g in groupes_dans_salle)
                resultats.append({
                    "salle_id": salle.id,
                    "salle_nom": f"{salle.type} {salle.name}",
                    "capacite": salle.capacity,
                    "effectif_total": effectif_total,
                    "places_restantes": capacite_restante,
                    "groupes": [
                        {
                            "groupe_id": g.id,
                            "groupe_nom": g.nom,
                            "effectif": g.effectif
                        } for g in groupes_dans_salle
                    ],
                    "statut": self.get_statut_capacite(salle.capacity, effectif_total)
                })
        
        # Groupes restants non assignés
        for groupe in groupes_restants:
            resultats.append({
                "salle_id": None,
                "salle_nom": "Non assigné",
                "capacite": 0,
                "effectif_total": groupe.effectif,
                "places_restantes": 0,
                "groupes": [{
                    "groupe_id": groupe.id,
                    "groupe_nom": groupe.nom,
                    "effectif": groupe.effectif
                }],
                "statut": {"status": "error", "icon": "❌", "message": "Non assigné"}
            })
        
        return resultats
    
    def suggerer_melange_etudiant(self) -> List[Dict]:
        """
        Suggère une répartition au niveau étudiant (préparation pour l'évolution future)
        Exemple: 15 GLSI + 15 ISI dans Salle 1, 20 TIC + 10 EEA dans Salle 2
        """
        total_etudiants = sum(g.effectif for g in self.groupes)
        resultats = []
        
        # Répartir les étudiants proportionnellement dans les salles
        for salle in self.salles:
            capacite_salle = salle.capacity
            if total_etudiants <= 0:
                break
                
            # Calculer le nombre d'étudiants à mettre dans cette salle
            proportion = min(1.0, capacite_salle / total_etudiants) if total_etudiants > 0 else 0
            effectif_salle = min(capacite_salle, total_etudiants)
            
            # Répartir les étudiants entre les groupes
            repartition_etudiants = []
            effectif_restant = effectif_salle
            for groupe in self.groupes:
                if effectif_restant <= 0:
                    break
                pris = min(groupe.effectif, effectif_restant)
                repartition_etudiants.append({
                    "groupe_nom": groupe.nom,
                    "effectif_groupe": groupe.effectif,
                    "effectif_assignes": pris
                })
                effectif_restant -= pris
            
            resultats.append({
                "salle_nom": f"{salle.type} {salle.name}",
                "capacite": salle.capacity,
                "effectif_total": effectif_salle,
                "taux_occupation": (effectif_salle / salle.capacity) * 100,
                "repartition": repartition_etudiants
            })
            total_etudiants -= effectif_salle
        
        return resultats