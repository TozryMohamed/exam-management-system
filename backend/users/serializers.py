# users/serializers.py - CODE COMPLET CORRIGÉ

from rest_framework import serializers
from .models import User, StudentProfile, TeacherProfile, Department, Groupe
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import datetime
import random
import string


def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=length))


def get_logo_url():
    if settings.DEBUG:
        return f"{settings.STATIC_URL}images/isaat.png"
    else:
        return staticfiles_storage.url('images/isaat.png')


def send_account_creation_email(email, username, password, role, full_name=""):
    current_year = datetime.now().year
    next_year = current_year + 1
    
    role_fr = {
        'admin': 'Administrateur',
        'enseignant': 'Enseignant',
        'etudiant': 'Étudiant'
    }.get(role, 'Utilisateur')
    
    subject = "🎓 Bienvenue sur la Plateforme d'Examens - ISATT Kasserine"
    logo_url = get_logo_url()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenue - ISATT Kasserine</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            .header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .logo-container {{
                text-align: center;
                margin-bottom: 15px;
            }}
            .logo {{
                max-width: 80px;
                height: auto;
                border-radius: 50%;
                background: white;
                padding: 10px;
            }}
            .header h1 {{
                margin: 10px 0 0;
                font-size: 24px;
            }}
            .header p {{
                margin: 5px 0 0;
                font-size: 14px;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px 25px;
            }}
            .greeting {{
                font-size: 18px;
                color: #1e3c72;
                margin-bottom: 20px;
                font-weight: 500;
            }}
            .credentials-box {{
                background-color: #f8f9fa;
                border-left: 4px solid #2a5298;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .warning-box {{
                background-color: #fff3e0;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #ff9800;
            }}
            .info-box {{
                background-color: #e8f0fe;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #2a5298;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #e0e0e0;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin: 10px 0;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-container">
                    <img src="{logo_url}" alt="ISATT Kasserine" class="logo">
                </div>
                <h1>🏫 Institut Supérieur des Arts et Métiers</h1>
                <p>Kasserine - Service des Examens</p>
                <p><strong>Plateforme de Gestion des Examens</strong></p>
            </div>
            
            <div class="content">
                <div class="greeting">
                    👋 Bonjour {full_name if full_name else username},
                </div>
                
                <p>Nous avons le plaisir de vous confirmer la création de votre compte sur la <strong>Plateforme de Gestion des Examens de l'ISATT Kasserine</strong>.</p>
                
                <div class="credentials-box">
                    <h4>🔑 Vos identifiants de connexion :</h4>
                    <p><strong>👤 Nom d'utilisateur :</strong> <code>{username}</code></p>
                    <p><strong>🔒 Mot de passe :</strong> <code>{password}</code></p>
                    <p><strong>📧 Email :</strong> {email}</p>
                    <p><strong>🎯 Rôle :</strong> {role_fr}</p>
                </div>
                
                <div class="info-box">
                    <strong>⏳ Activation du compte :</strong><br>
                    Votre compte a été créé avec succès mais est actuellement <strong>en attente d'activation</strong> par l'administrateur.<br>
                    Vous recevrez un email dès que votre compte sera activé.
                </div>
                
                <div class="warning-box">
                    <strong>⚠️ Recommandations importantes :</strong><br>
                    • 🔐 Changez votre mot de passe après votre première connexion<br>
                    • 🤫 Ne communiquez jamais vos identifiants à un tiers<br>
                    • 🔄 Utilisez la fonction "Mot de passe oublié" en cas de perte
                </div>
                
                <center>
                    <a href="http://localhost:3000/login" class="button">🚀 Accéder à la plateforme</a>
                </center>
            </div>
            
            <div class="footer">
                <p><strong>Service des Examens - ISATT Kasserine</strong></p>
                <p>© {current_year} ISATT Kasserine - Université de Kairouan. Tous droits réservés.</p>
                <p><em>Ce message est généré automatiquement, merci de ne pas y répondre.</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    ═══════════════════════════════════════════════════════════
        **ISATT KASSERINE - SERVICE DES EXAMENS**
    ═══════════════════════════════════════════════════════════
    
    Bonjour {full_name if full_name else username},
    
    Votre compte a été créé avec succès.
    
    👤 Nom d'utilisateur : {username}
    🔒 Mot de passe : {password}
    🎯 Rôle : {role_fr}
    
    ⏳ STATUT : En attente d'activation par l'administrateur
    
    🔗 Accès : http://localhost:3000/login
    
    ═══════════════════════════════════════════════════════════
    """
    
    try:
        send_mail(subject, text_content, settings.EMAIL_HOST_USER, [email], html_message=html_content, fail_silently=False)
        print(f"✅ Email envoyé à {email}")
        return True
    except Exception as e:
        print(f"❌ Erreur email: {str(e)}")
        return False


# ============================================================
# SERIALIZERS (SANS IMPORT CIRCULAIRE)
# ============================================================

# 1. FORGOT PASSWORD SERIALIZER
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


# 2. RESET PASSWORD SERIALIZER
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        return data


# 3. REGISTER SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    groupe_id = serializers.IntegerField(required=False, allow_null=True)
    specialite = serializers.CharField(required=False, allow_blank=True)
    telephone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "cin",
            "role",
            "password",
            "telephone",
            "groupe_id",
            "specialite"
        ]

    def create(self, validated_data):
        groupe_id = validated_data.pop("groupe_id", None)
        specialite = validated_data.pop("specialite", "")
        password = validated_data.pop("password", None)

        if not password or password.strip() == "":
            password = generate_password()

        user = User.objects.create_user(
            password=password,
            is_active=False,
            **validated_data
        )

        if user.role == "etudiant":
            StudentProfile.objects.create(
                user=user,
                groupe_id=groupe_id if groupe_id else None
            )
        elif user.role == "enseignant":
            TeacherProfile.objects.create(
                user=user,
                specialite=specialite if specialite else ""
            )

        full_name = f"{user.first_name} {user.last_name}".strip()
        send_account_creation_email(user.email, user.username, password, user.role, full_name)

        return user


# 4. USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    groupe_id = serializers.SerializerMethodField()
    department_id = serializers.SerializerMethodField()
    groupe_name = serializers.SerializerMethodField()
    specialite_id = serializers.SerializerMethodField()
    specialite_name = serializers.SerializerMethodField()
    groupe_level = serializers.SerializerMethodField()
    specialite = serializers.SerializerMethodField()
    
    groupe_id_input = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    specialite_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'cin', 'role', 'telephone', 'password', 'is_active',
            'date_joined', 'last_login',
            'groupe_id', 'groupe_id_input', 'groupe_name', 
            'department_id',
            'specialite_id',
            'specialite_name',
            'groupe_level',
            'specialite',
            'specialite_input'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'cin': {'required': False},
            'role': {'required': False},
            'is_active': {'required': False},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True},
        }

    def get_groupe_id(self, obj):
        if obj.role == "etudiant" and hasattr(obj, "studentprofile") and obj.studentprofile.groupe:
            return obj.studentprofile.groupe.id
        return None

    def get_groupe_name(self, obj):
        if obj.role == "etudiant" and hasattr(obj, "studentprofile") and obj.studentprofile.groupe:
            return obj.studentprofile.groupe.name
        return None

    def get_department_id(self, obj):
        if obj.role == "etudiant" and hasattr(obj, "studentprofile") and obj.studentprofile.groupe:
            if obj.studentprofile.groupe.department:
                return obj.studentprofile.groupe.department.id
        return None

    def get_specialite_id(self, obj):
        if obj.role == "etudiant" and hasattr(obj, "studentprofile") and obj.studentprofile.groupe:
            groupe = obj.studentprofile.groupe
            if hasattr(groupe, 'specialite') and groupe.specialite:
                return groupe.specialite.id
        return None

    def get_specialite_name(self, obj):
        if obj.role == "etudiant" and hasattr(obj, "studentprofile") and obj.studentprofile.groupe:
            groupe = obj.studentprofile.groupe
            if hasattr(groupe, 'specialite') and groupe.specialite:
                return groupe.specialite.nom
        return None

    def get_groupe_level(self, obj):
        if obj.role == "etudiant" and hasattr(obj, "studentprofile") and obj.studentprofile.groupe:
            niveau = obj.studentprofile.groupe.level
            if niveau:
                return niveau
        return None

    def get_specialite(self, obj):
        if obj.role == "enseignant" and hasattr(obj, "teacherprofile"):
            return obj.teacherprofile.specialite
        return None

    def update(self, instance, validated_data):
        groupe_id = validated_data.pop('groupe_id_input', None)
        specialite_input = validated_data.pop('specialite_input', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            if attr not in ['role']:
                setattr(instance, attr, value)
        
        if password and password.strip():
            instance.set_password(password)
        
        instance.save()
        
        if instance.role == "etudiant" and groupe_id is not None:
            try:
                groupe = Groupe.objects.get(id=groupe_id) if groupe_id else None
                profile, created = StudentProfile.objects.get_or_create(user=instance)
                profile.groupe = groupe
                profile.save()
            except Groupe.DoesNotExist:
                pass
        
        if instance.role == "enseignant" and specialite_input is not None:
            try:
                if hasattr(instance, 'teacherprofile') and instance.teacherprofile:
                    instance.teacherprofile.specialite = specialite_input if specialite_input else ""
                    instance.teacherprofile.save()
                else:
                    TeacherProfile.objects.create(
                        user=instance,
                        specialite=specialite_input if specialite_input else ""
                    )
            except Exception as e:
                pass
        
        return instance


# 5. LOGIN SERIALIZER
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# 6. LOGOUT SERIALIZER
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


# 7. DEPARTMENT SERIALIZER
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


# 8. GROUPE SERIALIZER
class GroupeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    specialite_id = serializers.IntegerField(source='specialite.id', read_only=True, allow_null=True)
    specialite_nom = serializers.CharField(source='specialite.nom', read_only=True, allow_null=True)

    class Meta:
        model = Groupe
        fields = [
            'id', 'name', 'level',
            'department', 'department_name', 'department_code',
            'specialite_id', 'specialite_nom',
        ]


# 9. STUDENT LIST SERIALIZER
class StudentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    groupe = serializers.IntegerField()
    groupe_nom = serializers.CharField()