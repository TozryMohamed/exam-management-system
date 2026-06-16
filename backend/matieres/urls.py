from django.urls import path
from .views import (
    SpecialiteListCreateView, 
    SpecialiteDetailView,
    MatiereListCreateView, 
    MatiereDetailView,
    MatieresByStudentDepartmentView,
    # 🔥 Nouvelles vues pour le filtrage avancé
)

urlpatterns = [
    # Specialites
    path("specialites/", SpecialiteListCreateView.as_view(), name='specialites-list'),
    path("specialites/<int:pk>/", SpecialiteDetailView.as_view(), name='specialites-detail'),
    
    # Matieres
    path("matieres/", MatiereListCreateView.as_view(), name='matieres-list'),
    path("matieres/<int:pk>/", MatiereDetailView.as_view(), name='matieres-detail'),
    path("matieres/by-student-department/", MatieresByStudentDepartmentView.as_view(), 
         name='matieres-by-student-department'),
]