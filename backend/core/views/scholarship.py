from rest_framework import viewsets, generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone
import zipfile
import io

from core.models import Scholarship, ScholarshipApplication, StudentDocument
from core.serializers import ScholarshipSerializer, ApplicationSerializer
from core.services.validation_engine import validate_application

@staff_member_required
def download_application_zip(request, application_id):
    """
    Admin-only utility to download all documents submitted by a student
    for a specific scholarship application as a ZIP archive.
    """
    application = get_object_or_404(ScholarshipApplication, id=application_id)
    docs = application.attached_documents.all()
    
    if not docs:
        return HttpResponse("Fayllar mavjud emas", status=404)
        
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for doc in docs:
            if doc.file:
                name_prefix = doc.get_doc_type_display().replace("/", "_")
                filename = f"{name_prefix}_{doc.id}_{doc.file.name.split('/')[-1]}"
                try:
                    with doc.file.open('rb') as f:
                        zip_file.writestr(filename, f.read())
                except Exception as e:
                    print(f"Error adding file {filename} to zip: {e}")
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = f'attachment; filename="application_{application_id}_files.zip"'
    return response


class ScholarshipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset listing available scholarships.
    """
    queryset = Scholarship.objects.all().order_by("-created_at")
    serializer_class = ScholarshipSerializer


class ApplicationCreateView(generics.CreateAPIView):
    """
    API endpoint for students to draft and submit a scholarship application.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CheckEligibilityAPIView(views.APIView):
    """
    Validates if a student meets all eligibility criteria for a specific scholarship.
    Returns boolean eligibility, list of validation errors, and draft status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, scholarship_id):
        user = request.user
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)

        # 1. Check if user already applied
        applied = ScholarshipApplication.objects.filter(user=user, scholarship=scholarship).first()
        
        # 2. Run rule-based validation engine
        errors = validate_application(user, scholarship)

        return Response({
            "eligible": len(errors) == 0,
            "errors": errors,
            "already_applied": applied is not None,
            "application_status": applied.status if applied else None,
            "application_id": applied.id if applied else None,
            "admin_note": applied.admin_note if applied else None
        }, status=status.HTTP_200_OK)


class ApplyScholarshipAPIView(views.APIView):
    """
    Validates eligibility, processes motivation letters,
    attaches uploaded student portfolio docs, and submits the application.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, scholarship_id):
        user = request.user
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)

        # 1. Double submission check
        if ScholarshipApplication.objects.filter(user=user, scholarship=scholarship).exists():
            return Response({"error": "Siz ushbu stipendiyaga allaqachon ariza topshirgansiz."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Deadline expiration check
        if scholarship.deadline and scholarship.deadline < timezone.now().date():
             return Response({"error": "Arizalar qabul qilish muddati tugagan."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Rule-based strict validation
        errors = validate_application(user, scholarship)
        if errors:
            return Response({
                "status": "rejected",
                "errors": errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4. Motivation letter check
        motivation = request.data.get("motivation_letter", "").strip()
        if not motivation:
             return Response({"error": "Motivatsiya xati bo'sh bo'lishi mumkin emas."}, status=status.HTTP_400_BAD_REQUEST)

        # 5. Create application instance
        application = ScholarshipApplication.objects.create(
            user=user,
            scholarship=scholarship,
            motivation_letter=motivation
        )

        # 6. Link attached documents
        doc_ids = request.data.get("attached_documents", [])
        if isinstance(doc_ids, list) and doc_ids:
            application.attached_documents.set(doc_ids)

        return Response({
            "status": "accepted",
            "application_id": application.id
        }, status=status.HTTP_201_CREATED)
