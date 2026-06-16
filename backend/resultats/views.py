# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from django.db.models import Q, Avg, F, Sum, Count
# from django.shortcuts import get_object_or_404
# from .models import ResultatMatiere
# from matieres.models import Matiere
# from users.models import User, Groupe, StudentProfile, TeacherProfile
# import logging

# logger = logging.getLogger(__name__)


# class MatieresByTeacherView(APIView):
#     """Récupère les matières enseignées par l'enseignant connecté"""
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
        
#         if user.role != 'enseignant':
#             return Response({"error": "Non autorisé - Réservé aux enseignants"}, 
#                           status=status.HTTP_403_FORBIDDEN)
        
#         from matieres.serializers import MatiereSerializer
        
#         matieres_directes = Matiere.objects.filter(enseignant=user)
        
#         matieres_departement = Matiere.objects.none()
#         if hasattr(user, 'teacher_profile') and user.teacher_profile.department:
#             matieres_departement = Matiere.objects.filter(
#                 specialite__department=user.teacher_profile.department
#             )
        
#         matieres = (matieres_directes | matieres_departement).distinct()
        
#         serializer = MatiereSerializer(matieres, many=True)
#         return Response(serializer.data)


# class StudentsByMatiereAndGroupesView(APIView):
#     """Récupère les étudiants d'une matière avec leurs notes existantes"""
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         matiere_id = request.query_params.get('matiere')
        
#         if not matiere_id:
#             return Response({"error": "matiere parameter required"}, 
#                           status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             matiere = Matiere.objects.select_related(
#                 'specialite', 'specialite__department'
#             ).get(id=matiere_id)
#         except Matiere.DoesNotExist:
#             return Response({"error": "Matière non trouvée"}, 
#                           status=status.HTTP_404_NOT_FOUND)
        
#         user = request.user
#         if user.role == 'enseignant':
#             has_access = (
#                 matiere.enseignant == user or 
#                 (hasattr(user, 'teacher_profile') and 
#                  user.teacher_profile.department == matiere.specialite.department)
#             )
#             if not has_access:
#                 return Response({"error": "Accès non autorisé à cette matière"}, 
#                               status=status.HTTP_403_FORBIDDEN)
        
#         # Trouver les groupes concernés
#         groupes = Groupe.objects.none()
        
#         if matiere.specialite and hasattr(matiere.specialite, 'department') and matiere.specialite.department:
#             groupes = Groupe.objects.filter(
#                 department=matiere.specialite.department,
#                 level=matiere.niveau
#             )
#         elif matiere.specialite:
#             groupes = Groupe.objects.filter(specialite=matiere.specialite)
        
#         if not groupes.exists():
#             return Response([])
        
#         # Récupérer les étudiants
#         students = StudentProfile.objects.filter(
#             groupe__in=groupes
#         ).select_related('user', 'groupe')
        
#         # Construire la réponse avec les notes existantes
#         resultats_data = []
#         for student in students:
#             existing_notes = None
            
#             try:
#                 existing_result = ResultatMatiere.objects.get(
#                     etudiant=student.user,
#                     matiere=matiere,
#                     session='principale'
#                 )
#                 existing_notes = {
#                     'ds': existing_result.ds,
#                     'exam': existing_result.exam,
#                     'oral': existing_result.oral,
#                     'tp': existing_result.tp,
#                     'exam_r': existing_result.exam_r,
#                     'moyenne': existing_result.moyenne,
#                     'is_validated': existing_result.is_validated
#                 }
#             except ResultatMatiere.DoesNotExist:
#                 pass
            
#             resultats_data.append({
#                 'id': student.user.id,
#                 'username': student.user.username,
#                 'first_name': student.user.first_name or '',
#                 'last_name': student.user.last_name or '',
#                 'groupe_nom': student.groupe.name if student.groupe else 'N/A',
#                 'existing_notes': existing_notes
#             })
        
#         return Response(resultats_data)


# class CreateOrUpdateNoteView(APIView):
#     """Crée ou met à jour une note - LE BACKEND CALCULE TOUT"""
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         data = request.data
#         user = request.user
        
#         etudiant_id = data.get('etudiant')
#         matiere_id = data.get('matiere')
#         session_type = data.get('session', 'principale')
        
#         if not etudiant_id or not matiere_id:
#             return Response({"error": "etudiant et matiere sont requis"}, 
#                           status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             etudiant = User.objects.get(id=etudiant_id, role='etudiant')
#             matiere = Matiere.objects.get(id=matiere_id)
#         except User.DoesNotExist:
#             return Response({"error": "Étudiant non trouvé"}, 
#                           status=status.HTTP_404_NOT_FOUND)
#         except Matiere.DoesNotExist:
#             return Response({"error": "Matière non trouvée"}, 
#                           status=status.HTTP_404_NOT_FOUND)
        
#         # Vérification département
#         try:
#             student_profile = StudentProfile.objects.get(user=etudiant)
#             if not student_profile.groupe:
#                 return Response({"error": "Étudiant non assigné à un groupe"}, 
#                               status=status.HTTP_400_BAD_REQUEST)
            
#             student_department = student_profile.groupe.department
#             matiere_department = matiere.specialite.department
            
#             if student_department != matiere_department:
#                 logger.warning(
#                     f"Tentative de note incohérente: {etudiant.username} "
#                     f"({student_department.nom if student_department else 'N/A'}) "
#                     f"- {matiere.titre} "
#                     f"({matiere_department.nom if matiere_department else 'N/A'})"
#                 )
#                 return Response({
#                     "error": "Incohérence : matière hors département de l'étudiant"
#                 }, status=status.HTTP_400_BAD_REQUEST)
                
#         except StudentProfile.DoesNotExist:
#             return Response({"error": "Profil étudiant non trouvé"}, 
#                           status=status.HTTP_404_NOT_FOUND)
        
#         # Vérifier droits enseignant
#         if user.role == 'enseignant':
#             has_access = (
#                 matiere.enseignant == user or
#                 (hasattr(user, 'teacher_profile') and 
#                  user.teacher_profile and 
#                  user.teacher_profile.department == matiere_department)
#             )
#             if not has_access:
#                 return Response({"error": "Non autorisé à noter cette matière"}, 
#                               status=status.HTTP_403_FORBIDDEN)
        
#         # Créer ou récupérer le résultat
#         resultat, created = ResultatMatiere.objects.get_or_create(
#             etudiant=etudiant,
#             matiere=matiere,
#             session=session_type,
#             defaults={
#                 'ds': 0, 'exam': 0, 'oral': 0, 'tp': 0, 'exam_r': 0,
#                 'moyenne': 0, 'is_validated': False
#             }
#         )
        
#         # Mettre à jour les notes brutes UNIQUEMENT
#         if session_type == 'principale':
#             resultat.ds = float(data.get('ds', resultat.ds or 0))
#             resultat.exam = float(data.get('exam', resultat.exam or 0))
#             resultat.oral = float(data.get('oral', resultat.oral or 0))
#             resultat.tp = float(data.get('tp', resultat.tp or 0))
#         else:
#             resultat.exam_r = float(data.get('exam_r', resultat.exam_r or 0))
        
#         # LE CALCUL SE FAIT ICI, DANS LE BACKEND
#         resultat.save()
        
#         from .serializers import ResultatMatiereSerializer
#         serializer = ResultatMatiereSerializer(resultat)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class StudentNotesView(APIView):
#     """
#     Vue pour le dashboard étudiant.
#     Calcule TOUT dans le backend : moyennes par semestre, annuelles, générale.
#     """
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
        
#         if user.role != 'etudiant':
#             return Response({"error": "Réservé aux étudiants"}, 
#                           status=status.HTTP_403_FORBIDDEN)
        
#         # Récupérer tous les résultats de l'étudiant
#         resultats = ResultatMatiere.objects.filter(
#             etudiant=user
#         ).select_related('matiere', 'matiere__specialite')
        
#         # ==========================================
#         # 1. PRÉPARER LES DONNÉES PAR MATIÈRE
#         # ==========================================
#         resultats_list = []
#         matieres_dict = {}  # Pour déduplication (garder la meilleure moyenne)
        
#         for result in resultats:
#             matiere = result.matiere
            
#             # Si on a déjà cette matière, garder la meilleure moyenne
#             if matiere.id in matieres_dict:
#                 if result.moyenne > matieres_dict[matiere.id]['moyenne']:
#                     matieres_dict[matiere.id] = {
#                         'id': result.id,
#                         'matiere_code': matiere.code,
#                         'matiere_nom': matiere.titre,
#                         'coefficient': matiere.coefficient,
#                         'credits': matiere.credits,
#                         'semestre': matiere.semestre,
#                         'nature': matiere.nature,
#                         'ds': result.ds,
#                         'exam': result.exam,
#                         'oral': result.oral,
#                         'tp': result.tp,
#                         'exam_r': result.exam_r,
#                         'moyenne': result.moyenne,
#                         'is_validated': result.is_validated,
#                         'session': result.session
#                     }
#             else:
#                 matieres_dict[matiere.id] = {
#                     'id': result.id,
#                     'matiere_code': matiere.code,
#                     'matiere_nom': matiere.titre,
#                     'coefficient': matiere.coefficient,
#                     'credits': matiere.credits,
#                     'semestre': matiere.semestre,
#                     'nature': matiere.nature,
#                     'ds': result.ds,
#                     'exam': result.exam,
#                     'oral': result.oral,
#                     'tp': result.tp,
#                     'exam_r': result.exam_r,
#                     'moyenne': result.moyenne,
#                     'is_validated': result.is_validated,
#                     'session': result.session
#                 }
        
#         resultats_list = list(matieres_dict.values())
        
#         # ==========================================
#         # 2. CALCULER LES MOYENNES PAR SEMESTRE
#         # ==========================================
#         moyennes_semestres = {}
#         credits_semestres = {}
        
#         for semestre in range(1, 7):
#             # Utiliser la méthode statique du modèle
#             moyenne_semestre = ResultatMatiere.calculer_moyenne_semestre(user, semestre)
#             moyennes_semestres[f"S{semestre}"] = moyenne_semestre
            
#             # Calculer les crédits validés pour ce semestre
#             resultats_semestre = ResultatMatiere.objects.filter(
#                 etudiant=user,
#                 matiere__semestre=semestre,
#                 is_validated=True
#             ).select_related('matiere')
            
#             credits = sum(r.matiere.credits for r in resultats_semestre)
#             credits_semestres[f"S{semestre}"] = credits
        
#         # ==========================================
#         # 3. CALCULER LES MOYENNES ANNUELLES
#         # ==========================================
#         moyennes_annuelles = {}
#         for annee in range(1, 4):
#             moyenne_annuelle = ResultatMatiere.calculer_moyenne_annuelle(user, annee)
#             moyennes_annuelles[f"Année {annee}"] = moyenne_annuelle
        
#         # ==========================================
#         # 4. CALCULER LA MOYENNE GÉNÉRALE (HIÉRARCHIQUE)
#         # ==========================================
#         moyenne_generale = ResultatMatiere.calculer_moyenne_generale(user)
        
#         # ==========================================
#         # 5. STATISTIQUES GLOBALES
#         # ==========================================
#         total_matieres = len(resultats_list)
#         matieres_validees = sum(1 for r in resultats_list if r['is_validated'])
#         total_credits = sum(r['credits'] for r in resultats_list if r['is_validated'])
#         total_credits_possibles = sum(r['credits'] for r in resultats_list)
        
#         # ==========================================
#         # 6. RÉPONSE COMPLÈTE
#         # ==========================================
#         return Response({
#             'resultats': resultats_list,
#             'moyennes_semestres': moyennes_semestres,
#             'credits_semestres': credits_semestres,
#             'moyennes_annuelles': moyennes_annuelles,
#             'moyenne_generale': moyenne_generale,
#             'total_matieres': total_matieres,
#             'matieres_validees': matieres_validees,
#             'total_credits': total_credits,
#             'total_credits_possibles': total_credits_possibles,
#             'is_valide': moyenne_generale >= 10
#         })


# class StudentsByTeacherDepartmentView(APIView):
#     """Récupère tous les étudiants du département de l'enseignant"""
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
        
#         if user.role != 'enseignant':
#             return Response({"error": "Non autorisé - Réservé aux enseignants"}, 
#                           status=status.HTTP_403_FORBIDDEN)
        
#         teacher_dept = None
#         if hasattr(user, 'teacher_profile') and user.teacher_profile:
#             teacher_dept = user.teacher_profile.department
        
#         if not teacher_dept:
#             return Response({"error": "Vous n'êtes pas assigné à un département"}, 
#                           status=status.HTTP_200_OK)
        
#         groupes = Groupe.objects.filter(department=teacher_dept)
#         students = StudentProfile.objects.filter(
#             groupe__in=groupes
#         ).select_related('user', 'groupe')
        
#         resultats_data = []
#         for student in students:
#             resultats_data.append({
#                 'id': student.user.id,
#                 'username': student.user.username,
#                 'first_name': student.user.first_name,
#                 'last_name': student.user.last_name,
#                 'groupe_nom': student.groupe.nom if student.groupe else 'N/A',
#                 'groupe_level': student.groupe.level if student.groupe else None,
#                 'matricule': getattr(student, 'matricule', ''),
#             })
        
#         return Response(resultats_data)




# resultats/views.py - CODE COMPLET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import ResultatMatiere
from .serializers import ResultatMatiereSerializer
from matieres.models import Matiere, Specialite
from matieres.serializers import MatiereSerializer
from users.models import User, Groupe, StudentProfile, TeacherProfile
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MatieresByTeacherView(APIView):
    """Récupère les matières enseignées par l'enseignant connecté"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'enseignant':
            return Response({"error": "Non autorisé - Réservé aux enseignants"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        matieres_directes = Matiere.objects.filter(enseignant=user)
        
        matieres_departement = Matiere.objects.none()
        if hasattr(user, 'teacher_profile') and user.teacher_profile and user.teacher_profile.department:
            matieres_departement = Matiere.objects.filter(
                specialite__department=user.teacher_profile.department
            )
        
        matieres = (matieres_directes | matieres_departement).distinct()
        
        serializer = MatiereSerializer(matieres, many=True)
        return Response(serializer.data)


class StudentsByMatiereAndGroupesView(APIView):
    """Récupère les étudiants d'une matière avec leurs notes existantes"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        matiere_id = request.query_params.get('matiere')
        
        if not matiere_id:
            return Response({"error": "matiere parameter required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            matiere = Matiere.objects.select_related(
                'specialite', 'specialite__department'
            ).get(id=matiere_id)
        except Matiere.DoesNotExist:
            return Response({"error": "Matière non trouvée"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        if user.role == 'enseignant':
            matiere_department = matiere.specialite.department if matiere.specialite else None
            has_access = (
                matiere.enseignant == user or 
                (hasattr(user, 'teacher_profile') and 
                 user.teacher_profile and 
                 user.teacher_profile.department == matiere_department)
            )
            if not has_access:
                return Response({"error": "Accès non autorisé à cette matière"}, 
                              status=status.HTTP_403_FORBIDDEN)
        
        # Trouver les groupes concernés
        groupes = Groupe.objects.none()
        
        if matiere.specialite and hasattr(matiere.specialite, 'department') and matiere.specialite.department:
            groupes = Groupe.objects.filter(
                department=matiere.specialite.department,
                level=matiere.niveau
            )
        elif matiere.specialite:
            groupes = Groupe.objects.filter(specialite=matiere.specialite)
        
        if not groupes.exists():
            return Response([])
        
        # Récupérer les étudiants
        students = StudentProfile.objects.filter(
            groupe__in=groupes
        ).select_related('user', 'groupe')
        
        # Construire la réponse avec les notes existantes
        resultats_data = []
        for student in students:
            existing_notes = None
            
            try:
                existing_result = ResultatMatiere.objects.get(
                    etudiant=student.user,
                    matiere=matiere,
                    session='principale'
                )
                existing_notes = {
                    'id': existing_result.id,
                    'ds': existing_result.ds,
                    'exam': existing_result.exam,
                    'oral': existing_result.oral,
                    'tp': existing_result.tp,
                    'exam_r': existing_result.exam_r,
                    'moyenne': existing_result.moyenne,
                    'moyenne_finale': existing_result.moyenne_finale if hasattr(existing_result, 'moyenne_finale') else existing_result.moyenne,
                    'is_validated': existing_result.is_validated
                }
            except ResultatMatiere.DoesNotExist:
                pass
            
            # Récupérer le nom du groupe
            groupe_nom = "N/A"
            if student.groupe:
                if hasattr(student.groupe, 'name'):
                    groupe_nom = student.groupe.name
                elif hasattr(student.groupe, 'nom'):
                    groupe_nom = student.groupe.nom
                else:
                    groupe_nom = str(student.groupe)
            
            resultats_data.append({
                'id': student.user.id,
                'username': student.user.username,
                'first_name': student.user.first_name or '',
                'last_name': student.user.last_name or '',
                'groupe_nom': groupe_nom,
                'existing_notes': existing_notes
            })
        
        return Response(resultats_data)


class CreateOrUpdateNoteView(APIView):
    """Crée ou met à jour une note - LE BACKEND CALCULE TOUT"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        user = request.user
        
        etudiant_id = data.get('etudiant')
        matiere_id = data.get('matiere')
        session_type = data.get('session', 'principale')
        
        if not etudiant_id or not matiere_id:
            return Response({"error": "etudiant et matiere sont requis"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            etudiant = User.objects.get(id=etudiant_id, role='etudiant')
            matiere = Matiere.objects.get(id=matiere_id)
        except User.DoesNotExist:
            return Response({"error": "Étudiant non trouvé"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Matiere.DoesNotExist:
            return Response({"error": "Matière non trouvée"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        try:
            student_profile = StudentProfile.objects.get(user=etudiant)
            if not student_profile.groupe:
                return Response({"error": "Étudiant non assigné à un groupe"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Profil étudiant non trouvé"}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        resultat, created = ResultatMatiere.objects.get_or_create(
            etudiant=etudiant,
            matiere=matiere,
            session=session_type,
            defaults={
                'ds': 0, 'exam': 0, 'oral': 0, 'tp': 0, 'exam_r': 0,
                'moyenne': 0, 'moyenne_finale': 0, 'is_validated': False
            }
        )
        
        if session_type == 'principale':
            if 'ds' in data:
                resultat.ds = float(data.get('ds', 0))
            if 'exam' in data:
                resultat.exam = float(data.get('exam', 0))
            if 'oral' in data:
                resultat.oral = float(data.get('oral', 0))
            if 'tp' in data:
                resultat.tp = float(data.get('tp', 0))
        else:
            if 'exam_r' in data:
                resultat.exam_r = float(data.get('exam_r', 0))
        
        resultat.save()
        
        serializer = ResultatMatiereSerializer(resultat)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentNotesView(APIView):
    """
    Vue pour le dashboard étudiant.
    Le backend est la SEULE source de vérité pour tous les calculs.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'etudiant':
            return Response({"error": "Réservé aux étudiants"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # ==========================================
        # 1. RÉCUPÉRER LES INFORMATIONS DE L'ÉTUDIANT AVEC GROUPE ET SPÉCIALITÉ
        # ==========================================
        niveau = "Non défini"
        specialite = "Non défini"
        groupe_nom = "Non défini"
        specialite_code = ""
        
        try:
            student_profile = StudentProfile.objects.select_related('groupe').get(user=user)
            if student_profile.groupe:
                groupe_nom = student_profile.groupe.name
                niveau = student_profile.groupe.level or "Non défini"
                
                # Extraire le code spécialité depuis le nom du groupe
                group_parts = student_profile.groupe.name.split(" ")
                specialite_code = group_parts[0] if group_parts else ""
                
                # Chercher la spécialité par son code
                if specialite_code:
                    specialite_obj = Specialite.objects.filter(code=specialite_code).first()
                    if specialite_obj:
                        specialite = specialite_obj.nom
                    else:
                        specialite = specialite_code
                else:
                    # Fallback: chercher par le nom du groupe
                    specialite_obj = Specialite.objects.filter(nom__icontains=student_profile.groupe.name).first()
                    if specialite_obj:
                        specialite = specialite_obj.nom
                        specialite_code = specialite_obj.code
        except StudentProfile.DoesNotExist:
            pass
        except Exception as e:
            print(f"Erreur récupération spécialité: {e}")
        
        nom_complet = f"{user.first_name} {user.last_name}".strip() or user.username
        prenom = user.first_name or ""
        nom = user.last_name or ""
        
        # ==========================================
        # 2. RÉCUPÉRER TOUS LES RÉSULTATS
        # ==========================================
        resultats = ResultatMatiere.objects.filter(
            etudiant=user,
            session='principale'
        ).select_related('matiere', 'matiere__specialite')
        
        # ==========================================
        # 3. PRÉPARER LA LISTE DES RÉSULTATS
        # ==========================================
        resultats_list = []
        matieres_dict = {}
        
        for result in resultats:
            matiere = result.matiere
            
            if matiere.id in matieres_dict:
                if result.moyenne_finale > matieres_dict[matiere.id]['moyenne']:
                    matieres_dict[matiere.id] = {
                        'id': result.id,
                        'matiere_code': matiere.code,
                        'matiere_nom': matiere.titre,
                        'coefficient': matiere.coefficient or 1,
                        'credits': matiere.credits or 0,
                        'semestre': matiere.semestre,
                        'nature': matiere.nature,
                        'ds': result.ds,
                        'exam': result.exam,
                        'oral': result.oral,
                        'tp': result.tp,
                        'exam_r': result.exam_r,
                        'moyenne': result.moyenne_finale if hasattr(result, 'moyenne_finale') and result.moyenne_finale > 0 else result.moyenne,
                        'is_validated': result.is_validated
                    }
            else:
                matieres_dict[matiere.id] = {
                    'id': result.id,
                    'matiere_code': matiere.code,
                    'matiere_nom': matiere.titre,
                    'coefficient': matiere.coefficient or 1,
                    'credits': matiere.credits or 0,
                    'semestre': matiere.semestre,
                    'nature': matiere.nature,
                    'ds': result.ds,
                    'exam': result.exam,
                    'oral': result.oral,
                    'tp': result.tp,
                    'exam_r': result.exam_r,
                    'moyenne': result.moyenne_finale if hasattr(result, 'moyenne_finale') and result.moyenne_finale > 0 else result.moyenne,
                    'is_validated': result.is_validated
                }
        
        resultats_list = list(matieres_dict.values())
        
        # ==========================================
        # 4. CALCULER LES MOYENNES PAR SEMESTRE
        # ==========================================
        moyennes_semestres = {}
        credits_semestres = {}
        
        for semestre in range(1, 7):
            resultats_semestre = [r for r in resultats_list if r['semestre'] == semestre]
            
            # Moyenne pondérée du semestre
            total_coef = 0
            somme_ponderee = 0
            
            for r in resultats_semestre:
                if r['moyenne'] is not None and r['moyenne'] > 0:
                    coef = r['coefficient']
                    total_coef += coef
                    somme_ponderee += r['moyenne'] * coef
            
            moyenne_semestre = round(somme_ponderee / total_coef, 2) if total_coef > 0 else 0
            moyennes_semestres[f"S{semestre}"] = moyenne_semestre
            
            # Crédits validés
            credits = sum(r['credits'] for r in resultats_semestre if r['is_validated'])
            credits_semestres[f"S{semestre}"] = credits
        
        # ==========================================
        # 5. CALCULER LES MOYENNES ANNUELLES
        # ==========================================
        moyennes_annuelles = {}
        
        for annee in range(1, 4):
            semestre_debut = (annee - 1) * 2 + 1
            semestre_fin = semestre_debut + 1
            
            s1_moyenne = moyennes_semestres.get(f"S{semestre_debut}", 0)
            s2_moyenne = moyennes_semestres.get(f"S{semestre_fin}", 0)
            
            moyennes_valides = []
            if s1_moyenne > 0:
                moyennes_valides.append(s1_moyenne)
            if s2_moyenne > 0:
                moyennes_valides.append(s2_moyenne)
            
            moyenne_annee = round(sum(moyennes_valides) / len(moyennes_valides), 2) if moyennes_valides else 0
            moyennes_annuelles[f"Année {annee}"] = moyenne_annee
        
        # ==========================================
        # 6. CALCULER LA MOYENNE GÉNÉRALE
        # ==========================================
        moyennes_annees = [
            moyennes_annuelles["Année 1"],
            moyennes_annuelles["Année 2"],
            moyennes_annuelles["Année 3"]
        ]
        moyennes_annees_valides = [m for m in moyennes_annees if m > 0]
        moyenne_generale = round(sum(moyennes_annees_valides) / len(moyennes_annees_valides), 2) if moyennes_annees_valides else 0
        
        # ==========================================
        # 7. STATISTIQUES GLOBALES
        # ==========================================
        total_matieres = len(resultats_list)
        matieres_validees = sum(1 for r in resultats_list if r['is_validated'])
        total_credits = sum(r['credits'] for r in resultats_list if r['is_validated'])
        total_credits_possibles = sum(r['credits'] for r in resultats_list)
        
        # ==========================================
        # 8. RÉPONSE COMPLÈTE
        # ==========================================
        return Response({
            'etudiant': {
                'id': user.id,
                'username': user.username,
                'nom_complet': nom_complet,
                'prenom': prenom,
                'nom': nom,
                'niveau': niveau,
                'specialite': specialite,
                'specialite_code': specialite_code,
                'groupe': groupe_nom
            },
            'resultats': resultats_list,
            'moyennes_semestres': moyennes_semestres,
            'credits_semestres': credits_semestres,
            'moyennes_annuelles': moyennes_annuelles,
            'moyenne_generale': moyenne_generale,
            'total_matieres': total_matieres,
            'matieres_validees': matieres_validees,
            'total_credits': total_credits,
            'total_credits_possibles': total_credits_possibles,
            'is_valide': moyenne_generale >= 10
        })


class StudentsByTeacherDepartmentView(APIView):
    """Récupère tous les étudiants du département de l'enseignant"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role != 'enseignant':
            return Response({"error": "Non autorisé - Réservé aux enseignants"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        teacher_dept = None
        if hasattr(user, 'teacher_profile') and user.teacher_profile:
            teacher_dept = user.teacher_profile.department
        
        if not teacher_dept:
            return Response({"error": "Vous n'êtes pas assigné à un département"}, 
                          status=status.HTTP_200_OK)
        
        groupes = Groupe.objects.filter(department=teacher_dept)
        students = StudentProfile.objects.filter(
            groupe__in=groupes
        ).select_related('user', 'groupe')
        
        resultats_data = []
        for student in students:
            groupe_nom = "N/A"
            if student.groupe:
                if hasattr(student.groupe, 'name'):
                    groupe_nom = student.groupe.name
                elif hasattr(student.groupe, 'nom'):
                    groupe_nom = student.groupe.nom
                else:
                    groupe_nom = str(student.groupe)
            
            resultats_data.append({
                'id': student.user.id,
                'username': student.user.username,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'groupe_nom': groupe_nom,
                'groupe_level': student.groupe.level if student.groupe and hasattr(student.groupe, 'level') else None,
                'matricule': getattr(student, 'matricule', ''),
            })
        
        return Response(resultats_data)