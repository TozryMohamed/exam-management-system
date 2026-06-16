# # resultats/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     # Matieres de l'enseignant (dans resultats car on ne touche pas matieres)
#     path('matieres/my/', views.my_matieres, name='my-matieres'),
    
#     # Étudiants par matière
#     path('groupes/students/', views.students_by_matiere, name='students-by-matiere'),
    
#     # Résultats
#     path('create/', views.create_resultat, name='create-resultat'),
#     path('my/', views.my_resultats, name='my-resultats'),
#     path('moyenne/', views.moyenne_etudiant, name='moyenne-etudiant'),
# ]




# ver fonctionnel 

from django.urls import path
from . import views

urlpatterns = [
    # Matières de l'enseignant
    path('matieres/my/', views.MatieresByTeacherView.as_view(), name='my-matieres'),
    
    # Étudiants par matière (pour saisie des notes)
    path('groupes/students/', views.StudentsByMatiereAndGroupesView.as_view(), name='groupes-students'),
    
    # Étudiants par département
    path('students/by-department/', views.StudentsByTeacherDepartmentView.as_view(), name='students-by-department'),
    
    # Création/modification de notes
    path('create/', views.CreateOrUpdateNoteView.as_view(), name='create-note'),
    
    # Dashboard étudiant
    path('my/', views.StudentNotesView.as_view(), name='my-notes'),
]