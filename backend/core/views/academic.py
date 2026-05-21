from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.contrib import messages

from core.models import Faculty, Major, SocialAchievement, AcademicYear, Profile
from core.serializers import FacultySerializer, MajorSerializer, SocialAchievementSerializer
from core.services.ranking import generate_annual_ranking

def recalc_profile_xp(user):
    """
    Recalculates a student's total XP (document rating) based on their approved StudentDocuments in each category.
    """
    from core.models import StudentDocument, DOCUMENT_MAX_POINTS
    
    total_xp = 0.0
    
    for doc_type_code, max_allowed in DOCUMENT_MAX_POINTS.items():
        latest_doc = (
            StudentDocument.objects
            .filter(user=user, doc_type=doc_type_code, status='approved')
            .order_by('-created_at', '-id')
            .first()
        )
        
        if latest_doc:
            score = latest_doc.score or 0.0
            total_xp += min(float(score), float(max_allowed))
        
    Profile.objects.filter(user=user).update(xp=total_xp)

@staff_member_required
def generate_ranking_view(request, year_id):
    """
    Staff-only endpoint to trigger annual ranking calculation for all majors.
    """
    generate_annual_ranking(year_id)
    messages.success(request, "Reyting muvaffaqiyatli yaratildi!")
    return HttpResponseRedirect("/admin/core/annualranking/")


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for University Faculties.
    """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.AllowAny]


class MajorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for Faculty Majors. Supports filtering by faculty_id.
    """
    serializer_class = MajorSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Major.objects.all()
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)
        return qs


class SocialAchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for students to submit and track their social activities/extracurricular works.
    Includes validation constraints (max 2 per category).
    """
    serializer_class = SocialAchievementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        # 1. Staff and Superusers can view all submissions
        if user.is_authenticated and user.is_staff:
            return SocialAchievement.objects.all()

        # 2. Authenticated users see approved ones from others, plus all of their own
        if user.is_authenticated:
            return SocialAchievement.objects.filter(
                Q(status='approved') | Q(user=user)
            )

        # 3. Anonymous guests only see approved ones
        return SocialAchievement.objects.filter(status='approved')

    def perform_create(self, serializer):
        user = self.request.user
        category = self.request.data.get('category')
        
        # Limit check: A student can upload a maximum of 2 documents per category (excluding rejected)
        if category:
            existing_count = SocialAchievement.objects.filter(
                user=user, 
                category=category
            ).exclude(status='rejected').count()
            
            if existing_count >= 2:
                raise ValidationError("Ushbu kategoriya uchun maksimal 2 ta hujjat yuklash imkoniyati tugagan.")

        active_year = AcademicYear.objects.filter(is_active=True).first()
        if not active_year:
            raise ValidationError("Ayni damda faol o'quv yili mavjud emas.")

        serializer.save(
            user=user,
            academic_year=active_year
        )

    def perform_destroy(self, instance):
        user = self.request.user
        
        # 1. Staff can delete any record
        if user.is_staff:
            instance.delete()
            return

        # 2. Students can delete their own records only if they aren't approved yet
        if instance.user == user:
            if instance.status == 'approved':
                raise PermissionDenied("Tasdiqlangan hujjatni o'chira olmaysiz. Iltimos, adminga murojaat qiling.")
            instance.delete()
        else:
            raise PermissionDenied("Sizda ushbu amalni bajarish uchun ruxsat yo'q.")
