from django.contrib.auth.models import AbstractUser
from django.db import models


# ============= DEPARTEMENT =============
class Department(models.Model):
    """Département"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name


# ============= GROUPE =============
class Groupe(models.Model):
    """Groupe d'étudiants (classe)"""
    LEVEL_CHOICES = (
        ('1', 'Niveau 1'),
        ('2', 'Niveau 2'),
        ('3', 'Niveau 3'),
        ('4', 'Niveau 4'),
        ('5', 'Niveau 5'),
    )
    
    name = models.CharField(max_length=100)  # Ex: "GLSI 1", "ISI 2"
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="groupes")
    
    def __str__(self):
        return f"{self.name}"


# ============= USER =============
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Etudiant'),
    )

    cin = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, null=True, blank=True)


# ============= STUDENT PROFILE (CORRIGÉ) =============
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="studentprofile")
    groupe = models.ForeignKey(Groupe, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")

    def __str__(self):
        return f"{self.user.username} - {self.groupe.name if self.groupe else 'Sans groupe'}"


# ============= TEACHER PROFILE =============
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacherprofile")
    specialite = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username