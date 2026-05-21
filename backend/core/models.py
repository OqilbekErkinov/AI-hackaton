from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, verbose_name="Nomi")
    is_active = models.BooleanField(default=False, verbose_name="Faolmi?")

    class Meta:
        verbose_name = "Reyting shakllantirish"
        verbose_name_plural = "Reyting shakllantirish"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            AcademicYear.objects.update(is_active=False)
        super().save(*args, **kwargs)

class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nomi")

    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetlar"

    def __str__(self):
        return self.name

class Major(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="majors", verbose_name="Fakultet")
    name = models.CharField(max_length=255, verbose_name="Nomi")

    class Meta:
        unique_together = ('faculty', 'name')
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"

    def __str__(self):
        return f"{self.name}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Foydalanuvchi"
    )
    full_name = models.CharField(max_length=255, blank=True, verbose_name="F.I.SH.")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Avatar")
    about = models.TextField(blank=True, null=True, verbose_name="Haqida")
    role = models.CharField(max_length=50, default="user", verbose_name="Rol")

    # AI integration fields
    interests = models.JSONField(default=list, blank=True, verbose_name="Qiziqishlar")
    is_mentorship_active = models.BooleanField(default=False, verbose_name="Mentorlik faolmi?")
    mentorship_data = models.JSONField(default=dict, blank=True, verbose_name="Mentorlik ma'lumotlari")

    # umumiy XP
    xp = models.IntegerField(default=0, verbose_name="XP Ball")
    global_rank = models.IntegerField(null=True, blank=True, verbose_name="Global reyting")

    gpa = models.FloatField(null=True, blank=True, verbose_name="GPA")
    has_debt = models.BooleanField(default=False, verbose_name="Akademik qarzdorlik bor")
    has_discipline_penalty = models.BooleanField(default=False, verbose_name="Intizomiy jazo bor")

    # universitet
    university_short = models.CharField(max_length=255, blank=True, verbose_name="OTM (qisqa)")
    university_full = models.CharField(max_length=255, blank=True, verbose_name="OTM (to'liq)")

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
        verbose_name="Fakultet"
    )
    major = models.ForeignKey(
        Major,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
        verbose_name="Yo'nalish"
    )

    # bosqich (kurs)
    course = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Bosqich (1–6)",
        verbose_name="Bosqich"
    )

    # guruh
    group = models.CharField(
        max_length=50,
        blank=True,
        help_text="Masalan: 23-05",
        verbose_name="Guruh"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Talaba"
        verbose_name_plural = "Talabalar"

    def __str__(self):
        return self.full_name or self.user.email






class Message(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Kimdan"
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="Kimga"
    )
    text = models.TextField(verbose_name="Xabar matni")
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True, verbose_name="Ilova")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Yuborilgan vaqti")
    read = models.BooleanField(default=False, verbose_name="O'qildimi?")

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"

    def __str__(self):
        return f"msg {self.id} from {self.from_user.email} to {self.to_user.email}"


# === AI ASSISTANT chat tarixi ===
class AIChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_chats", verbose_name="Foydalanuvchi")
    is_user = models.BooleanField(default=True, verbose_name="Foydalanuvchimi?")
    text = models.TextField(verbose_name="Xabar matni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqti")

    class Meta:
        ordering = ['created_at']
        verbose_name = "AI Chat xabari"
        verbose_name_plural = "AI Chat xabarlari"

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.text[:30]}"

# === AI MENTOR chat tarixi ===
class MentorshipMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentorship_chats", verbose_name="Foydalanuvchi")
    is_user = models.BooleanField(default=True, verbose_name="Foydalanuvchimi?")
    text = models.TextField(verbose_name="Xabar matni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqti")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Mentorlik xabari"
        verbose_name_plural = "Mentorlik xabarlari"

    def __str__(self):
        return f"{'User' if self.is_user else 'Mentor'}: {self.text[:30]}"


class Resume(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resumes",
        verbose_name="Foydalanuvchi"
    )
    file = models.FileField(upload_to="resumes/", verbose_name="Fayl")
    filename = models.CharField(max_length=512, blank=True, verbose_name="Fayl nomi")
    status = models.CharField(max_length=32, default="ready", verbose_name="Holat")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Rezume"
        verbose_name_plural = "Rezumelar"

    def __str__(self):
        return self.filename or self.file.name


import sys
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError

def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("Maksimal fayl hajmi 5MB bo'lishi kerak.")

def compress_image(image):
    try:
        im = Image.open(image)
        if im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        
        # O'ta katta rasmlarni kichraytiramiz
        max_size = (1600, 1600)
        im.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = BytesIO()
        im.save(output, format='JPEG', quality=70, optimize=True)
        output.seek(0)
        
        return InMemoryUploadedFile(
            output, 
            'ImageField', 
            f"{image.name.split('.')[0]}.jpg", 
            'image/jpeg', 
            sys.getsizeof(output), 
            None
        )
    except:
        return image


# IJTIMOIY FAOLLIK


class SocialAchievement(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
    )

    CATEGORY_CHOICES = (
        (1, 'Kitobxonlik madaniyati'),
        (2, '5 muhim tashabbus'),
        (3, 'Akademik o\'zlashtirish (GPA)'),
        (4, 'Odob-axloq va dress-kod'),
        (5, 'Ko\'rik-tanlov va olimpiadalar'),
        (6, 'Darslardagi davomat'),
        (7, 'Ma\'rifat darslari'),
        (8, 'Volontyorlik va jamoat ishlari'),
        (9, 'Madaniy tashriflar'),
        (10, 'Sport va sog\'lom turmush'),
        (11, 'Boshqa ma\'naviy faollik'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_achievements', verbose_name="Foydalanuvchi")
    category = models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES, verbose_name="Toifa")
    sub_category = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kichik toifa")
    rank = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="O'rin")

    date = models.DateField(verbose_name="Sana")
    description = models.TextField(verbose_name="Tavsif")
    proof_file = models.FileField(
        upload_to='social_proofs/', 
        verbose_name="Isbot (Fayl)",
        validators=[validate_file_size]
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holat")
    score = models.FloatField(default=0, verbose_name="Ball")
    admin_note = models.TextField(blank=True, null=True, verbose_name="Admin izohi")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="Akademik yil"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Ijtimoiy faollik"
        verbose_name_plural = "Ijtimoiy faolliklar"

    def __str__(self):
        return f"{self.user.username} - {self.get_category_display()}"

    def clean(self):
        from .logic import MAX_POINTS_MAP
        from django.core.exceptions import ValidationError
        super().clean()
        if self.status == 'approved':
            max_allowed = float(MAX_POINTS_MAP.get(int(self.category), 5))
            if float(self.score) > max_allowed:
                raise ValidationError(f"Xatolik: ushbu toifa uchun maksimal ball {max_allowed}. Siz {self.score} ball kiritdingiz.")

    def save(self, *args, **kwargs):
        # Rasmni siqish
        if self.proof_file and not self.id: # Faqat yangi yuklanganda
            ext = self.proof_file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                self.proof_file = compress_image(self.proof_file)
        
        super().save(*args, **kwargs)


class AnnualRanking(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name="Akademik yil"
    )
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        verbose_name="Yo'nalish"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Talaba"
    )

    total_score = models.FloatField(verbose_name="Umumiy ball")
    rank = models.IntegerField(verbose_name="Rank")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        unique_together = ("academic_year", "major", "student")
        ordering = ["rank"]
        verbose_name = "Yillik reyting"
        verbose_name_plural = "Yillik reytinglar"

    def __str__(self):
        return f"{self.student} - {self.rank}"




class Scholarship(models.Model):

    CATEGORY_CHOICES = (
        ("state", "Davlat"),
        ("private", "Xususiy"),
        ("international", "Xalqaro"),
    )

    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    short_description = models.TextField(verbose_name="Qisqa tavsif")
    description = models.TextField(verbose_name="To'liq tavsif")

    amount = models.CharField(max_length=100, verbose_name="Miqdori")

    organization = models.CharField(max_length=255, verbose_name="Tashkilot")

    deadline = models.DateField(verbose_name="Oxirgi muddat")

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Toifa"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Stipendiya"
        verbose_name_plural = "Stipendiyalar"

    def __str__(self):
        return self.title


class ScholarshipRequirement(models.Model):

    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name="requirements",
        verbose_name="Stipendiya"
    )

    text = models.CharField(max_length=255, verbose_name="Talab matni")

    class Meta:
        verbose_name = "Stipendiya talabi"
        verbose_name_plural = "Stipendiya talablari"

    def __str__(self):
        return self.text

class ScholarshipApplication(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Talaba"
    )

    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Stipendiya"
    )

    motivation_letter = models.TextField(verbose_name="Motivatsiya xati")

    attached_documents = models.ManyToManyField(
        "StudentDocument",
        blank=True,
        related_name="applications_attached",
        verbose_name="Ilova qilingan hujjatlar"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    status = models.CharField(
        max_length=20,
        choices=(
            ("pending","Kutilmoqda"),
            ("approved","Tasdiqlandi"),
            ("rejected","Rad etildi")
        ),
        default="pending",
        verbose_name="Holat"
    )

    admin_note = models.TextField(blank=True, null=True, verbose_name="Admin izohi")

    class Meta:
        verbose_name = "Stipendiya arizasi"
        verbose_name_plural = "Stipendiya arizalari"

    def __str__(self):
        return f"{self.user.username} - {self.scholarship.title}"


class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    topic = models.CharField(max_length=100, verbose_name="Mavzu")

    short = models.TextField(verbose_name="Qisqa tavsif")
    description = models.TextField(verbose_name="To'liq tavsif")

    image = models.ImageField(upload_to='announcements/', null=True, blank=True, verbose_name="Rasm")

    deadline = models.DateField(null=True, blank=True, verbose_name="Oxirgi muddat")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    views = models.IntegerField(default=0, verbose_name="Ko'rishlar soni")

    type = models.CharField(max_length=50, verbose_name="Turi")
    is_important = models.BooleanField(default=False, verbose_name="Muhimmi?")

    locations = models.JSONField(default=list, blank=True, verbose_name="Joylashuvlar")
    requirements = models.JSONField(default=list, blank=True, verbose_name="Talablar")
    benefits = models.JSONField(default=list, blank=True, verbose_name="Imtiyozlar")

    link = models.URLField(null=True, blank=True, verbose_name="Havola")

    class Meta:
        verbose_name = "E'lon"
        verbose_name_plural = "E'lonlar"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if isinstance(self.locations, str):
            self.locations = [i.strip() for i in self.locations.split(",")]

        if isinstance(self.requirements, str):
            self.requirements = [i.strip() for i in self.requirements.split(",")]

        if isinstance(self.benefits, str):
            self.benefits = [i.strip() for i in self.benefits.split(",")]

        super().save(*args, **kwargs)


DOCUMENT_MAX_POINTS = {
    "transcript": 30.0,
    "language_cert": 20.0,
    "article": 10.0,
    "thesis": 10.0,
    "publication": 10.0,
    "ict_cert": 10.0,
    "conference": 5.0,
    "history_cert": 5.0,
    "recommendation": 0.0,
    "passport": 0.0,
}

class StudentDocument(models.Model):
    DOCUMENT_TYPES = [
        ("transcript", "Transcript / Baholar"),
        ("article", "Ilmiy maqola"),
        ("thesis", "Tezis"),
        ("publication", "Boshqa nashr ishlari (kitob, qo'llanma)"),
        ("language_cert", "Til sertifikati (IELTS, CEFR, etc)"),
        ("ict_cert", "IT sertifikati / Diplomi"),
        ("history_cert", "O'zbekiston tarixi (Dabtal fanlar)"),
        ("conference", "Konferensiya ishtiroki / Diplomi"),
        ("recommendation", "Tavsiyanoma"),
        ("passport", "Passport / ID karta"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents", verbose_name="Talaba")
    doc_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, verbose_name="Hujjat turi")
    file = models.FileField(
        upload_to="documents/", 
        verbose_name="Fayl",
        validators=[validate_file_size]
    )

    meta = models.JSONField(blank=True, null=True, verbose_name="Meta ma'lumotlar")
    score = models.FloatField(default=0.0, verbose_name="Ball")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        verbose_name="Akademik yil"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Kutilmoqda'),
            ('approved', 'Tasdiqlandi'),
            ('rejected', 'Rad etildi')
        ],
        default='pending',
        verbose_name="Holat"
    )

    admin_note = models.TextField(blank=True, null=True, verbose_name="Admin izohi")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Talaba hujjati"
        verbose_name_plural = "Talaba hujjatlari"

    def __str__(self):
        return f"{self.user.username} - {self.get_doc_type_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        max_p = DOCUMENT_MAX_POINTS.get(self.doc_type, 0.0)
        if self.score > max_p:
            raise ValidationError(
                f"Xatolik: {self.get_doc_type_display()} uchun maksimal ball {max_p}. Siz {self.score} ball kiritdingiz."
            )

    def save(self, *args, **kwargs):
        # Rasmni siqish
        if self.file and not self.id:
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                self.file = compress_image(self.file)
        
        if not self.academic_year:
            active_year = AcademicYear.objects.filter(is_active=True).first()
            if active_year:
                self.academic_year = active_year

        super().save(*args, **kwargs)


class ScholarshipRule(models.Model):
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name="rules",
        verbose_name="Stipendiya"
    )

    RULE_TYPES = [
        ("min_gpa", "Minimum GPA"),
        ("min_articles", "Minimum Articles"),
        ("min_thesis", "Minimum Thesis"),
        ("min_publications", "Minimum Publications (Others)"),
        ("min_conferences", "Minimum Conference Participations"),
        ("require_language", "Language (Uzbek + Foreign)"),
        ("require_ict", "ICT Certificate Required"),
        ("require_history", "History Result Required"),
        ("no_debt", "No Academic Debt"),
        ("no_penalty", "No Discipline Penalty"),
        ("course", "Allowed Course"),
    ]

    rule_type = models.CharField(max_length=50, choices=RULE_TYPES, verbose_name="Qoida turi")
    value = models.JSONField(verbose_name="Qiymat")

    class Meta:
        verbose_name = "Stipendiya qoidasi"
        verbose_name_plural = "Stipendiya qoidalari"

    def __str__(self):
        return f"{self.rule_type} - {self.value}"