
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q, Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from .models import GroupeEtudiant, RepartitionExamen, RepartitionDetail
from .serializers import (
    GroupeEtudiantSerializer, RepartitionExamenSerializer, RepartitionDetailSerializer
)
from exams.models import Exam, Salle
from users.models import User
import math
import random
from collections import defaultdict
import traceback
import re

# ============================================================
# Générateur de places (sièges)
# ============================================================
class SeatGenerator:
    def __init__(self, capacity):
        self.capacity = capacity
        self.seats = self._generate_all_seats()
        random.shuffle(self.seats)
        self.current_index = 0

    def _generate_all_seats(self):
        seats = []
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        seats_per_row = math.ceil(self.capacity / len(rows))
        for row in rows:
            for num in range(1, seats_per_row + 1):
                seat = f"{row}{num}"
                seats.append(seat)
                if len(seats) >= self.capacity:
                    break
            if len(seats) >= self.capacity:
                break
        return seats

    def get_next_seat(self):
        if self.current_index < len(self.seats):
            seat = self.seats[self.current_index]
            self.current_index += 1
            return seat
        return None


# ============================================================
# API : mélange à partir d'IDs d'étudiants
# ============================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def melange_avec_etudiants_reels(request):
    try:
        etudiants_ids = request.data.get("etudiants", [])
        examens_ids = request.data.get("examens", [])
        
        if not etudiants_ids or not examens_ids:
            return Response({
                "success": False,
                "message": "❌ Veuillez sélectionner des étudiants et des examens"
            }, status=400)

        examens = Exam.objects.filter(id__in=examens_ids)
        etudiants = User.objects.filter(id__in=etudiants_ids, role="etudiant")
        
        if not etudiants.exists():
            return Response({"success": False, "message": "❌ Aucun étudiant trouvé"}, status=404)
        
        # 🔑 CONSTRUIRE LE MAPPING ÉTUDIANT → EXAMEN
        # Chaque étudiant doit savoir à quel examen il appartient
        mapping_etudiant_exam = {}
        etudiant_objets = {}  # Cache pour retrouver l'objet User
        
        for etudiant in etudiants:
            etudiant_objets[etudiant.id] = etudiant
            # Par défaut, l'étudiant n'est associé à aucun examen encore
        
        # IMPORTANT: Assigner chaque étudiant à son examen de rattachement
        # Un étudiant peut correspondre à plusieurs examens, on prend le premier
        for examen in examens:
            # Filtrer les étudiants qui correspondent à cet examen
            # (La logique de filtrage est normalement gérée côté frontend)
            for etudiant in etudiants:
                if etudiant.id in etudiants_ids:
                    mapping_etudiant_exam[etudiant.id] = examen.id
        
        # Regrouper les examens par DATE + HEURE (période identique)
        examens_par_periode = defaultdict(list)
        
        for examen in examens:
            date_key = examen.date if examen.date else "sans_date"
            time_key = "sans_heure"
            if examen.time:
                time_str = str(examen.time)
                time_key = time_str.split(':')[0] if ':' in time_str else "sans_heure"
            periode_key = f"{date_key}_{time_key}"
            examens_par_periode[periode_key].append(examen)
        
        tous_les_resultats = []
        total_etudiants_global = 0
        total_salles_global = 0
        
        for periode_key, examens_groupe in examens_par_periode.items():
            parts = periode_key.split('_')
            date_part = parts[0] if len(parts) > 0 else "sans_date"
            time_part = parts[1] if len(parts) > 1 else "sans_heure"
            
            # Tous les étudiants de cette période (ils sont déjà filtrés par le frontend)
            etudiants_periode = etudiants
            
            # Collecter toutes les salles de tous les examens du groupe
            salles_ids = set()
            for examen in examens_groupe:
                if examen.salle_id:
                    salles_ids.add(examen.salle_id)
            
            salles = Salle.objects.filter(id__in=salles_ids)
            
            if not salles.exists():
                tous_les_resultats.append({
                    "periode": periode_key,
                    "date": date_part,
                    "heure": time_part,
                    "success": False,
                    "message": "❌ Aucune salle disponible"
                })
                continue
            
            total_etudiants = etudiants_periode.count()
            capacite_totale = sum(s.capacity for s in salles)
            
            if capacite_totale < total_etudiants:
                tous_les_resultats.append({
                    "periode": periode_key,
                    "date": date_part,
                    "heure": time_part,
                    "success": False,
                    "message": f"❌ Capacité insuffisante: {capacite_totale} places pour {total_etudiants} étudiants"
                })
                continue
            
            # 🔑 MÉLANGE ROUND-ROBIN ENTRE TOUS LES ÉTUDIANTS
            etudiants_list = list(etudiants_periode)
            random.shuffle(etudiants_list)
            salles_list = list(salles)
            random.shuffle(salles_list)
            
            # Distribution équilibrée entre toutes les salles
            distribution = {salle.id: [] for salle in salles_list}
            capacites_restantes = {salle.id: salle.capacity for salle in salles_list}
            
            index_salle = 0
            for etudiant in etudiants_list:
                placed = False
                for _ in range(len(salles_list)):
                    salle = salles_list[index_salle % len(salles_list)]
                    if capacites_restantes[salle.id] > 0:
                        distribution[salle.id].append(etudiant)
                        capacites_restantes[salle.id] -= 1
                        placed = True
                        index_salle += 1
                        break
                    index_salle += 1
                
                if not placed:
                    tous_les_resultats.append({
                        "periode": periode_key,
                        "date": date_part,
                        "heure": time_part,
                        "success": False,
                        "message": "❌ Erreur de placement: capacité insuffisante"
                    })
                    break
            
            # Construire les données des salles avec les infos de chaque étudiant
            salles_data = []
            for salle in salles_list:
                etudiants_dans_salle = distribution.get(salle.id, [])
                if not etudiants_dans_salle:
                    continue
                
                seat_gen = SeatGenerator(salle.capacity)
                etudiants_avec_places = []
                groupes_stats = {}
                
                for etudiant in etudiants_dans_salle:
                    # Informations du groupe de l'étudiant
                    groupe_nom = "Sans groupe"
                    if hasattr(etudiant, 'studentprofile') and etudiant.studentprofile and etudiant.studentprofile.groupe:
                        if hasattr(etudiant.studentprofile.groupe, 'nom'):
                            groupe_nom = etudiant.studentprofile.groupe.nom
                        elif hasattr(etudiant.studentprofile.groupe, 'name'):
                            groupe_nom = etudiant.studentprofile.groupe.name
                    
                    groupes_stats[groupe_nom] = groupes_stats.get(groupe_nom, 0) + 1
                    place = seat_gen.get_next_seat()
                    
                    # 🔑 AJOUTER exam_id POUR CHAQUE ÉTUDIANT
                    # Cela permet de savoir à quel examen appartient chaque étudiant
                    exam_id = mapping_etudiant_exam.get(etudiant.id, examens_groupe[0].id)
                    exam_title = examens_groupe[0].title
                    
                    # Chercher le titre exact de l'examen
                    for ex in examens_groupe:
                        if ex.id == exam_id:
                            exam_title = ex.title
                            break
                    
                    etudiants_avec_places.append({
                        "id": etudiant.id,
                        "exam_id": exam_id,  # 🔑 NOUVEAU: ID de l'examen de rattachement
                        "exam_title": exam_title,  # 🔑 NOUVEAU: Titre de l'examen
                        "nom": f"{etudiant.first_name} {etudiant.last_name}".strip() or etudiant.username,
                        "place": place if place else "?"
                    })
                
                salles_data.append({
                    "salle_id": salle.id,
                    "salle_nom": f"{salle.type} {salle.name}",
                    "capacite": salle.capacity,
                    "effectif": len(etudiants_dans_salle),
                    "etudiants": etudiants_avec_places,
                    "groupes_stats": groupes_stats,
                    "taux_occupation": (len(etudiants_dans_salle) / salle.capacity) * 100 if salle.capacity > 0 else 0
                })
            
            type_regroupement = "melange" if len(examens_groupe) >= 2 else "simple"
            total_etudiants_global += total_etudiants
            total_salles_global += len(salles_data)
            
            tous_les_resultats.append({
                "periode": periode_key,
                "date": date_part,
                "heure": time_part,
                "success": True,
                "type": type_regroupement,
                "message": f"{'🎲 Mélange' if len(examens_groupe) >= 2 else '📝 Simple'} pour {len(examens_groupe)} examen(s)",
                "examens": [{"id": e.id, "title": e.title} for e in examens_groupe],
                "total_etudiants": total_etudiants,
                "total_salles": len(salles_data),
                "salles": salles_data
            })
        
        return Response({
            "success": True,
            "message": f"✅ Répartition terminée pour {total_etudiants_global} étudiants",
            "total_etudiants": total_etudiants_global,
            "total_salles": total_salles_global,
            "groupes_par_periode": tous_les_resultats,
            "salles": [salle for resultat in tous_les_resultats if resultat.get("success") for salle in resultat.get("salles", [])]
        })
        
    except Exception as e:
        traceback.print_exc()
        return Response({"success": False, "message": f"Erreur serveur : {str(e)}"}, status=500)


# ============================================================
# API : mélange intelligent (pour compatibilité)
# ============================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def melange_intelligent(request):
    try:
        groupes_ids = request.data.get("groupes", [])
        salles_ids = request.data.get("salles", [])
        
        if not groupes_ids or not salles_ids:
            return Response({"success": False, "message": "❌ Groupes et salles requis"}, status=400)
        
        groupes = GroupeEtudiant.objects.filter(id__in=groupes_ids)
        salles = Salle.objects.filter(id__in=salles_ids)
        
        if not groupes.exists():
            return Response({"success": False, "message": "❌ Aucun groupe trouvé"}, status=404)
        
        if not salles.exists():
            return Response({"success": False, "message": "❌ Aucune salle trouvée"}, status=404)
        
        total_etudiants = sum(g.effectif for g in groupes)
        capacite_totale = sum(s.capacity for s in salles)
        
        if capacite_totale < total_etudiants:
            return Response({
                "success": False,
                "message": f"❌ Capacité insuffisante"
            }, status=400)
        
        return Response({
            "success": True,
            "message": "✅ Analyse terminée",
            "total_etudiants": total_etudiants,
            "total_salles": len(salles)
        })
        
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)


# ============================================================
# API : appliquer le mélange (sauvegarde) - VERSION CORRIGÉE
# ============================================================
# groups/views.py - REMPLACER la fonction appliquer_melange

# groups/views.py - REMPLACER la fonction appliquer_melange

# groups/views.py - REMPLACER la fonction appliquer_melange

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def appliquer_melange(request):
    try:
        print("=" * 60)
        print("🔵 [appliquer_melange] Début de la sauvegarde")
        
        examen_id = request.data.get("examen_id")
        salles_data = request.data.get("salles", [])
        
        if not examen_id:
            return Response({"success": False, "message": "❌ ID examen requis"}, status=400)
        
        try:
            examen = Exam.objects.get(id=examen_id)
            print(f"🔵 Examen: {examen.title} (ID: {examen.id})")
        except Exam.DoesNotExist:
            return Response({"success": False, "message": "❌ Examen non trouvé"}, status=404)
        
        total_crees = 0
        total_places = 0
        
        # Traiter chaque salle
        for salle_data in salles_data:
            salle_id = salle_data.get("salle_id")
            etudiants_data = salle_data.get("etudiants", [])
            
            if not salle_id or not etudiants_data:
                continue
            
            try:
                salle = Salle.objects.get(id=salle_id)
                print(f"🔵 Salle: {salle.name} (ID: {salle.id}) - {len(etudiants_data)} étudiants")
            except Salle.DoesNotExist:
                print(f"⚠️ Salle {salle_id} non trouvée, ignorée")
                continue
            
            # 🔑 Filtrer uniquement les étudiants de CET examen
            etudiants_examen = [
                e for e in etudiants_data 
                if e.get("exam_id") == examen.id
            ]
            
            if not etudiants_examen:
                print(f"⚠️ Aucun étudiant de l'examen {examen.title} dans la salle {salle.name}")
                continue
            
            print(f"🔵 Étudiants de l'examen {examen.title} dans la salle {salle.name}: {len(etudiants_examen)}")
            
            # 🔑 RÉCUPÉRER LE VRAI GROUPE DES ÉTUDIANTS
            groupe_etudiant = None
            for etudiant_data in etudiants_examen:
                user_id = etudiant_data.get("id")
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        if hasattr(user, 'studentprofile') and user.studentprofile:
                            if user.studentprofile.groupe:
                                # Vérifier si c'est un objet GroupeEtudiant ou autre
                                groupe_obj = user.studentprofile.groupe
                                # Essayer d'obtenir le nom
                                if hasattr(groupe_obj, 'nom'):
                                    groupe_nom = groupe_obj.nom
                                    groupe_etudiant = groupe_obj
                                    print(f"🔵 Groupe trouvé: {groupe_nom} (ID: {groupe_obj.id})")
                                    break
                                elif hasattr(groupe_obj, 'name'):
                                    # C'est un objet avec 'name' au lieu de 'nom'
                                    # Chercher ou créer un GroupeEtudiant correspondant
                                    groupe_nom = groupe_obj.name
                                    groupe_etudiant, created = GroupeEtudiant.objects.get_or_create(
                                        nom=groupe_nom,
                                        defaults={"effectif": 0, "niveau": examen.niveau or "L0"}
                                    )
                                    print(f"🔵 Groupe converti: {groupe_etudiant.nom} (ID: {groupe_etudiant.id})")
                                    break
                    except User.DoesNotExist:
                        pass
            
            # Si aucun groupe trouvé, créer un groupe basé sur le niveau de l'examen
            if not groupe_etudiant:
                niveau_examen = examen.niveau or "L0"
                groupe_etudiant, created = GroupeEtudiant.objects.get_or_create(
                    nom=f"Niveau {niveau_examen}",
                    defaults={"effectif": 0, "niveau": niveau_examen}
                )
                print(f"⚠️ Groupe créé par défaut: {groupe_etudiant.nom}")
            
            # 🔑 VÉRIFIER SI LA RÉPARTITION EXISTE DÉJÀ
            repartition = RepartitionExamen.objects.filter(
                examen=examen,
                salle=salle
            ).first()
            
            if repartition:
                # Mise à jour de la répartition existante
                print(f"🔄 Mise à jour de la répartition existante (ID: {repartition.id})")
                repartition.effectif = len(etudiants_examen)
                repartition.groupe = groupe_etudiant
                repartition.save()
            else:
                # Création d'une nouvelle répartition
                repartition = RepartitionExamen.objects.create(
                    examen=examen,
                    groupe=groupe_etudiant,
                    salle=salle,
                    effectif=len(etudiants_examen)
                )
                total_crees += 1
                print(f"✅ Nouvelle répartition créée avec groupe {groupe_etudiant.nom} (ID: {repartition.id})")
            
            # Supprimer les anciens détails
            RepartitionDetail.objects.filter(repartition=repartition).delete()
            
            # Créer les nouveaux détails
            details_a_creer = []
            for i, etudiant_data in enumerate(etudiants_examen):
                user_id = etudiant_data.get("id")
                place = etudiant_data.get("place", "?")
                
                if not user_id:
                    continue
                
                if isinstance(user_id, str):
                    try:
                        user_id = int(user_id)
                    except ValueError:
                        print(f"⚠️ ID étudiant invalide: {user_id}")
                        continue
                
                details_a_creer.append(
                    RepartitionDetail(
                        repartition=repartition,
                        user_id=user_id,
                        place_number=i + 1,
                        seat_code=place,
                        student_index=i
                    )
                )
            
            if details_a_creer:
                RepartitionDetail.objects.bulk_create(details_a_creer)
                total_places += len(details_a_creer)
                print(f"✅ {len(details_a_creer)} places créées pour la salle {salle.name}")
        
        print(f"🔵 Total: {total_crees} répartitions, {total_places} places")
        print("=" * 60)
        
        return Response({
            "success": True,
            "message": f"✅ {total_crees} répartitions et {total_places} places créées",
            "repartitions_count": total_crees,
            "places_count": total_places
        })
        
    except Exception as e:
        print(f"❌ Erreur dans appliquer_melange: {str(e)}")
        traceback.print_exc()
        return Response({"success": False, "message": f"Erreur serveur : {str(e)}"}, status=500)

# ============================================================
# API : MES PLACES
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mes_places(request):
    user = request.user
    
    try:
        details = RepartitionDetail.objects.filter(user_id=user.id).select_related(
            'repartition__examen', 'repartition__salle'
        )
        
        result = []
        for d in details:
            result.append({
                "examen_id": d.repartition.examen.id,
                "examen_title": d.repartition.examen.title,
                "examen_date": d.repartition.examen.date,
                "examen_time": d.repartition.examen.time,
                "salle_nom": f"{d.repartition.salle.type} {d.repartition.salle.name}",
                "place": d.seat_code,
                "place_number": d.place_number,
            })
        return Response(result)
    except Exception as e:
        print(f"❌ Erreur dans mes_places: {str(e)}")
        return Response([], status=200)


# ============================================================
# VUES CRUD STANDARDS
# ============================================================
class GroupeListCreateView(generics.ListCreateAPIView):
    queryset = GroupeEtudiant.objects.all()
    serializer_class = GroupeEtudiantSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupeEtudiant.objects.all()
    serializer_class = GroupeEtudiantSerializer
    permission_classes = [permissions.IsAuthenticated]

class RepartitionListCreateView(generics.ListCreateAPIView):
    queryset = RepartitionExamen.objects.all()
    serializer_class = RepartitionExamenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        examen_id = self.request.query_params.get('examen')
        if examen_id:
            queryset = queryset.filter(examen_id=examen_id)
        return queryset

class RepartitionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RepartitionExamen.objects.all()
    serializer_class = RepartitionExamenSerializer
    permission_classes = [permissions.IsAuthenticated]

class RepartitionDetailListView(generics.ListAPIView):
    queryset = RepartitionDetail.objects.all()
    serializer_class = RepartitionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        repartition_id = self.request.query_params.get('repartition')
        if repartition_id:
            queryset = queryset.filter(repartition_id=repartition_id)
        return queryset


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_repartition_suggestions(request, examen_id):
    try:
        examen = Exam.objects.get(id=examen_id)
        salles_disponibles = Salle.objects.all()
        groupes = GroupeEtudiant.objects.all()
        total_etudiants = sum(g.effectif for g in groupes)
        capacite_totale = sum(s.capacity for s in salles_disponibles)
        suggestions = [{
            "status": "success" if capacite_totale >= total_etudiants else "warning",
            "message": f"Capacité {'suffisante' if capacite_totale >= total_etudiants else 'insuffisante'}",
            "groupes": [{"id": g.id, "nom": g.nom, "effectif": g.effectif} for g in groupes],
            "salles": [{"id": s.id, "nom": s.name, "capacite": s.capacity} for s in salles_disponibles]
        }]
        return Response(suggestions)
    except Exam.DoesNotExist:
        return Response({"error": "Examen non trouvé"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verifier_capacite(request):
    try:
        repartitions = request.data.get("repartitions", [])
        verification = {}
        for repart in repartitions:
            salle_id = repart.get("salle_id")
            if not salle_id:
                continue
            salle = Salle.objects.get(id=salle_id)
            effectif = repart.get("effectif", 0)
            if salle_id not in verification:
                verification[salle_id] = {
                    "salle_nom": f"{salle.type} {salle.name}",
                    "capacite": salle.capacity,
                    "effectif_total": 0,
                    "groupes": []
                }
            verification[salle_id]["effectif_total"] += effectif
            verification[salle_id]["groupes"].append(repart.get("groupe_nom"))
        resultats = []
        for salle_id, data in verification.items():
            effectif_total = data["effectif_total"]
            capacite = data["capacite"]
            if effectif_total > capacite:
                statut = "error"
                message = f"❌ Dépassement: {effectif_total}/{capacite}"
            elif effectif_total == capacite:
                statut = "success"
                message = f"✔️ Pleine: {effectif_total}/{capacite}"
            else:
                pourcentage = (effectif_total / capacite) * 100
                if pourcentage <= 50:
                    statut = "warning"
                    message = f"⚠️ Sous-utilisation: {effectif_total}/{capacite} ({pourcentage:.0f}%)"
                else:
                    statut = "info"
                    message = f"ℹ️ Partiellement remplie: {effectif_total}/{capacite}"
            resultats.append({
                "salle_id": salle_id,
                "salle_nom": data["salle_nom"],
                "capacite": capacite,
                "effectif_total": effectif_total,
                "groupes": data["groupes"],
                "statut": statut,
                "message": message
            })
        return Response(resultats)
    except Salle.DoesNotExist:
        return Response({"error": "Salle non trouvée"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



# groups/views.py - Remplacer la fonction get_historique_regroupements

# groups/views.py - AJOUTER CES FONCTIONS À LA FIN DU FICHIER

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_historique_regroupements(request):
    """
    Récupère l'historique des regroupements à partir des tables existantes
    """
    try:
        # Récupérer toutes les répartitions groupées par minute de création
        repartitions = RepartitionExamen.objects.all().select_related(
            'examen', 'salle', 'groupe', 'examen__teacher'
        ).order_by('-created_at')
        
        if not repartitions.exists():
            return Response({
                'success': True,
                'historique': []
            })
        
        # Grouper par minute de création (YYYYMMDD_HHMM)
        from collections import defaultdict
        grouped_by_session = defaultdict(lambda: {
            'date_regroupement': None,
            'examens': [],
            'total_etudiants': 0,
            'total_salles': set(),
        })
        
        for repartition in repartitions:
            created = repartition.created_at
            session_key = created.strftime('%Y%m%d_%H%M')
            
            if grouped_by_session[session_key]['date_regroupement'] is None:
                grouped_by_session[session_key]['date_regroupement'] = created
            
            # Ajouter l'examen
            examen_data = {
                'id': repartition.examen.id,
                'title': repartition.examen.title,
                'date': str(repartition.examen.date) if repartition.examen.date else None,
                'time': str(repartition.examen.time) if repartition.examen.time else None,
                'niveau': repartition.examen.niveau,
            }
            
            # Éviter les doublons
            examen_existe = False
            for ex in grouped_by_session[session_key]['examens']:
                if ex['id'] == examen_data['id']:
                    examen_existe = True
                    break
            
            if not examen_existe:
                grouped_by_session[session_key]['examens'].append(examen_data)
            
            grouped_by_session[session_key]['total_etudiants'] += repartition.effectif
            grouped_by_session[session_key]['total_salles'].add(repartition.salle.id)
        
        # Convertir en liste
        historique = []
        for session_key, data in grouped_by_session.items():
            historique.append({
                'id': session_key,
                'date_regroupement': data['date_regroupement'].isoformat(),
                'type_regroupement': 'melange' if len(data['examens']) > 1 else 'simple',
                'total_etudiants': data['total_etudiants'],
                'total_salles': len(data['total_salles']),
                'examens': data['examens'],
            })
        
        # Trier par date décroissante
        historique.sort(key=lambda x: x['date_regroupement'], reverse=True)
        
        return Response({
            'success': True,
            'historique': historique
        })
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': True,
            'historique': []
        })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_historique_details(request, session_key):
    """
    Récupère les détails complets d'une session d'historique
    """
    try:
        from datetime import datetime
        
        # Session_key est au format YYYYMMDD_HHMM
        try:
            session_date = datetime.strptime(session_key, '%Y%m%d_%H%M')
        except ValueError:
            return Response({
                'success': False,
                'message': 'Format de session invalide'
            }, status=400)
        
        # Chercher les répartitions créées autour de cette date
        date_start = session_date.replace(second=0, microsecond=0)
        date_end = date_start.replace(second=59, microsecond=999999)
        
        repartitions = RepartitionExamen.objects.filter(
            created_at__gte=date_start,
            created_at__lte=date_end
        ).select_related('examen', 'salle', 'groupe', 'examen__teacher')
        
        if not repartitions.exists():
            return Response({
                'success': False,
                'message': 'Aucune répartition trouvée pour cette session'
            }, status=404)
        
        # Grouper les détails par examen
        details_examens = []
        examens_ids = repartitions.values_list('examen_id', flat=True).distinct()
        
        for examen_id in examens_ids:
            reparts_examen = repartitions.filter(examen_id=examen_id)
            examen = reparts_examen.first().examen
            
            salles_data = []
            
            for repart in reparts_examen:
                details = RepartitionDetail.objects.filter(
                    repartition=repart
                ).select_related('user')
                
                etudiants_list = []
                for detail in details:
                    nom_etudiant = f"{detail.user.first_name} {detail.user.last_name}".strip() or detail.user.username
                    etudiants_list.append({
                        'etudiant_nom': nom_etudiant,
                        'place': detail.seat_code,
                        'place_number': detail.place_number,
                        'user_id': detail.user.id
                    })
                
                etudiants_list.sort(key=lambda x: x.get('place_number', 0))
                
                salles_data.append({
                    'salle_id': repart.salle.id,
                    'salle_nom': f"{repart.salle.type} {repart.salle.name}".strip() if repart.salle.type else repart.salle.name,
                    'capacite': repart.salle.capacity,
                    'effectif': len(etudiants_list),
                    'etudiants': etudiants_list,
                })
            
            surveillant_nom = examen.teacher.username if examen.teacher else None
            
            details_examens.append({
                'examen_id': examen.id,
                'examen_title': examen.title,
                'examen_date': str(examen.date) if examen.date else None,
                'examen_time': str(examen.time) if examen.time else None,
                'examen_niveau': examen.niveau,
                'surveillant': surveillant_nom,
                'salles': salles_data
            })
        
        total_etudiants = sum(sum(len(s.get('etudiants', [])) for s in examen.get('salles', [])) for examen in details_examens)
        
        return Response({
            'success': True,
            'regroupement': {
                'id': session_key,
                'date_regroupement': date_start.isoformat(),
                'type_regroupement': 'melange' if len(examens_ids) > 1 else 'simple',
                'total_etudiants': total_etudiants,
                'total_salles': len(salles_data) if salles_data else 0
            },
            'details_examens': details_examens
        })
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=500)


# groups/views.py - REMPLACER COMPLÈTEMENT la fonction

# groups/views.py - REMPLACER la fonction telecharger_pdf_historique

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def telecharger_pdf_historique(request, session_key):
    """
    Télécharge le PDF/HTML pour une session d'historique
    Format: TABLEAU avec (Salle + Groupe) en lignes, Créneaux en colonnes
    """
    try:
        from django.http import HttpResponse
        from datetime import datetime
        
        session_date = datetime.strptime(session_key, '%Y%m%d_%H%M')
        date_start = session_date.replace(second=0, microsecond=0)
        date_end = date_start.replace(second=59, microsecond=999999)
        
        repartitions = RepartitionExamen.objects.filter(
            created_at__gte=date_start,
            created_at__lte=date_end
        ).select_related('examen', 'salle', 'groupe', 'examen__teacher')
        
        if not repartitions.exists():
            return Response({'error': 'Aucune répartition trouvée'}, status=404)
        
        # Générer le HTML au format tableau (Salle + Groupe)
        html_content = generate_tableau_examens(repartitions, session_key, date_start)
        
        return HttpResponse(html_content, content_type='text/html')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)


# groups/views.py - REMPLACER COMPLÈTEMENT la fonction generate_tableau_examens

# groups/views.py - REMPLACER COMPLÈTEMENT la fonction generate_tableau_examens

# groups/views.py - REMPLACER COMPLÈTEMENT la fonction generate_tableau_examens

# groups/views.py - REMPLACER la fonction generate_tableau_examens

# groups/views.py - REMPLACER la fonction generate_tableau_examens

# groups/views.py - REMPLACER COMPLÈTEMENT la fonction generate_tableau_examens

# groups/views.py - REMPLACER COMPLÈTEMENT la fonction generate_tableau_examens

def generate_tableau_examens(repartitions, session_key, date_regroupement):
    """Génère le HTML au format TABLEAU avec une ligne par examen"""
    from datetime import datetime
    
    maintenant = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Collecter toutes les données
    lignes = []
    
    for repart in repartitions:
        examen = repart.examen
        salle = repart.salle
        groupe = repart.groupe
        
        salle_nom = f"{salle.type} {salle.name}".strip() if salle.type else salle.name
        groupe_nom = groupe.nom if groupe else "Groupe"
        
        date_examen = str(examen.date) if examen.date else "Date inconnue"
        heure_examen = examen.time.strftime('%H:%M') if examen.time else "Horaire inconnu"
        
        # Formater la date
        try:
            date_obj = datetime.strptime(date_examen, '%Y-%m-%d')
            jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            date_formatee = f"{jours_fr[date_obj.weekday()]} {date_obj.strftime('%d/%m/%Y')}"
        except:
            date_formatee = date_examen
        
        lignes.append({
            'salle': salle_nom,
            'groupe': groupe_nom,
            'date': date_formatee,
            'horaire': heure_examen,
            'examen': examen.title
        })
    
    # Trier par salle, groupe, date, horaire
    lignes.sort(key=lambda x: (x['salle'], x['groupe'], x['date'], x['horaire']))
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendrier des Examens - {session_key}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Times New Roman', Times, serif;
            background: white;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid black;
        }}
        .header h1 {{
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .header h2 {{
            font-size: 16px;
            font-weight: normal;
            margin-bottom: 5px;
        }}
        .header p {{
            font-size: 12px;
            margin-top: 10px;
        }}
        
        .exam-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 20px;
        }}
        .exam-table th,
        .exam-table td {{
            border: 2px solid black;
            padding: 10px 8px;
            vertical-align: middle;
        }}
        .exam-table th {{
            background: #e0e0e0;
            text-align: center;
            font-weight: bold;
            font-size: 14px;
        }}
        .exam-table td {{
            text-align: center;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 10px;
            border-top: 1px solid black;
            margin-top: 25px;
        }}
        
        @media print {{
            body {{ padding: 20px; margin: 0; }}
            .exam-table th, .exam-table td {{ border: 2px solid black !important; }}
            .exam-table th {{ background: #e0e0e0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Institut Supérieur des Sciences Appliquées et de Technologie de Kasserine</h1>
            <h2>Calendrier des Examens - Session du {date_regroupement.strftime('%d/%m/%Y à %H:%M')}</h2>
            <p>Généré le : {maintenant}</p>
        </div>
        
        <table class="exam-table">
            <thead>
                <tr>
                    <th>Salle</th>
                    <th>Groupe</th>
                    <th>Date</th>
                    <th>Horaire</th>
                    <th>Examen</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for ligne in lignes:
        html += f"""
                <tr>
                    <td>{ligne['salle']}</td>
                    <td>{ligne['groupe']}</td>
                    <td>{ligne['date']}</td>
                    <td>{ligne['horaire']}</td>
                    <td>{ligne['examen']}</td>
                </tr>
"""
    
    html += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>Document officiel - À imprimer et à distribuer aux étudiants</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def generate_calendrier_html(repartitions, session_key, date_regroupement):
    """Génère le HTML au format TABLEAU CALENDRIER"""
    from datetime import datetime
    from collections import defaultdict
    
    maintenant = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Organiser les données par salle et par créneau
    salles_map = defaultdict(lambda: defaultdict(list))
    tous_les_creneaux = set()
    toutes_les_salles = set()
    
    for repart in repartitions:
        examen = repart.examen
        salle = repart.salle
        
        salle_nom = f"{salle.type} {salle.name}".strip() if salle.type else salle.name
        
        date_examen = str(examen.date) if examen.date else "Date inconnue"
        heure_examen = examen.time.strftime('%H:%M') if examen.time else "Horaire inconnu"
        creneau_key = f"{date_examen}|{heure_examen}"
        
        details = RepartitionDetail.objects.filter(repartition=repart).count()
        surveillant = examen.teacher.username if examen.teacher else "À définir"
        groupe_nom = repart.groupe.nom if repart.groupe else "Groupe"
        
        tous_les_creneaux.add(creneau_key)
        toutes_les_salles.add(salle_nom)
        
        salles_map[salle_nom][creneau_key].append({
            'groupe': groupe_nom,
            'examen': examen.title,
            'surveillant': surveillant,
            'nb_etudiants': details
        })
    
    # Trier les créneaux
    def tri_creneau(creneau):
        try:
            date_str, heure_str = creneau.split('|')
            return (date_str, heure_str)
        except:
            return (creneau, "")
    
    creneaux_list = sorted(tous_les_creneaux, key=tri_creneau)
    salles_list = sorted(toutes_les_salles)
    
    # Formater les entêtes
    entetes_creneaux = []
    for creneau in creneaux_list:
        try:
            date_str, heure_str = creneau.split('|')
            if date_str != "Date inconnue":
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                    date_formatee = f"{jours_fr[date_obj.weekday()]} {date_obj.strftime('%d/%m/%Y')}"
                except:
                    date_formatee = date_str
            else:
                date_formatee = date_str
            entetes_creneaux.append(f"{date_formatee}<br><small>{heure_str}</small>")
        except:
            entetes_creneaux.append(creneau)
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendrier des Examens - {session_key}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: white;
            padding: 40px 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        .university-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #1e3c72;
        }}
        .university-header h1 {{
            font-size: 22px;
            color: #1e3c72;
            margin-bottom: 8px;
        }}
        .university-header h2 {{
            font-size: 16px;
            color: #2a5298;
            font-weight: normal;
        }}
        .university-header p {{
            font-size: 12px;
            color: #64748b;
            margin-top: 5px;
        }}
        
        .calendrier-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        .calendrier-table th {{
            background: #1e3c72;
            color: white;
            padding: 10px 6px;
            border: 1px solid #2a5298;
            text-align: center;
        }}
        .calendrier-table td {{
            border: 1px solid #e2e8f0;
            padding: 8px 6px;
            vertical-align: top;
        }}
        .salle-cell {{
            background: #f0fdf4;
            font-weight: 600;
            text-align: center;
            vertical-align: middle;
            width: 100px;
        }}
        
        .examen-cell {{
            margin-bottom: 5px;
            padding: 5px;
            background: #f8fafc;
            border-radius: 4px;
            border-left: 3px solid #11998e;
        }}
        .examen-groupe {{
            font-weight: 700;
            color: #1e3c72;
            font-size: 10px;
        }}
        .examen-nom {{
            font-weight: 600;
            font-size: 10px;
            margin: 2px 0;
        }}
        .examen-surveillant {{
            font-size: 9px;
            color: #64748b;
        }}
        .examen-nb {{
            font-size: 9px;
            color: #11998e;
            margin-top: 2px;
        }}
        .vide-cell {{
            color: #cbd5e1;
            text-align: center;
            font-size: 11px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #64748b;
            font-size: 10px;
            border-top: 1px solid #e2e8f0;
            margin-top: 20px;
        }}
        
        @media print {{
            body {{ padding: 20px; margin: 0; }}
            .calendrier-table th {{ background: #1e3c72 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .salle-cell {{ background: #f0fdf4 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="university-header">
            <h1>🏛️ Institut Supérieur des Sciences Appliquées et de Technologie de Kasserine</h1>
            <h2>📅 Calendrier des Examens - Session du {date_regroupement.strftime('%d/%m/%Y %H:%M')}</h2>
            <p>Généré le : {maintenant}</p>
        </div>
        
        <table class="calendrier-table">
            <thead>
                <tr>
                    <th>Salle / Créneau</th>
                    {''.join([f'<th>{entete}</th>' for entete in entetes_creneaux])}
                </tr>
            </thead>
            <tbody>
"""
    
    for salle in salles_list:
        html += f"""
                <tr>
                    <td class="salle-cell">🏫 {salle}</td>
"""
        for creneau in creneaux_list:
            examens = salles_map[salle].get(creneau, [])
            if examens:
                cell_content = ""
                for ex in examens:
                    cell_content += f"""
                        <div class="examen-cell">
                            <div class="examen-groupe">{ex['groupe']}</div>
                            <div class="examen-nom">{ex['examen']}</div>
                            <div class="examen-surveillant">👨‍🏫 {ex['surveillant']}</div>
                            <div class="examen-nb">👥 {ex['nb_etudiants']} étudiants</div>
                        </div>
"""
                html += f'<td>{cell_content}</td>'
            else:
                html += '<td class="vide-cell">—</td>'
        html += """
                </td>
"""
    
    html += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>Document généré automatiquement par le système de gestion des examens</p>
            <p>Pour imprimer : utilisez 'Ctrl+P' puis sélectionnez 'Enregistrer en PDF'</p>
        </div>
    </div>
</body>
</html>"""
    
    return html