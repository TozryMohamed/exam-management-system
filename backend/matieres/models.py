# # matieres/models.py
# from django.db import models
# from django.conf import settings
# from users.models import Department  # 👈 Importer Department


# class Specialite(models.Model):
#     """Spécialité (filière)"""
#     code = models.CharField(max_length=20, unique=True)
#     nom = models.CharField(max_length=200)
    
#     # 👇 NOUVEAU : Lien avec Department
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.CASCADE,
#         related_name="specialites",
#         null=True,
#         blank=True
#     )
    
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         dept_name = f" - {self.department.nom}" if self.department else ""
#         return f"{self.code} - {self.nom}{dept_name}"


# class Matiere(models.Model):
#     NATURE_CHOICES = [
#         ('MX', 'Matière de Base'),
#         ('CC', 'Contrôle Continu'),
#         ('TP', 'Travaux Pratiques'),
#         ('TD', 'Travaux Dirigés'),
#     ]
    
#     code = models.CharField(max_length=20, unique=True)
#     titre = models.CharField(max_length=200)
#     credits = models.IntegerField(default=3)
#     coefficient = models.IntegerField(default=1)
#     nature = models.CharField(max_length=2, choices=NATURE_CHOICES, default='MX')
    
#     # Relation avec spécialité
#     specialite = models.ForeignKey(
#         Specialite,
#         on_delete=models.CASCADE,
#         related_name="matieres"
#     )
    
#     # Enseignant responsable (optionnel)
#     enseignant = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="matieres_enseignees",
#         limit_choices_to={'role': 'enseignant'}
#     )
    
#     semestre = models.IntegerField(
#         choices=[(1, 'Semestre 1'), (2, 'Semestre 2'), (3, 'Semestre 3'), 
#                  (4, 'Semestre 4'), (5, 'Semestre 5'), (6, 'Semestre 6')], 
#         null=True, blank=True
#     )
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['specialite', 'semestre', 'code']
    
#     def __str__(self):
#         return f"{self.code} - {self.titre} ({self.specialite.code})"



from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import Department  # 👈 Le SEUL import nécessaire


class Specialite(models.Model):
    """Spécialité (filière)"""
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=200)
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="specialites",
        null=True,
        blank=True
    )
    
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "Spécialité"
        verbose_name_plural = "Spécialités"
    
    def __str__(self):
        dept_name = f" - {self.department.name if hasattr(self.department, 'name') else self.department.nom}" if self.department else ""
        return f"{self.code} - {self.nom}{dept_name}"


class Matiere(models.Model):
    """Matière universitaire avec niveau d'étude"""
    
    NATURE_CHOICES = [
        ('MX', 'Matière de Base'),
        ('CC', 'Contrôle Continu'),
        ('TP', 'Travaux Pratiques'),
        ('TD', 'Travaux Dirigés'),
    ]
    
    NIVEAU_CHOICES = [
        (1, 'Niveau 1 (L1)'),
        (2, 'Niveau 2 (L2)'),
        (3, 'Niveau 3 (L3)'),
    ]
    
    SEMESTRE_CHOICES = [
        (1, 'Semestre 1'),
        (2, 'Semestre 2'),
        (3, 'Semestre 3'),
        (4, 'Semestre 4'),
        (5, 'Semestre 5'),
        (6, 'Semestre 6'),
    ]
    
    # Identifiants
    code = models.CharField(max_length=20, unique=True)
    titre = models.CharField(max_length=200)
    
    # Caractéristiques académiques
    credits = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(30)])
    coefficient = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    nature = models.CharField(max_length=2, choices=NATURE_CHOICES, default='MX')
    
    # NOUVEAU : Niveau d'étude
    niveau = models.IntegerField(
        choices=NIVEAU_CHOICES,
        default=1,
        help_text="Niveau d'étude auquel cette matière est enseignée"
    )
    
    # Semestre (conserve la granularité)
    semestre = models.IntegerField(
        choices=SEMESTRE_CHOICES,
        null=True, 
        blank=True,
        help_text="Semestre spécifique dans le niveau"
    )
    
    # Relations
    specialite = models.ForeignKey(
        Specialite,
        on_delete=models.CASCADE,
        related_name="matieres"
    )
    
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matieres_enseignees",
        limit_choices_to={'role': 'enseignant'}
    )
    
    # Métadonnées
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['specialite', 'niveau', 'semestre', 'code']
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        unique_together = ['code', 'specialite', 'niveau']
    
    def __str__(self):
        return f"{self.code} - {self.titre} ({self.get_niveau_display()})"
    
    @property
    def niveau_from_semestre(self):
        """Calcule automatiquement le niveau à partir du semestre si non défini"""
        if self.niveau:
            return self.niveau
        if self.semestre:
            return (self.semestre + 1) // 2
        return None
    
    @classmethod
    def get_niveau_from_semestre(cls, semestre):
        """Utilitaire de classe pour calculer le niveau depuis un semestre"""
        return (semestre + 1) // 2 if semestre else None

# 🔴 STOP ! RIEN D'AUTRE après cette ligne dans models.py
# Le code de views.py doit être dans views.py, PAS ICI !