from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import Notification
from .serializers import NotificationSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):

    receiver_role = request.data.get("receiver_role", "admin")
    sujet = request.data.get("sujet", "")
    message = request.data.get("message", "")
    type_notification = request.data.get("type", "message")

    if not sujet or not message:
        return Response({
            "error": "Le sujet et le message sont obligatoires"
        }, status=400)

    try:
        receivers = User.objects.filter(role=receiver_role)
        
        if not receivers.exists():
            return Response({
                "error": f"Aucun utilisateur trouvé avec le rôle '{receiver_role}'"
            }, status=404)

        created_notifications = []
        for receiver in receivers:
            notif = Notification.objects.create(
                sender=request.user,
                receiver=receiver,
                sujet=sujet,
                message=message,
                type=type_notification
            )
            created_notifications.append(notif)

        return Response({
            "success": True,
            "message": f"Notification envoyée à {len(created_notifications)} destinataire(s)",
            "count": len(created_notifications)
        })

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_notifications(request):

    notifications = Notification.objects.filter(
        receiver=request.user
    ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(
            id=notification_id,
            receiver=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({"success": True})
    except Notification.DoesNotExist:
        return Response({"error": "Notification non trouvée"}, status=404)