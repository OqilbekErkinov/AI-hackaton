from rest_framework import viewsets, views, status, permissions, authentication
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from core.models import AIChatMessage, MentorshipMessage
from core.serializers import AIChatMessageSerializer, MentorshipMessageSerializer
from core.services.ai_service import ask_gpt, generate_cv_content
from core.services.mentorship_service import ask_mentor
from core.services.admin_ai_service import ask_admin_ai
from core.services.voice_service import VoiceService

class AIChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for students to chat with the general Academic AI Assistant.
    Supports text/voice inputs, law/mentor modes, and TTS generation.
    """
    serializer_class = AIChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Rejim bo'yicha tarixni filtrlash (alohida va toza saqlash uchun)
        mode = self.request.query_params.get("mode", "mentor")
        return AIChatMessage.objects.filter(user=self.request.user, mode=mode)

    def create(self, request, *args, **kwargs):
        mode = request.data.get("mode", "mentor")
        voice_synthesize = request.data.get("voice_synthesize") == "true" or request.data.get("voice_synthesize") is True
        
        user_text = request.data.get("text")
        audio_file = request.FILES.get("audio")

        # 1. Ovozli xabar yuborilgan bo'lsa STT qilish
        if audio_file:
            try:
                user_text = VoiceService.transcribe_audio(audio_file)
            except Exception as e:
                return Response({"error": f"Ovozni matnga o'girishda xatolik: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_text:
            return Response({"error": "text yoki audio fayl maydoni talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Foydalanuvchi so'rovini saqlash
        user_msg = AIChatMessage.objects.create(
            user=request.user, 
            is_user=True, 
            text=user_text,
            mode=mode
        )

        # 3. GPT-4o-mini'ga so'rov yuborish
        ai_response_text = ask_gpt(request.user, user_text, mode=mode)

        # 4. Agar ovozli sintez talab qilingan bo'lsa TTS qilish
        audio_url = None
        if voice_synthesize:
            audio_url = VoiceService.synthesize_speech(ai_response_text)

        # 5. AI javobini saqlash
        ai_msg = AIChatMessage.objects.create(
            user=request.user, 
            is_user=False, 
            text=ai_response_text,
            mode=mode,
            audio_url=audio_url
        )
        
        # Ovozli yuklashda user transkripsiyasini ham qo'shimcha qaytaramiz
        serializer_data = self.get_serializer(ai_msg).data
        serializer_data["user_transcription"] = user_text
        
        return Response(serializer_data, status=status.HTTP_201_CREATED)


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
    grant eligibility lists, and academic dashboard insights.
    """
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        user_text = request.data.get("text")
        if not user_text:
            return Response({"error": "text maydoni talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        ai_response = ask_admin_ai(request.user, user_text)
        return Response({"message": ai_response, "status": "success"}, status=status.HTTP_200_OK)
