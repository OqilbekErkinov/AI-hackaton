from openai import OpenAI
import os
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from core.models import Profile, SocialAchievement, AnnualRanking, ScholarshipApplication, StudentDocument, AcademicYear


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-proj-placeholder")
client = OpenAI(api_key=OPENAI_API_KEY)


def get_admin_context():
    """
    Barcha foydalanuvchilar va tizim statistikasi ma'lumotlarini jamlaydi.
    """
    active_year = AcademicYear.objects.filter(is_active=True).first()
    user_count = User.objects.count()
    
    # 1. Hujjatlar statistikasi
    ach_stats = SocialAchievement.objects.values('status').annotate(count=Count('id'))
    doc_stats = StudentDocument.objects.values('status').annotate(count=Count('id'))
    
    # 2. Eng yaxshi talabalar (Top 10 XP)
    top_students = Profile.objects.all().order_by('-xp')[:10]
    
    # 3. Grant nomzodlari (agar joriy yil bo'lsa)
    grant_candidates = []
    if active_year:
        grant_candidates = AnnualRanking.objects.filter(academic_year=active_year).order_by('rank')[:15]

    summary = f"--- NEXORA PLATFORMA ANALITIKASI ---\n"
    summary += f"Joriy faol yil: {active_year.name if active_year else 'Noma`lum'}\n"
    summary += f"Jami foydalanuvchilar: {user_count}\n\n"
    
    summary += "HUJJATLAR HOLATI:\n"
    for s in ach_stats:
        summary += f"- {s['status'].capitalize()}: {s['count']} ta faollik\n"
    
    summary += "\nTOP 10 TALABA (GLOBAL XP):\n"
    for p in top_students:
        summary += f"- {p.full_name} | XP: {p.xp} | Guruh: {p.group or 'Noma`lum'}\n"

    if grant_candidates:
        summary += "\nGRANT NOMZODLARI (TOP 15):\n"
        for r in grant_candidates:
            summary += f"- [Rank: {r.rank}] {r.student.profile.full_name} | Ball: {r.total_score} | Yo'nalish: {r.major.name}\n"

    summary += "\nOXIRGI YUKLANGAN 5 TA HUJJAT:\n"
    recent_docs = SocialAchievement.objects.all().order_by('-created_at')[:5]
    for d in recent_docs:
        summary += f"- {d.user.profile.full_name}: {d.get_category_display()} ({d.status})\n"

    return summary


def ask_admin_ai(admin_user, admin_message):
    """
    ADMIN AI funksiyasi.
    """
    context = get_admin_context()

    system_instruction = f"""
Siz Nexora platformasining "Bosh AI Tahlilchisi" (Chief Data Analyst)siz.
Administratorga tizimdagi tendensiyalar, muammolar va yutuqlar haqida chuqur tahlil berishingiz kerak.

SIZGA TAQDIM ETILAYOTGAN JORIY MA'LUMOTLAR:
{context}

VAZIFALARINGIZ:
1. Ma'lumotlardagi g'alati holatlarni (anomaliyalar) aniqlang (masalan, kutilayotgan hujjatlar juda ko'payib ketgan bo'lsa).
2. Eng faol yo'nalishlar va guruhlarni tahlil qiling.
3. Grantga munosib nomzodlar haqida tavsiyalar bering.
4. Foydalanuvchi savoliga qarab, yuqoridagi kontekstdan foydalanib ANIQ raqamlar bilan javob bering.
5. Agar admin savoli kontekstda bo'lmasa, umumiy tizim boshqaruvi bo'yicha maslahat bering.

Muloqot tili: O'zbek tili. Ohang: Professional, tahliliy va yordamga tayyor.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": admin_message}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        return response.choices[0].message.content if response.choices else "Xatolik yuz berdi."
    except Exception as e:
        return f"Tizim xatosi: {str(e)}"
