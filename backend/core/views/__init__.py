from .auth import RegisterView, LoginView, MeView
from .profile import (
    ProfileViewSet, ResumeUploadView, UploadDocumentAPIView,
    MyDocumentsAPIView, DeleteDocumentAPIView
)
from .academic import (
    FacultyViewSet, MajorViewSet, SocialAchievementViewSet,
    generate_ranking_view, recalc_profile_xp
)
from .scholarship import (
    ScholarshipViewSet, ApplicationCreateView, CheckEligibilityAPIView,
    ApplyScholarshipAPIView, download_application_zip
)
from .ai import (
    AIChatViewSet, MentorshipChatViewSet, CVGenerateAPIView, TTSAPIView,
    QuizGenerateAPIView, QuizSubmitAPIView,
    AdminAIChatView, admin_ai_chat_view
)
from .communication import (
    MessageViewSet, AnnouncementListAPIView, AnnouncementViewUpdateAPIView,
    landing_view
)
