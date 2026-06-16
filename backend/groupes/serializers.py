# groups/serializers.py
from rest_framework import serializers
from .models import GroupeEtudiant, RepartitionExamen, RepartitionDetail


class GroupeEtudiantSerializer(serializers.ModelSerializer):
    specialite_nom = serializers.CharField(source='specialite.nom', read_only=True)
    
    class Meta:
        model = GroupeEtudiant
        fields = ['id', 'nom', 'effectif', 'niveau', 'specialite', 'specialite_nom', 'created_at', 'updated_at']


class RepartitionDetailSerializer(serializers.ModelSerializer):
    user_nom = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = RepartitionDetail
        fields = ['id', 'repartition', 'user', 'user_nom', 'user_username', 'place_number', 'seat_code', 'student_index', 'created_at']


class RepartitionExamenSerializer(serializers.ModelSerializer):
    details = RepartitionDetailSerializer(many=True, read_only=True)
    salle_nom = serializers.CharField(source='salle.name', read_only=True)
    salle_type = serializers.CharField(source='salle.type', read_only=True)
    groupe_nom = serializers.CharField(source='groupe.nom', read_only=True)
    
    class Meta:
        model = RepartitionExamen
        fields = ['id', 'examen', 'groupe', 'groupe_nom', 'salle', 'salle_nom', 'salle_type', 'effectif', 'details', 'created_at', 'updated_at']