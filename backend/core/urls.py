from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, MeView, ProfileViewSet, MessageViewSet,
    ResumeUploadView, FacultyViewSet, MajorViewSet,
    SocialAchievementViewSet, generate_ranking_view, download_application_zip, ScholarshipViewSet,
    ApplicationCreateView, AnnouncementListAPIView, AnnouncementViewUpdateAPIView,
    CheckEligibilityAPIView, ApplyScholarshipAPIView, UploadDocumentAPIView, 
    MyDocumentsAPIView, DeleteDocumentAPIView,
    AIChatViewSet, MentorshipChatViewSet, CVGenerateAPIView, TTSAPIView, AdminAIChatView,
    admin_ai_chat_view)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r'faculties', FacultyViewSet, basename="faculty")
router.register(r'majors', MajorViewSet, basename="major")
router.register(r'social-achievements', SocialAchievementViewSet, basename='socialachievement')
router.register("scholarships", ScholarshipViewSet)
router.register(r"ai-chat", AIChatViewSet, basename="ai-chat")
router.register(r"mentorship-chat", MentorshipChatViewSet, basename="mentorship-chat")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("resumes/upload/", ResumeUploadView.as_view(), name="resume-upload"),
    path("admin/generate-ranking/<int:year_id>/", generate_ranking_view),
    path("applications/", ApplicationCreateView.as_view()),
    path('announcements/', AnnouncementListAPIView.as_view()),
    path('announcements/<int:pk>/view/', AnnouncementViewUpdateAPIView.as_view()),
    path("scholarships/<int:scholarship_id>/check/", CheckEligibilityAPIView.as_view()),
    path("scholarships/<int:scholarship_id>/apply/", ApplyScholarshipAPIView.as_view()),
    path("documents/", MyDocumentsAPIView.as_view()),
    path("documents/upload/", UploadDocumentAPIView.as_view()),
    path("documents/<int:doc_id>/delete/", DeleteDocumentAPIView.as_view()),
    path("ai/generate-cv/", CVGenerateAPIView.as_view(), name="ai-generate-cv"),
    path("ai/tts/", TTSAPIView.as_view(), name="ai-tts"),
    path("admin-ai-chat/", AdminAIChatView.as_view(), name="admin-ai-chat"),
    path("admin/ai-assistant/", admin_ai_chat_view, name="admin-ai-assistant"),
    path("admin/download-application-zip/<int:application_id>/", download_application_zip, name="download-application-zip"),
]
