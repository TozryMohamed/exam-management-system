from rest_framework import serializers
from .models import Exam, Salle

class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = "__all__"


class ExamSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_id = serializers.IntegerField(source='teacher.id', read_only=True)  # 🔑 AJOUTER teacher_id
    salle_name = serializers.SerializerMethodField()
    salle_id = serializers.IntegerField(source='salle.id', read_only=True)  # 🔑 AJOUTER salle_id
    specialite_nom = serializers.SerializerMethodField()
    specialite_id = serializers.IntegerField(source='specialite.id', read_only=True)  # 🔑 AJOUTER specialite_id
    niveau_display = serializers.SerializerMethodField()
    semestre_display = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = "__all__"
        extra_kwargs = {
            'specialite': {'required': False},
            'niveau': {'required': False},
            'semestre': {'required': False},
        }

    def get_teacher_name(self, obj):
        return obj.teacher.username if obj.teacher else "Aucun enseignant"

    def get_salle_name(self, obj):
        if obj.salle:
            return f"{obj.salle.type} {obj.salle.name}"
        return "Aucune salle"

    def get_specialite_nom(self, obj):
        return obj.specialite.nom if obj.specialite else None

    def get_niveau_display(self, obj):
        return dict(Exam._meta.get_field('niveau').choices).get(obj.niveau, obj.niveau) if obj.niveau else None

    def get_semestre_display(self, obj):
        return f"Semestre {obj.semestre}" if obj.semestre else None

    def validate(self, data):
        date = data.get("date")
        time = data.get("time")
        salle = data.get("salle")
        teacher = data.get("teacher")
        
        instance = self.instance
        errors = {}

        # Vérifier les champs requis
        if not data.get('specialite'):
            errors["specialite"] = "La spécialité est requise"
        if not data.get('niveau'):
            errors["niveau"] = "L'année est requise"
        if not data.get('semestre'):
            errors["semestre"] = "Le semestre est requis"

        # Conflit salle
        if salle and date and time:
            existing = Exam.objects.filter(date=date, time=time, salle=salle)
            if instance:
                existing = existing.exclude(id=instance.id)
            if existing.exists():
                errors["salle"] = "🚨 Cette salle est déjà réservée à ce créneau."

        # Conflit enseignant
        if teacher and date and time:
            existing = Exam.objects.filter(date=date, time=time, teacher=teacher)
            if instance:
                existing = existing.exclude(id=instance.id)
            if existing.exists():
                errors["teacher"] = "🚨 Cet enseignant a déjà un examen à ce moment."

        if errors:
            raise serializers.ValidationError(errors)

        return data