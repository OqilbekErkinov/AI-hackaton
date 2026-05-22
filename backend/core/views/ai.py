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
        is_voice_input = bool(audio_file)  # Ovozli kirish bo'lsa True

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

        # 4. Ovozli sintez:
        # - Agar OVOZLI kirish bo'lsa: har doim TTS (ovozli javob)
        # - Agar MATN kirish bo'lsa: faqat voice_synthesize=true bo'lganda TTS
        audio_url = None
        should_synthesize = is_voice_input or voice_synthesize
        if should_synthesize:
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
        serializer_data["is_voice_input"] = is_voice_input  # Frontend uchun flag
        
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


class TTSAPIView(views.APIView):
    """
    On-demand Text-to-Speech endpoint.
    Foydalanuvchi matn javobini audio sifatida eshitmoqchi bo'lganda chaqiriladi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get("text", "").strip()
        if not text:
            return Response({"error": "text maydoni talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)
        if len(text) > 4096:
            text = text[:4096]
        
        audio_url = VoiceService.synthesize_speech(text)
        if audio_url:
            return Response({"audio_url": audio_url}, status=status.HTTP_200_OK)
        return Response({"error": "Audio yaratishda xatolik yuz berdi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === SMART EDU VIKTORINASI (BOSQICH 4) ===
import json
from django.db.models import F
from core.models import QuizAttempt, Profile
from core.services.ai_service import generate_quiz

class QuizGenerateAPIView(views.APIView):
    """
    GPT orqali berilgan mavzu bo'yicha dinamik test (JSON) yaratadi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        topic = request.query_params.get("topic", "Dasturlash asoslari")
        raw_json = generate_quiz(topic)
        
        # Markdown bloklarini tozalash
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:]
        if raw_json.endswith("```"):
            raw_json = raw_json[:-3]
            
        try:
            quiz_data = json.loads(raw_json)
            return Response(quiz_data, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({"error": "AI test yaratishda xatolik yuz berdi.", "raw": raw_json}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizSubmitAPIView(views.APIView):
    """
    Talaba testni yechib bo'lgach, natijani saqlaydi va XP (ball) beradi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        topic = request.data.get("topic")
        score = request.data.get("score")
        total_questions = request.data.get("total_questions")

        if not all([topic, score is not None, total_questions]):
            return Response({"error": "Barcha maydonlar (topic, score, total_questions) talab qilinadi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            score = int(score)
            total_questions = int(total_questions)
        except ValueError:
            return Response({"error": "score va total_questions butun son bo'lishi kerak."}, status=status.HTTP_400_BAD_REQUEST)

        # 1 ta to'g'ri javob = 5 XP
        xp_earned = score * 5

        # Natijani saqlash
        attempt = QuizAttempt.objects.create(
            user=request.user,
            topic=topic,
            score=score,
            total_questions=total_questions,
            xp_earned=xp_earned
        )

        # Foydalanuvchi profiliga umumiy XP ni qo'shish
        Profile.objects.filter(user=request.user).update(xp=F('xp') + xp_earned)

        return Response({
            "message": "Natija saqlandi!",
            "xp_earned": xp_earned,
            "total_score": score
        }, status=status.HTTP_201_CREATED)


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
