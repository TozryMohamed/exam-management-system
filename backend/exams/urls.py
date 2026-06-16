from django.urls import path
from .views import (
    ExamListCreateView,
    ExamDetailView,
    SalleListCreateView,
    teachers_list
)

urlpatterns = [
    path("exams/", ExamListCreateView.as_view()),
    path("exams/<int:pk>/", ExamDetailView.as_view()),
    path("salles/", SalleListCreateView.as_view()),

    # 👨‍🏫 NEW
    path("teachers/", teachers_list),
]