from django.urls import path

from .views import (
    send_notification,
    my_notifications,
    mark_as_read           # ← AJOUTER CET IMPORT
)

urlpatterns = [
    path('send/', send_notification),
    path('my/', my_notifications),
    path('<int:notification_id>/read/', mark_as_read, name='mark-as-read'),
]