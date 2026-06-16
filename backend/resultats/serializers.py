# from rest_framework import serializers
# from .models import ResultatMatiere


# class ResultatMatiereSerializer(serializers.ModelSerializer):
#     matiere_code = serializers.CharField(source='matiere.code', read_only=True)
#     matiere_nom = serializers.CharField(source='matiere.titre', read_only=True)
#     etudiant_nom = serializers.SerializerMethodField()

#     class Meta:
#         model = ResultatMatiere
#         fields = [
#             'id', 'etudiant', 'etudiant_nom', 'matiere', 'matiere_code', 'matiere_nom',
#             'session', 'oral', 'ds', 'exam', 'tp', 'exam_r',
#             'moyenne', 'is_validated', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['moyenne', 'is_validated', 'created_at', 'updated_at']

#     def get_etudiant_nom(self, obj):
#         return f"{obj.etudiant.first_name} {obj.etudiant.last_name}"




# resultats/serializers.py
from rest_framework import serializers
from .models import ResultatMatiere


class ResultatMatiereSerializer(serializers.ModelSerializer):
    matiere_code = serializers.CharField(source='matiere.code', read_only=True)
    matiere_nom = serializers.CharField(source='matiere.titre', read_only=True)
    matiere_coefficient = serializers.FloatField(source='matiere.coefficient', read_only=True)
    matiere_credits = serializers.IntegerField(source='matiere.credits', read_only=True)
    matiere_semestre = serializers.IntegerField(source='matiere.semestre', read_only=True)
    matiere_nature = serializers.CharField(source='matiere.nature', read_only=True)
    etudiant_nom = serializers.SerializerMethodField()

    class Meta:
        model = ResultatMatiere
        fields = [
            'id', 'etudiant', 'etudiant_nom', 'matiere',
            'matiere_code', 'matiere_nom', 'matiere_coefficient',
            'matiere_credits', 'matiere_semestre', 'matiere_nature',
            'session', 'oral', 'ds', 'exam', 'tp', 'exam_r',
            'moyenne', 'moyenne_finale', 'is_validated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['moyenne', 'moyenne_finale', 'is_validated', 'created_at', 'updated_at']

    def get_etudiant_nom(self, obj):
        return f"{obj.etudiant.first_name} {obj.etudiant.last_name}".strip() or obj.etudiant.username