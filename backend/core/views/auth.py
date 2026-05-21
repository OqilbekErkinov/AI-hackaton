from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework_simplejwt.tokens import RefreshToken
import base64
import uuid

from core.models import Profile
from core.serializers import UserSerializer, ProfileSerializer

def tokens_for_user(user):
    """
    Generate access and refresh tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

class RegisterView(views.APIView):
    """
    Handles student registration. Returns the created user, profile,
    and authentication JWT tokens.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, *args, **kwargs):
        data = request.data
        email = (data.get("email") or "").strip().lower()
        password = data.get("password")
        fullname = data.get("fullname") or ""
        phone = data.get("phone") or ""
        avatar_file = request.FILES.get("avatar")
        avatar_dataurl = (
            data.get("avatarDataUrl") or data.get("avatar_data_url") or None
        )

        if not email or not password:
            return Response(
                {"detail": "Elektron pochta va parol talab qilinadi"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"email": ["Bu email allaqachon roʻyxatdan o'tgan."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {"password": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST
            )

        username = email.split("@")[0]
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        p, created = Profile.objects.get_or_create(
            user=user, defaults={"full_name": fullname, "phone": phone}
        )
        p.full_name = fullname or p.full_name
        p.phone = phone or p.phone

        if avatar_file and hasattr(avatar_file, "name"):
            p.avatar = avatar_file
        else:
            if avatar_dataurl:
                try:
                    header, base64data = (
                        avatar_dataurl.split(",", 1)
                        if "," in avatar_dataurl
                        else ("", avatar_dataurl)
                    )
                    if header and "/" in header:
                        fmt = header.split(";")[0].split("/")[1]
                    else:
                        fmt = "png"
                    filename = f"avatar_{uuid.uuid4().hex}.{fmt}"
                    data_file = ContentFile(
                        base64.b64decode(base64data), name=filename
                    )
                    p.avatar.save(filename, data_file, save=False)
                except Exception:
                    pass
        p.save()

        tokens = tokens_for_user(user)
        user_ser = UserSerializer(user)
        profile_ser = ProfileSerializer(p, context={"request": request})
        return Response(
            {
                "user": user_ser.data,
                "profile": profile_ser.data,
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )

class LoginView(views.APIView):
    """
    Handles user login using email and password, returning active tokens and user profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Elektron pochta va parol talab qilinadi"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Berilgan hisob maʼlumotlari bilan faol hisob topilmadi"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Berilgan hisob maʼlumotlari bilan faol hisob topilmadi"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Foydalanuvchi faol emas"}, status=status.HTTP_403_FORBIDDEN
            )

        tokens = tokens_for_user(user)
        user_ser = UserSerializer(user)
        profile_ser = ProfileSerializer(user.profile, context={"request": request})
        return Response(
            {
                "user": user_ser.data,
                "profile": profile_ser.data,
                **tokens,
            }
        )

class MeView(views.APIView):
    """
    Returns the currently authenticated user details and their profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        ser = UserSerializer(user)
        prof = ProfileSerializer(user.profile, context={"request": request})
        return Response({"user": ser.data, "profile": prof.data})
