from django.contrib.auth.models import User
from .models import Profile, SocialAchievement, StudentDocument
from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from .views import recalc_profile_xp

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver([post_save, post_delete], sender=SocialAchievement)
def update_user_xp_social(sender, instance, **kwargs):
    try:
        # 1. XP ni qayta hisoblash
        recalc_profile_xp(instance.user)
        
        from core.services.ranking import recalc_global_ranks, generate_annual_ranking
        
        # 2. Global reytingni yangilash
        recalc_global_ranks()
        
        # 3. Yillik reytingni yangilash (Avtomatik)
        year_id = instance.academic_year_id
        if not year_id:
            from .models import AcademicYear
            active_year = AcademicYear.objects.filter(is_active=True).first()
            if active_year:
                year_id = active_year.id
        
        if year_id:
            generate_annual_ranking(year_id)
            
    except Exception as e:
        print(f"Signal error: {e}")

@receiver([post_save, post_delete], sender=StudentDocument)
def update_user_xp_document(sender, instance, **kwargs):
    try:
        # 1. XP ni qayta hisoblash
        recalc_profile_xp(instance.user)
        
        from core.services.ranking import recalc_global_ranks, generate_annual_ranking
        
        # 2. Global reytingni yangilash
        recalc_global_ranks()
        
        # 3. Yillik reytingni yangilash (Avtomatik)
        year_id = instance.academic_year_id
        if not year_id:
            from .models import AcademicYear
            active_year = AcademicYear.objects.filter(is_active=True).first()
            if active_year:
                year_id = active_year.id
        
        if year_id:
            generate_annual_ranking(year_id)
            
    except Exception as e:
        print(f"Signal error: {e}")