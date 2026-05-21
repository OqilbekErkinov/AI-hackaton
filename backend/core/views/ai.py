from rest_framework import viewsets, views, status, permissions, authentication
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from core.models import AIChatMessage, MentorshipMessage
from core.serializers import AIChatMessageSerializer, MentorshipMessageSerializer
from core.services.ai_service import ask_gpt, generate_cv_content
from core.services.mentorship_service import ask_mentor
from core.services.admin_ai_service import ask_admin_ai

class AIChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for students to chat with the general Academic AI Assistant.
    Generates intelligent responses and logs chat history.
    """
    serializer_class = AIChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIChatMessage.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user_text = request.data.get("text")
        if not user_text:
            return Response({"error": "text maydoni talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Save user query
        AIChatMessage.objects.create(user=request.user, is_user=True, text=user_text)

        # 2. Query core AI service adapter
        ai_response_text = ask_gpt(request.user, user_text)

        # 3. Save AI response and return
        ai_msg = AIChatMessage.objects.create(user=request.user, is_user=False, text=ai_response_text)
        return Response(self.get_serializer(ai_msg).data, status=status.HTTP_201_CREATED)


class MentorshipChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for students interacting with their specialized AI Career Mentor.
    Includes past conversation context for high quality personalized advice.
    """
    serializer_class = MentorshipMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MentorshipMessage.objects.filter(user=self.request.user).order_by('created_at')

    def create(self, request, *args, **kwargs):
        user_text = request.data.get("text")
        if not user_text:
            return Response({"error": "text maydoni talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Save student message
        MentorshipMessage.objects.create(user=request.user, is_user=True, text=user_text)

        # 2. Retrieve last 10 messages for context
        history = list(reversed(
            list(MentorshipMessage.objects.filter(user=request.user).order_by('-created_at')[:10])
        ))

        # 3. Query mentor service adapter
        mentor_response_text = ask_mentor(request.user, user_text, history=history)

        # 4. Save and return response
        mentor_msg = MentorshipMessage.objects.create(user=request.user, is_user=False, text=mentor_response_text)
        return Response(self.get_serializer(mentor_msg).data, status=status.HTTP_201_CREATED)


class CVGenerateAPIView(views.APIView):
    """
    Dynamically generates clean, structured LaTeX/Markdown CV content using LLM.
    Leverages student's academic history, achievements, and GPA details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = generate_cv_content(request.user)
        return Response({"content": content}, status=status.HTTP_200_OK)


@staff_member_required
def admin_ai_chat_view(request):
    """
    Django Admin panel integrated template view for the Admin AI copilot.
    """
    return render(request, 'admin/admin_ai_assistant.html', {
        'title': 'AI Smart Assistant',
    })


class AdminAIChatView(views.APIView):
    """
    API endpoint for admin-exclusive AI Chat queries about overall university statistics,
    ranking lists, and academic dashboard insights.
    """
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        user_text = request.data.get("text")
        if not user_text:
            return Response({"error": "text maydoni talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        ai_response = ask_admin_ai(request.user, user_text)
        return Response({"message": ai_response, "status": "success"}, status=status.HTTP_200_OK)
