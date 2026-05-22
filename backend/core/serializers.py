# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Profile, Message, Resume, Faculty, Major,
    SocialAchievement, Scholarship, ScholarshipRequirement,
    ScholarshipApplication, Announcement, StudentDocument,
    AIChatMessage, MentorshipMessage)
import json

from .computingxp import compute_xp


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'

class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    # Frontendda nomlarni ko'rish uchun (Read-only)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    major_name = serializers.CharField(source='major.name', read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ("user", "user_id", "avatar_url", "xp")

    def get_user_id(self, obj):
        return obj.user.id

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            url = obj.avatar.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def update(self, instance, validated_data):
        """
        ForeignKey (Faculty va Major) ID orqali keladi.
        Django buni avtomatik tushunishi uchun super().update ishlatamiz.
        """
        # Faqat kerakli maydonlarni instance ga o'zlashtiramiz
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, obj):
        data = super().to_representation(obj)
        # Agar ism bo'sh bo'lsa, username ni qaytaramiz
        if not data.get("full_name"):
            data["full_name"] = obj.user.get_full_name() or obj.user.username
        return data





class MessageSerializer(serializers.ModelSerializer):
    # o‘qishda nested user ma’lumot
    from_user = UserSerializer(read_only=True)
    to_user_detail = UserSerializer(source="to_user", read_only=True)

    # yozishda faqat id yuboramiz
    to_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Message
        fields = (
            "id",
            "from_user",
            "to_user",        # write-only (id)
            "to_user_detail", # read-only (full object)
            "text",
            "created_at",
            "read",
        )
        read_only_fields = ("id", "from_user", "created_at", "read")

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        else:
            data = dict(data)

        if "to_user" not in data:
            for key in ("to_id", "to", "receiver", "toUser"):
                if key in data and data.get(key):
                    data["to_user"] = data.get(key)
                    break

        if "text" not in data:
            for key in ("body", "message", "msg", "content"):
                if key in data and data.get(key):
                    data["text"] = data.get(key)
                    break

        return super().to_internal_value(data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["from_id"] = instance.from_user_id
        rep["to_id"] = instance.to_user_id
        return rep


class ResumeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ("id", "user", "filename", "file", "file_url", "created_at")

    def get_file_url(self, obj):
        request = (
            self.context.get("request") if isinstance(self.context, dict) else None
        )
        if hasattr(obj, "file") and obj.file:
            try:
                url = obj.file.url
                if request and isinstance(url, str) and url.startswith("/"):
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return getattr(obj, "file", None)
        return None


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)


# IJTIMOIY FAOLLIK
class SocialAchievementSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = SocialAchievement
        fields = '__all__'
        read_only_fields = ('user', 'score', 'academic_year', 'status', 'admin_note')



class RequirementSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScholarshipRequirement
        fields = ["id", "text"]


class ScholarshipSerializer(serializers.ModelSerializer):

    requirements = RequirementSerializer(many=True)

    class Meta:
        model = Scholarship
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScholarshipApplication
        fields = "__all__"
        read_only_fields = ["user"]

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class StudentDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)

    class Meta:
        model = StudentDocument
        fields = ["id", "doc_type", "doc_type_display", "file", "file_url", "meta", "status", "score", "academic_year", "admin_note", "created_at"]
        read_only_fields = ["status", "score", "academic_year", "admin_note", "created_at"]

    def to_internal_value(self, data):
        # MultiPartParser sends QueryDict, which is immutable and expects strings.
        # We convert it to a standard dict to handle the parsed JSON 'meta' object.
        if hasattr(data, 'dict'):
            data = data.dict()
        else:
            data = dict(data)
        
        meta_val = data.get('meta')
        if meta_val and isinstance(meta_val, str):
            try:
                data['meta'] = json.loads(meta_val)
            except (ValueError, TypeError):
                pass
        
        return super().to_internal_value(data)

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    attached_docs_detail = StudentDocumentSerializer(source="attached_documents", many=True, read_only=True)

    class Meta:
        model = ScholarshipApplication
        fields = ["id", "user", "scholarship", "motivation_letter", "attached_documents", "attached_docs_detail", "status", "created_at"]
        read_only_fields = ["user", "status", "created_at"]

class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ['id', 'is_user', 'text', 'mode', 'audio_url', 'created_at']
        read_only_fields = ['id', 'created_at']


class MentorshipMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipMessage
        fields = ['id', 'is_user', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']
