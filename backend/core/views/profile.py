from rest_framework import views, viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
import uuid

from core.models import Profile, Resume, StudentDocument
from core.serializers import ProfileSerializer, ResumeSerializer, StudentDocumentSerializer

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and updating user profiles.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Profile.objects.select_related("user").all()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            try:
                uid = int(user_id)
                qs = qs.filter(user__id=uid)
            except (ValueError, TypeError):
                try:
                    uid = uuid.UUID(user_id)
                    qs = qs.filter(user__id=str(uid))
                except Exception:
                    qs = qs.filter(user__id=user_id)
        return qs

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = ProfileSerializer(
            request.user.profile, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["put", "patch"],
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser, JSONParser],
    )
    def update_me(self, request):
        """
        Updates the authenticated user's profile information.
        """
        profile = request.user.profile
        data = request.data.copy()

        # remove_avatar flag
        remove_avatar = data.pop("remove_avatar", None)

        # Course empty string handling
        if "course" in data and data.get("course") in ("", None):
            data["course"] = None

        serializer = ProfileSerializer(
            profile,
            data=data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile = serializer.save()

        # Handle avatar deletion
        flag = False
        if isinstance(remove_avatar, str):
            flag = remove_avatar.lower() in ["1", "true", "yes", "on"]
        elif isinstance(remove_avatar, bool):
            flag = remove_avatar

        if flag:
            if getattr(profile, "avatar", None):
                profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save(update_fields=["avatar"])

        out = ProfileSerializer(profile, context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)


class ResumeUploadView(views.APIView):
    """
    Handles PDF/document CV upload for students.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response(
                {"detail": "Fayl kiritilishi shart"}, status=status.HTTP_400_BAD_REQUEST
            )
        resume = Resume.objects.create(user=request.user, file=f, filename=f.name)
        ser = ResumeSerializer(resume, context={"request": request})
        return Response(ser.data, status=status.HTTP_201_CREATED)


class UploadDocumentAPIView(views.APIView):
    """
    Endpoint for uploading student portfolio documents (certificates, transcript, publications).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StudentDocumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyDocumentsAPIView(views.APIView):
    """
    Lists all documents uploaded by the authenticated student.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        docs = StudentDocument.objects.filter(user=request.user)
        serializer = StudentDocumentSerializer(
            docs,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class DeleteDocumentAPIView(views.APIView):
    """
    Deletes a specific student document by ID.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, doc_id):
        try:
            doc = StudentDocument.objects.get(id=doc_id, user=request.user)
            doc.delete()
            return Response({"status": "deleted"}, status=status.HTTP_200_OK)
        except StudentDocument.DoesNotExist:
            return Response({"error": "Hujjat topilmadi"}, status=status.HTTP_404_NOT_FOUND)
