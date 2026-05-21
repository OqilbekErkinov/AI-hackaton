from rest_framework import viewsets, views, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import render

from core.models import Message, Announcement
from core.serializers import MessageSerializer, AnnouncementSerializer

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for real-time instant messages between students and mentors.
    Supports filtering by active dialogue thread and listing unread counts.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.filter(
            Q(to_user=user) | Q(from_user=user)
        )

        other_id = self.request.query_params.get("with")
        if other_id:
            qs = qs.filter(
                Q(to_user_id=other_id, from_user=user)
                | Q(from_user_id=other_id, to_user=user)
            )

        unread_only = self.request.query_params.get("unread")
        if str(unread_only) in ("1", "true", "True"):
            qs = qs.filter(to_user=user, read=False)

        return qs.order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=False, methods=["post"], url_path="mark-read")
    def mark_read(self, request):
        """
        Marks all incoming messages in a thread as read.
        """
        other_id = request.data.get("with")
        if not other_id:
            return Response(
                {"detail": '"with" field is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            other_id = int(other_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": '"with" must be integer user id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        qs = Message.objects.filter(
            to_user=user,
            from_user_id=other_id,
            read=False,
        )
        updated_count = qs.update(read=True)
        return Response({"updated": updated_count}, status=status.HTTP_200_OK)


class AnnouncementListAPIView(views.APIView):
    """
    API endpoint listing university announcements, sorted in reverse-chronological order.
    """
    def get(self, request):
        data = Announcement.objects.all().order_by('-created_at')
        serializer = AnnouncementSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnnouncementViewUpdateAPIView(views.APIView):
    """
    Increments the view counter for an announcement upon a user reading it.
    """
    def post(self, request, pk):
        try:
            ann = Announcement.objects.get(pk=pk)
            ann.views += 1
            ann.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Announcement.DoesNotExist:
            return Response({"error": "E'lon topilmadi"}, status=status.HTTP_404_NOT_FOUND)


def landing_view(request):
    """
    Renders the default landing web page.
    """
    return render(request, 'landing.html')
