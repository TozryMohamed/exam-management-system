from rest_framework import serializers
from .models import Specialite, Matiere


class SpecialiteSerializer(serializers.ModelSerializer):
    matieres_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Specialite
        fields = '__all__'
    
    def get_matieres_count(self, obj):
        return obj.matieres.count()
    
    def to_representation(self, instance):
        """Ajoute le nom du département dans la représentation"""
        data = super().to_representation(instance)
        if instance.department:
            # Essaie d'abord .nom, puis .name
            data['department_nom'] = getattr(instance.department, 'nom', 
                                            getattr(instance.department, 'name', 'Non assigné'))
        else:
            data['department_nom'] = "Non assigné"
        return data


class MatiereSerializer(serializers.ModelSerializer):
    specialite_nom = serializers.SerializerMethodField()
    specialite_code = serializers.SerializerMethodField()
    enseignant_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Matiere
        fields = '__all__'
    
    def get_specialite_nom(self, obj):
        return obj.specialite.nom if obj.specialite else None
    
    def get_specialite_code(self, obj):
        return obj.specialite.code if obj.specialite else None
    
    def get_enseignant_nom(self, obj):
        if obj.enseignant:
            return f"{obj.enseignant.first_name} {obj.enseignant.last_name}"
        return "Non assigné"
    
    def to_representation(self, instance):
        """Ajoute le nom du département dans la représentation"""
        data = super().to_representation(instance)
        if instance.specialite and instance.specialite.department:
            # Essaie d'abord .nom, puis .name
            data['department_nom'] = getattr(instance.specialite.department, 'nom', 
                                            getattr(instance.specialite.department, 'name', 'Non assigné'))
        else:
            data['department_nom'] = "Non assigné"
        return data