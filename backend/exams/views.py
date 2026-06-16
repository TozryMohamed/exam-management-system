from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Exam, Salle
from .serializers import ExamSerializer, SalleSerializer

User = get_user_model()

# =========================
# EXAMS
# =========================

from django.db.models import Q
from rest_framework import generics
from .models import Exam

class ExamListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Exam.objects.all()
        
        niveau = self.request.query_params.get('niveau')
        specialite_id = self.request.query_params.get('specialite_id')
        
        # Filtrer par niveau
        if niveau and niveau != 'undefined' and niveau != 'null':
            queryset = queryset.filter(niveau=niveau)
        
        # Filtrer par spécialité - IGNORER si undefined ou null
        if specialite_id and specialite_id != 'undefined' and specialite_id != 'null':
            try:
                specialite_id_int = int(specialite_id)
                queryset = queryset.filter(
                    Q(specialite_id=specialite_id_int) | Q(specialite_id__isnull=True)
                )
            except (ValueError, TypeError):
                pass  # Ignorer les valeurs invalides
        
        return queryset


class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


# =========================
# SALLES
# =========================

class SalleListCreateView(generics.ListCreateAPIView):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer
    permission_classes = [IsAuthenticated]






# =========================
# TEACHERS 👨‍🏫
# =========================

@api_view(["GET"])
def teachers_list(request):
    teachers = User.objects.filter(role="enseignant")

    data = [
        {"id": t.id, "username": t.username}
        for t in teachers
    ]

    return Response(data)



