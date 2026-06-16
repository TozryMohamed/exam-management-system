from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Specialite, Matiere
from .serializers import SpecialiteSerializer, MatiereSerializer


# ===================== SPECIALITES =====================
class SpecialiteListCreateView(generics.ListCreateAPIView):
    queryset = Specialite.objects.all()
    serializer_class = SpecialiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class SpecialiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Specialite.objects.all()
    serializer_class = SpecialiteSerializer
    permission_classes = [permissions.IsAuthenticated]


# ===================== MATIERES =====================
class MatiereListCreateView(generics.ListCreateAPIView):
    serializer_class = MatiereSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrage optimisé avec select_related
        """
        queryset = Matiere.objects.select_related(
            'specialite', 
            'specialite__department',
            'enseignant'
        ).all()
        
        # Filtre par spécialité
        specialite_id = self.request.query_params.get('specialite')
        if specialite_id:
            queryset = queryset.filter(specialite_id=specialite_id)
        
        # Filtre par code de spécialité
        specialite_code = self.request.query_params.get('specialite_code')
        if specialite_code:
            queryset = queryset.filter(specialite__code__iexact=specialite_code)
        
        # 🔥 NOUVEAU : Filtre par niveau
        niveau = self.request.query_params.get('niveau')
        if niveau:
            queryset = queryset.filter(niveau=int(niveau))
        
        # 🔥 NOUVEAU : Filtre par département
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(
                specialite__department_id=int(department_id)
            )


        semestre = self.request.query_params.get('semestre')
        if semestre:
            queryset = queryset.filter(semestre=int(semestre))
        
        return queryset


class MatiereDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Matiere.objects.select_related(
        'specialite', 
        'specialite__department',
        'enseignant'
    ).all()
    serializer_class = MatiereSerializer
    permission_classes = [permissions.IsAuthenticated]


class MatieresByStudentDepartmentView(APIView):
    """
    🔥 AMÉLIORÉ : Récupère les matières filtrées par :
    - Département de l'étudiant
    - Niveau de l'étudiant (basé sur son groupe)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Vérifier que l'utilisateur est un étudiant
        if not hasattr(user, 'student_profile'):
            return Response(
                {"error": "Seuls les étudiants peuvent accéder à cet endpoint"}, 
                status=403
            )
        
        student = user.student_profile
        
        # Vérifier que l'étudiant a un groupe
        if not student.groupe:
            return Response(
                {"error": "L'étudiant n'est pas assigné à un groupe"}, 
                status=400
            )
        
        student_group = student.groupe
        student_department = student_group.department
        student_level = student_group.level  # 🔥 Récupération du niveau
        
        # 🔥 Filtrage par département ET niveau
        matieres = Matiere.objects.filter(
            specialite__department=student_department,
            niveau=student_level  # Filtrer par le niveau de l'étudiant
        ).select_related(
            'specialite', 
            'specialite__department', 
            'enseignant'
        ).order_by('semestre', 'code')
        
        # Option : si pas de résultats, retourner toutes les matières du département
        if not matieres.exists():
            matieres = Matiere.objects.filter(
                specialite__department=student_department
            ).select_related(
                'specialite', 
                'specialite__department', 
                'enseignant'
            ).order_by('niveau', 'semestre', 'code')
        
        serializer = MatiereSerializer(matieres, many=True)
        
        return Response({
            'student_info': {
                'name': f"{user.first_name} {user.last_name}",
                'department': getattr(student_department, 'nom', 
                                     getattr(student_department, 'name', 'Inconnu')),
                'level': student_level
            },
            'count': matieres.count(),
            'matieres': serializer.data
        })