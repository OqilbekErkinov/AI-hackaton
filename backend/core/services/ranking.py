from django.db.models import Sum, Q
from django.contrib.auth.models import User
from core.models import AnnualRanking, GrantQuota, Profile, StudentDocument


def recalc_global_ranks():
    # Barcha profillarni XP bo'yicha tartiblab olamiz
    profiles = list(Profile.objects.all().order_by("-xp", "id"))
    
    for i, p in enumerate(profiles):
        p.global_rank = i + 1
    
    # Bitta so'rovda barcha o'zgarishlarni saqlaymiz
    Profile.objects.bulk_update(profiles, ["global_rank"], batch_size=500)


def generate_annual_ranking(year_id):
    from core.logic import DOCUMENT_MAX_POINTS
    # Eski rankinglarni o‘chiramiz
    AnnualRanking.objects.filter(academic_year_id=year_id).delete()

    quotas = GrantQuota.objects.filter(academic_year_id=year_id)
    
    new_rankings = []

    for quota in quotas:
        major = quota.major
        students_list = User.objects.filter(profile__major=major)
        
        ranked_students = []
        for student in students_list:
            total_capped_score = 0
            for doc_type_code, max_allowed in DOCUMENT_MAX_POINTS.items():
                latest_doc = (
                    StudentDocument.objects
                    .filter(user=student, doc_type=doc_type_code, status='approved')
                    .order_by('-created_at', '-id')
                    .first()
                )
                
                if latest_doc:
                    score = latest_doc.score or 0.0
                    total_capped_score += min(float(score), float(max_allowed))
            
            ranked_students.append({
                'student': student,
                'total_score': total_capped_score
            })

        # Ballar bo'yicha saralaymiz
        ranked_students.sort(key=lambda x: x['total_score'], reverse=True)

        position = 1
        for item in ranked_students:
            new_rankings.append(
                AnnualRanking(
                    academic_year_id=year_id,
                    major=major,
                    student=item['student'],
                    total_score=item['total_score'],
                    rank=position,
                    is_grant_winner=position <= quota.total_slots
                )
            )
            position += 1

    # Barcha yangi rankinglarni bitta so'rovda yaratamiz
    if new_rankings:
        AnnualRanking.objects.bulk_create(new_rankings, batch_size=500)

    return "Ranking generated"