from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import User, Department, Groupe
from .serializers import (
    RegisterSerializer, UserSerializer, 
    DepartmentSerializer, GroupeSerializer
)

User = get_user_model()


# ===================== REGISTER =====================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ===================== LOGIN (CORRIGÉ) =====================
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        # Compte activé
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "user_id": user.id,
                "username": user.username
            })

        # Compte non activé
        if user and not user.is_active:
            return Response({
                "error": "Votre compte est en attente d'activation par l'administrateur. Veuillez réessayer plus tard."
            }, status=403)

        # Identifiants invalides
        return Response({
            "error": "Identifiants invalides. Vérifiez votre nom d'utilisateur et mot de passe."
        }, status=400)


# ===================== ME (PROFILE) =====================
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "cin": user.cin,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "telephone": user.telephone,
        }
        
        if user.role == "etudiant" and hasattr(user, "studentprofile"):
            student = user.studentprofile
            data["groupe_id"] = student.groupe.id if student.groupe else None
            data["groupe_name"] = student.groupe.name if student.groupe else None
            data["groupe_level"] = student.groupe.level if student.groupe else None
            
        elif user.role == "enseignant":
            if hasattr(user, "teacherprofile") and user.teacherprofile:
                data["specialite"] = user.teacherprofile.specialite
            else:
                data["specialite"] = None
        
        return Response(data)


# ===================== FORGOT PASSWORD =====================
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()

        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=400)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:3000/reset-password/{uid}/{token}"

        send_mail(
            "Reset Password",
            f"Click here to reset your password:\n{reset_link}",
            "noreply@system.com",
            [email],
        )

        return Response({"message": "Reset link sent"})


# ===================== RESET PASSWORD =====================
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        password = request.data.get("password")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token"}, status=400)

        user.set_password(password)
        user.save()

        return Response({"message": "Password updated successfully"})


# ===================== USER VIEWSET =====================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Transformer les données: 'specialite' -> 'specialite_input'
        data = request.data.copy()
        if 'specialite' in data:
            data['specialite_input'] = data.pop('specialite')
        
        # Transformer: 'groupe_id' -> 'groupe_id_input'
        if 'groupe_id' in data:
            data['groupe_id_input'] = data.pop('groupe_id')
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, partial=True, *args, **kwargs)


# ===================== DEPARTMENT VIEWSET =====================
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]


# ===================== GROUPE VIEWSET =====================
class GroupeViewSet(viewsets.ModelViewSet):
    queryset = Groupe.objects.all()
    serializer_class = GroupeSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset


# ===================== STUDENTS BY GROUP =====================
class StudentsByGroupView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        groupe_id = request.query_params.get('groupe')
        department_id = request.query_params.get('department')
        
        students = User.objects.filter(role='etudiant', studentprofile__isnull=False)
        
        if groupe_id:
            students = students.filter(studentprofile__groupe_id=groupe_id)
        
        if department_id:
            students = students.filter(studentprofile__groupe__department_id=department_id)
        
        result = []
        for student in students:
            profile = student.studentprofile
            groupe = profile.groupe
            result.append({
                "id": student.id,
                "nom": student.last_name or "",
                "prenom": student.first_name or "",
                "groupe": groupe.id if groupe else None,
                "groupe_nom": groupe.name if groupe else "Non assigné"
            })
        
        return Response(result)


# ===================== ADMIN STATS =====================
class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from exams.models import Exam, Salle
        from django.utils import timezone
        
        total_users = User.objects.count()
        total_students = User.objects.filter(role="etudiant").count()
        total_teachers = User.objects.filter(role="enseignant").count()
        total_exams = Exam.objects.count()
        total_rooms = Salle.objects.count()
        upcoming_exams = Exam.objects.filter(date__gte=timezone.now().date()).count()

        return Response({
            "totalUsers": total_users,
            "totalStudents": total_students,
            "totalTeachers": total_teachers,
            "totalExams": total_exams,
            "totalRooms": total_rooms,
            "upcomingExams": upcoming_exams,
        })


# ===================== RECENT ACTIVITIES =====================
class RecentActivitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from exams.models import Exam
        
        activities = []

        recent_exams = Exam.objects.order_by("-id")[:5]
        for exam in recent_exams:
            activities.append({
                "type": "exam",
                "message": f"Nouvel examen ajouté : {exam.title}",
                "date": str(exam.date),
            })

        recent_users = User.objects.order_by("-date_joined")[:5]
        for user in recent_users:
            user_type = "student" if user.role == "etudiant" else "teacher"
            activities.append({
                "type": user_type,
                "message": f"Nouvel utilisateur : {user.username}",
                "date": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
            })

        activities = sorted(activities, key=lambda x: x["date"], reverse=True)

        return Response(activities[:10])