# groups/models.py - Version CORRIGÉE (sans les tables d'historique)

from django.db import models
from exams.models import Exam, Salle


class GroupeEtudiant(models.Model):
    """Modèle pour les groupes d'étudiants"""
    nom = models.CharField(max_length=100)
    effectif = models.IntegerField(default=0)
    niveau = models.CharField(max_length=10, blank=True, null=True)
    specialite = models.ForeignKey('matieres.Specialite', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nom} ({self.effectif} étudiants)"


class RepartitionExamen(models.Model):
    """Répartition d'un groupe pour un examen dans une salle"""
    examen = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='repartitions')
    groupe = models.ForeignKey(GroupeEtudiant, on_delete=models.CASCADE, related_name='repartitions')
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name='repartitions')
    effectif = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['examen', 'groupe', 'salle']
    
    def __str__(self):
        return f"{self.examen.title} - {self.groupe.nom} -> {self.salle.name}"


class RepartitionDetail(models.Model):
    """Détail des places pour chaque répartition"""
    repartition = models.ForeignKey(RepartitionExamen, on_delete=models.CASCADE, related_name='details')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    place_number = models.IntegerField()
    seat_code = models.CharField(max_length=10)
    student_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['repartition', 'place_number']
    
    def __str__(self):
        return f"{self.repartition} - Place {self.seat_code}"