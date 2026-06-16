from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, MeView, ForgotPasswordView, ResetPasswordView,
    UserViewSet, DepartmentViewSet, GroupeViewSet , StudentsByGroupView,AdminStatsView,RecentActivitiesView
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('departments', DepartmentViewSet)
router.register('groupes', GroupeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('students-by-group/', StudentsByGroupView.as_view(), name='students-by-group'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/recent-activities/',RecentActivitiesView.as_view(),
),
]