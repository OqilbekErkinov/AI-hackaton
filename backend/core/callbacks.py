from .models import SocialAchievement, ScholarshipApplication, StudentDocument

def get_pending_social_count(request):
    count = SocialAchievement.objects.filter(status='pending').count()
    return str(count) if count > 0 else None

def get_pending_application_count(request):
    count = ScholarshipApplication.objects.filter(status='pending').count()
    return str(count) if count > 0 else None

def get_pending_document_count(request):
    count = StudentDocument.objects.filter(status='pending').count()
    return str(count) if count > 0 else None

def is_superuser(request):
    return request.user.is_superuser

def is_not_tutor(request):
    if request.user.is_superuser:
        return True
    profile = getattr(request.user, 'profile', None)
    if profile and str(profile.role).lower() == 'tutor':
        return False
    return True
