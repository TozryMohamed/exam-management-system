from django.db import models
from django.conf import settings
from matieres.models import Specialite

class Salle(models.Model):
    TYPE_CHOICES = [
        ("salle", "Salle"),
        ("amphi", "Amphi"),
    ]

    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="salle")

    def __str__(self):
        return f"{self.type} {self.name}"


class Exam(models.Model):
    NIVEAU_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
    ]
    
    SEMESTRE_CHOICES = [
        (1, 'Semestre 1'),
        (2, 'Semestre 2'),
    ]

    title = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()

    specialite = models.ForeignKey(
        Specialite,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Spécialité"
    )
    niveau = models.CharField(
        max_length=10,
        choices=NIVEAU_CHOICES,
        null=True,
        blank=True,
        verbose_name="Année"
    )
    semestre = models.IntegerField(
        choices=SEMESTRE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Semestre"
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exams"
    )

    salle = models.ForeignKey(
        Salle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        specialite_str = f" - {self.specialite.nom}" if self.specialite else ""
        niveau_str = f" ({self.niveau})" if self.niveau else ""
        return f"{self.title}{specialite_str}{niveau_str}"