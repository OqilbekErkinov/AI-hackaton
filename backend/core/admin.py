from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from nexora_backend.admin_site import admin_site
from .models import (
    ScholarshipApplication, AcademicYear, Faculty, Major, Profile, 
    Message, Resume, SocialAchievement, AnnualRanking, GrantQuota, 
    Scholarship, ScholarshipRequirement, Announcement, ScholarshipRule, 
    StudentDocument
)
from core.logic import calculate_score, MAX_POINTS_MAP, SUB_CATEGORY_MAP
from core.services.ranking import generate_annual_ranking
import openpyxl
from django.http import HttpResponse
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Avg
from django import forms
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


class ProfileInline(TabularInline):
    model = Profile
    can_delete = False
    fields = ("role", "group", "full_name", "phone")
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if profile.role == 'tutor':
                    return ("group",)
            except:
                pass
        return ()


# 0. User va Group modellari (Unfold dizaynida)
admin_site.unregister(User) if admin_site.is_registered(User) else None
admin_site.unregister(Group) if admin_site.is_registered(Group) else None

@admin.register(User, site=admin_site)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    inlines = (ProfileInline,)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.profile
            if profile.role == 'tutor' and profile.group:
                # Tutors can only see users from their group
                return qs.filter(profile__group=profile.group)
        except:
            pass
        return qs

@admin.register(Group, site=admin_site)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# 1. Fakultetlarni admin panelga qo'shish
@admin.register(Faculty, site=admin_site)
class FacultyAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

# 2. Yo'nalishlarni admin panelga qo'shish
@admin.register(Major, site=admin_site)
class MajorAdmin(ModelAdmin):
    list_display = ("id", "faculty", "name")
    list_filter = ("faculty",)
    search_fields = ("name", "faculty__name")

@admin.register(Profile, site=admin_site)
class ProfileAdmin(ModelAdmin):
    list_display = (
        "full_name",
        "user_email",
        "role",
        "university_short",
        "faculty",
        "major",
        "xp",
        "global_rank",
        "created_at",
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.profile
            if profile.role == 'tutor' and profile.group:
                return qs.filter(group=profile.group)
        except:
            pass
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if profile.role == 'tutor':
                    return list(readonly) + ["group", "role"]
            except:
                pass
        return readonly

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if profile.role == 'tutor' and profile.group:
                    obj.group = profile.group
                    obj.role = 'student' # Tyutorlar faqat talaba yarata oladi
            except:
                pass
        super().save_model(request, obj, form, change)

    readonly_fields = ("created_at", "xp", "global_rank")

    fieldsets = (
        (
            "Asosiy ma'lumotlar",
            {"fields": ("user", "full_name", "phone", "role", "avatar", "about")},
        ),
        (
            "Ta'lim ma'lumotlari",
            {
                "fields": (
                    "university_short",
                    "university_full",
                    "faculty",
                    "major",
                    "course",
                    "group",
                    "gpa",
                    "has_debt",
                    "has_discipline_penalty",
                )
            },
        ),
        (
            "Reyting / XP", 
            {
                "fields": (
                    "xp", 
                    "global_rank", 
                    "interests", 
                    "is_mentorship_active", 
                    "mentorship_data"
                )
            }
        ),
        ("Tizim", {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.profile
            if profile.role == 'tutor' and profile.group:
                return qs.filter(group=profile.group)
        except:
            pass
        return qs

# Message va Resume o'zgarishsiz qoladi



@admin.register(StudentDocument, site=admin_site)
class StudentDocumentAdmin(ModelAdmin):
    list_display = ("student_name", "doc_type_name", "status", "score", "academic_year", "created_at", "view_file")
    list_filter = ("doc_type", "status", "academic_year", "created_at")
    search_fields = ("user__username", "user__email", "user__profile__full_name", "meta__note")
    readonly_fields = ("student_profile_link", "doc_type", "created_at", "display_meta", "display_file", "score")
    
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("student_profile_link", "doc_type", "created_at"),
        }),
        ("Hujjat mazmuni", {
            "fields": ("display_meta", "display_file"),
        }),
        ("Qaror qabul qilish", {
            "fields": ("status", "score", "academic_year", "admin_note"),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

    actions = ['approve_docs', 'reject_docs']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.profile
            if profile.role == 'tutor' and profile.group:
                return qs.filter(user__profile__group=profile.group)
        except:
            pass
        return qs

    def student_name(self, obj):
        return obj.user.profile.full_name or obj.user.username
    student_name.short_description = "Talaba"

    def student_profile_link(self, obj):
        if obj.user:
            from django.urls import reverse
            try:
                profile_id = obj.user.profile.id
                url = reverse('admin:core_profile_change', args=[profile_id])
                name = obj.user.profile.full_name or obj.user.username
                return format_html('<a href="{}" style="font-weight: bold; color: #2563eb;">{} (Profilni ko\'rish)</a>', url, name)
            except:
                return obj.user.username
        return "-"
    student_profile_link.short_description = "Talaba (Profilga havola)"

    def doc_type_name(self, obj):
        return obj.get_doc_type_display()
    doc_type_name.short_description = "Hujjat turi"

    def approve_docs(self, request, queryset):
        for obj in queryset:
            obj.status = 'approved'
            obj.save()
        self.message_user(request, "Hujjatlar tasdiqlandi va ballar avtomatik hisoblandi.")
    approve_docs.short_description = "✅ Tasdiqlash"

    def reject_docs(self, request, queryset):
        for obj in queryset:
            obj.status = 'rejected'
            obj.save()
        self.message_user(request, "Hujjatlar rad etildi.")
    reject_docs.short_description = "❌ Rad etish"

    def view_file(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Ko\'rish</a>', obj.file.url)
        return "-"
    view_file.short_description = "Fayl"

    def display_meta(self, obj):
        if not obj.meta or not isinstance(obj.meta, dict):
            return "Ma'lumotlar mavjud emas"
        
        from django.utils.safestring import mark_safe
        from django.utils.html import escape

        html = '<div style="background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; max-width: 600px;">'
        
        has_data = False
        note = obj.meta.get('note')
        score = obj.meta.get('score')
        
        if score:
            has_data = True
            html += '<div style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">'
            html += '<span style="color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;">GPA / Ball:</span><br>'
            html += f'<span style="color: #2563eb; font-size: 16px; font-weight: 700;">{escape(score)}</span>'
            html += '</div>'
            
        if note:
            has_data = True
            html += '<div>'
            html += '<span style="color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;">Izoh / Ma\'lumot:</span><br>'
            html += f'<div style="color: #1e293b; font-size: 14px; line-height: 1.5; margin-top: 4px; white-space: pre-wrap;">{escape(note)}</div>'
            html += '</div>'
        
        if not has_data:
            return "Qo'shimcha ma'lumot yo'q"
            
        html += '</div>'
        return mark_safe(html)
    
    display_meta.short_description = "Hujjat tafsilotlari"

    def display_file(self, obj):
        if not obj.file:
            return "Fayl yuklanmagan"
        
        url = obj.file.url
        ext = url.lower().split('.')[-1]
        
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return format_html(
                '<div style="margin-top: 10px;">'
                '<img src="{}" style="max-height: 500px; max-width: 100%; border-radius: 8px; border: 1px solid #cbd5e1;" />'
                '<br><a href="{}" target="_blank" style="display: inline-block; margin-top: 10px; color: #2563eb; font-weight: bold;">[ To\'liq o\'lchamda ochish ]</a>'
                '</div>',
                url, url
            )
        
        return format_html(
            '<a href="{}" target="_blank" style="background-color: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block;">'
            '📄 Hujjatni ko\'rish (PDF/Fayl)'
            '</a>',
            url
        )
    
    display_file.short_description = "Yuklangan hujjat"

@admin.register(Message, site=admin_site)
class MessageAdmin(ModelAdmin):
    list_display = ("id", "from_user", "to_user", "created_at", "read")
    search_fields = ("from_user__email", "to_user__email", "text")
    list_filter = ("read",)

@admin.register(Resume, site=admin_site)
class ResumeAdmin(ModelAdmin):
    list_display = ("id", "user", "filename", "created_at")
    readonly_fields = ("created_at",)


# IJTIMOIY FAOLLIK



class SocialAchievementForm(forms.ModelForm):
    class Meta:
        model = SocialAchievement
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        score = cleaned_data.get('score')

        if category and score is not None:
            max_allowed = MAX_POINTS_MAP.get(category, 5)
            if score > max_allowed:
                raise forms.ValidationError(
                    f"Xatolik: ushbu toifa uchun maksimal ball {max_allowed}. Siz {score} ball kiritdingiz."
                )
        return cleaned_data

@admin.register(SocialAchievement, site=admin_site)
class SocialAchievementAdmin(ModelAdmin):
    form = SocialAchievementForm
    # Ro'yxat ko'rinishi
    list_display = ('user', 'category_name', 'sub_category_name', 'status', 'display_score', 'created_at')
    list_filter = ('status', 'category')

    # Talaba ma'lumotlarini admin o'zgartira olmasligi uchun readonly qilamiz
    def get_readonly_fields(self, request, obj=None):
        base_readonly = [
            'user', 'category', 'sub_category', 'sub_category_name', 'rank', 'date',
            'description', 'display_proof_file', 'estimated_score'
        ]
        # Faqat 1, 4, 8, 9 va 11-toifalar uchun 'score' editable bo'ladi
        if obj and obj.category in [1, 4, 8, 9, 11]:
            return base_readonly
        # Boshqa toifalar uchun 'score' readonly (avtomatik hisoblanadi)
        return base_readonly + ['score']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.profile
            if profile.role == 'tutor' and profile.group:
                return qs.filter(user__profile__group=profile.group)
        except:
            pass
        return qs

    # Admin faqat 'status', 'score' va 'admin_note' ni boshqara oladi
    fields = (
        'user', 'category', 'sub_category_name', 'rank', 'date',
        'description', 'display_proof_file', 'estimated_score',
        'score', 'status', 'admin_note'
    )

    def category_name(self, obj):
        return obj.get_category_display()

    category_name.short_description = "Yo'nalish"

    def sub_category_name(self, obj):
        return SUB_CATEGORY_MAP.get(str(obj.sub_category), obj.sub_category or "Belgilanmagan")

    sub_category_name.short_description = "Kichik toifa"

    def display_score(self, obj):
        return f"{obj.score} ball"

    display_score.short_description = "Berilgan ball"

    def display_proof_file(self, obj):
        if obj.proof_file:
            if obj.proof_file.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return format_html('<img src="{}" style="max-height: 300px; border-radius: 10px;" />',
                                   obj.proof_file.url)
            return format_html('<a href="{}" target="_blank">Hujjatni ko\'rish (PDF/Fayl)</a>', obj.proof_file.url)
        return "Fayl yuklanmagan"

    display_proof_file.short_description = "Isbot (Rasm/Hujjat)"

    def estimated_score(self, obj):
        score = calculate_score(obj)
        return format_html('<b style="color: #112d4e; font-size: 16px;">{} ball</b> (Nizom bo\'yicha)', score)

    estimated_score.short_description = "Tasdiqlansa beriladigan ball"

    # Tasdiqlash tugmasi (Action)
    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        for obj in queryset:
            # Har doim ballni qayta hisoblaymiz/tekshiramiz (capping uchun)
            obj.score = calculate_score(obj)
            obj.status = 'approved'
            obj.save()
        self.message_user(request, "Tanlangan yutuqlar tasdiqlandi va ballar me'yorga keltirildi.")

    approve_selected.short_description = "✅ Tanlanganlarni tasdiqlash"

    def reject_selected(self, request, queryset):
        for obj in queryset:
            obj.status = 'rejected'
            obj.score = 0
            obj.save()
        self.message_user(request, "Tanlangan yutuqlar rad etildi.")

    reject_selected.short_description = "❌ Tanlanganlarni rad etish"

    # Formani saqlashda ballni avtomat yozish/capping qilish
    def save_model(self, request, obj, form, change):
        if not obj.academic_year:
            active_year = AcademicYear.objects.filter(is_active=True).first()
            if active_year:
                obj.academic_year = active_year

        if obj.status == 'approved':
            # Har doim calculate_score ni chaqiramiz, u o'zi cap qiladi (logic.py da)
            obj.score = calculate_score(obj)
        elif obj.status == 'rejected':
            obj.score = 0
            
        super().save_model(request, obj, form, change)



def export_ranking_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ranking"

    headers = [
        "Akademik Yil",
        "Yo'nalish",
        "Talaba",
        "Umumiy ball",
        "O'rin",
        "Grant g'olibi"
    ]

    ws.append(headers)

    for obj in queryset:
        ws.append([
            obj.academic_year.name,
            obj.major.name,
            obj.student.profile.full_name or obj.student.username,
            obj.total_score,
            obj.rank,
            "HA" if obj.is_grant_winner else "YO'Q"
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=ranking.xlsx"

    wb.save(response)
    return response

export_ranking_excel.short_description = "📥 Export selected to Excel"


def export_grant_winners_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grant_winners.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("Grant Winners List", styles['Heading1']))
    elements.append(Spacer(1, 20))

    winners = queryset.filter(is_grant_winner=True)

    for obj in winners:
        text = f"{obj.student.profile.full_name} - {obj.major.name} - Rank {obj.rank}"
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 10))

    doc.build(elements)

    return response


export_grant_winners_pdf.short_description = "📄 Export Grant Winners PDF"


@admin.register(AnnualRanking, site=admin_site)
class AnnualRankingAdmin(ModelAdmin):

    list_display = (
        "student_profile_link",
        "major",
        "academic_year",
        "total_score",
        "colored_rank",
        "grant_status"
    )

    list_filter = (
        "academic_year",
        "major",
        "is_grant_winner"
    )

    search_fields = (
        "student__username",
        "student__email",
        "student__profile__full_name",
    )

    ordering = ("major", "rank")

    actions = [export_ranking_excel, export_grant_winners_pdf]

    readonly_fields = (
        "academic_year",
        "major",
        "student_profile_link",
        "total_score",
        "rank",
        "is_grant_winner",
        "achievement_breakdown"
    )

    def student_profile_link(self, obj):
        from django.urls import reverse
        try:
            profile_id = obj.student.profile.id
            url = reverse('admin:core_profile_change', args=[profile_id])
            name = obj.student.profile.full_name or obj.student.username
            return format_html('<a href="{}" style="font-weight: bold; color: #2563eb;">{}</a>', url, name)
        except:
            return obj.student.username
    student_profile_link.short_description = "Talaba"

    def grant_status(self, obj):
        if obj.is_grant_winner:
            return mark_safe(
                '<span style="color:green;font-weight:bold;">🏆 GRANT</span>'
            )
        return mark_safe('<span style="color:gray;font-weight:bold;">Kontrakt</span>')
    grant_status.short_description = "Grant"

    def achievement_breakdown(self, obj):
        from core.logic import MAX_POINTS_MAP
        
        # Har bir kategoriya bo'yicha eng oxirgi tasdiqlangan hujjatlarni yig'amiz
        final_achievements = []
        for cat in range(1, 12):
            latest = SocialAchievement.objects.filter(
                user=obj.student,
                category=cat,
                status='approved',
                academic_year=obj.academic_year
            ).order_by('-created_at', '-id').first()
            
            if latest:
                final_achievements.append(latest)

        html = "<h3>Hisoblangan faolliklar (Eng oxirgi hujjatlar)</h3><ul>"

        for ach in final_achievements:
            max_p = MAX_POINTS_MAP.get(ach.category, 5)
            display_score = min(float(ach.score), float(max_p))
            html += f"<li><b>{ach.get_category_display()}</b> — {display_score} ball (Hujjat bali: {ach.score})</li>"

        html += "</ul>"
        html += "<p style='color:gray; font-size: 12px;'>* Nizomga ko'ra har bir yo'nalish bo'yicha faqat eng oxirgi yuklangan hujjat bali inobatga olingan.</p>"

        return mark_safe(html)

    achievement_breakdown.short_description = "Faolliklar haqida"

    def colored_rank(self, obj):
        if obj.rank == 1:
            return mark_safe('<span style="color:gold;font-size:18px;">🥇 1</span>')
        elif obj.rank == 2:
            return mark_safe('<span style="color:silver;font-size:18px;">🥈 2</span>')
        elif obj.rank == 3:
            return mark_safe('<span style="color:#cd7f32;font-size:18px;">🥉 3</span>')
        return obj.rank

    colored_rank.short_description = "Rank"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("statistics/", self.admin_site.admin_view(self.statistics_view), name="ranking-statistics"),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        from .models import AnnualRanking

        data = (
            AnnualRanking.objects
            .values("major__name")
            .annotate(avg_score=Avg("total_score"))
        )

        context = dict(
            self.admin_site.each_context(request),
            data=list(data),
        )

        return TemplateResponse(request, "admin_custom/ranking_statistics.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["statistics_url"] = "statistics/"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(GrantQuota, site=admin_site)
class GrantQuotaAdmin(ModelAdmin):
    list_display = ("major", "academic_year", "total_slots")
    list_filter = ("academic_year", "major")
    search_fields = ("major__name", "academic_year__name")


@admin.register(AcademicYear, site=admin_site)
class AcademicYearAdmin(ModelAdmin):
    list_display = ("name", "is_active")

    actions = ["generate_ranking"]

    def generate_ranking(self, request, queryset):
        for year in queryset:
            generate_annual_ranking(year.id)

        self.message_user(
            request,
            "Reyting muvaffaqiyatli yaratildi!",
            messages.SUCCESS
        )

    generate_ranking.short_description = "Tanlangan yil uchun reytingni yaratish"



class RequirementInline(TabularInline):
    model = ScholarshipRequirement
    extra = 1

class RuleInline(TabularInline):
    model = ScholarshipRule
    extra = 1

@admin.register(Scholarship, site=admin_site)
class ScholarshipAdmin(ModelAdmin):

    list_display = (
        "title",
        "organization",
        "amount",
        "deadline",
        "category",
        "created_at"
    )
    list_filter = ("category", "deadline", "created_at")
    search_fields = ("title", "organization", "description")

    inlines = [
        RequirementInline,
        RuleInline
    ]


@admin.register(ScholarshipApplication, site=admin_site)
class ApplicationAdmin(ModelAdmin):
    list_display = (
        "student_name",
        "scholarship",
        "status",
        "created_at",
    )
    list_filter = ("status", "scholarship", "created_at")
    search_fields = ("user__username", "user__email", "scholarship__title")
    readonly_fields = ("student_profile_link", "scholarship_display", "display_attachments", "created_at")
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.profile
            if profile.role == 'tutor' and profile.group:
                return qs.filter(user__profile__group=profile.group)
        except:
            pass
        return qs

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("student_profile_link", "scholarship_display", "created_at"),
        }),
        ("Ariza mazmuni", {
            "fields": ("motivation_letter", "display_attachments"),
        }),
        ("Qaror qabul qilish", {
            "fields": ("status", "admin_note"),
        }),
    )

    def student_name(self, obj):
        return obj.user.profile.full_name or obj.user.username
    student_name.short_description = "Talaba"

    def scholarship_display(self, obj):
        return obj.scholarship.title
    scholarship_display.short_description = "Tanlangan stipendiya"

    def student_profile_link(self, obj):
        if obj.user:
            from django.urls import reverse
            try:
                profile_id = obj.user.profile.id
                url = reverse('admin:core_profile_change', args=[profile_id])
                name = obj.user.profile.full_name or obj.user.username
                return format_html('<a href="{}" style="font-weight: bold; color: #2563eb;">{} (Profilni ko\'rish)</a>', url, name)
            except:
                return obj.user.username
        return "-"
    student_profile_link.short_description = "Talaba (Profilga havola)"

    def display_attachments(self, obj):
        docs = obj.attached_documents.all()
        if not docs:
            return "Hujjatlar biriktirilmagan"
        
        html = '<div style="background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; max-width: 600px;">'
        
        # Zip download button
        zip_url = f"/api/admin/download-application-zip/{obj.id}/"
        html += f'<a href="{zip_url}" style="background-color: #16a34a; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 15px;">'
        html += '📦 Barcha hujjatlarni yuklab olish (ZIP)'
        html += '</a><br>'

        for doc in docs:
            html += '<div style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between;">'
            html += f'<div><span style="font-weight: bold; color: #1e293b;">{doc.get_doc_type_display()}</span>'
            if doc.meta and doc.meta.get('score'):
                html += f' <span style="color: #2563eb; margin-left: 5px;">(Ball: {doc.meta["score"]})</span>'
            html += '</div>'
            html += f'<a href="{doc.file.url}" target="_blank" style="color: #2563eb; font-weight: bold; margin-left: 10px;">[ Ko\'rish ]</a>'
            html += '</div>'
            
        html += '</div>'
        return mark_safe(html)
    display_attachments.short_description = "Ilova qilingan hujjatlar"


class AnnouncementAdminForm(forms.ModelForm):
    # 🔥 SHU QISM ENG MUHIM
    locations = forms.CharField(required=False, widget=forms.Textarea, help_text="Vergul bilan ajrating: Samarqand — Cloud, Toshkent — AI")
    requirements = forms.CharField(required=False, widget=forms.Textarea, help_text="Vergul bilan ajrating: Yosh 18–30, Ingliz tili, Saralash asosida")
    benefits = forms.CharField(required=False, widget=forms.Textarea, help_text="Vergul bilan ajrating: Bepul ta’lim, Sertifikat, Ish imkoniyati")

    class Meta:
        model = Announcement
        fields = '__all__'

    # 🔥 CLEAN FUNKSIYALAR

    def clean_locations(self):
        data = self.cleaned_data.get("locations")
        if data:
            return [i.strip() for i in data.split(",")]
        return []

    def clean_requirements(self):
        data = self.cleaned_data.get("requirements")
        if data:
            return [i.strip() for i in data.split(",")]
        return []

    def clean_benefits(self):
        data = self.cleaned_data.get("benefits")
        if data:
            return [i.strip() for i in data.split(",")]
        return []

@admin.register(Announcement, site=admin_site)
class AnnouncementAdmin(ModelAdmin):
    form = AnnouncementAdminForm
    list_display = ('title', 'type', 'views', 'created_at')







