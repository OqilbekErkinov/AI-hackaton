from openai import OpenAI
import os
from core.models import SocialAchievement
from core.services.rag_service import RAGService

# ⚠️ MUHIM: OPENAI_API_KEY ni .env faylida saqlang
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-proj-placeholder")
client = OpenAI(api_key=OPENAI_API_KEY)


def get_platform_context(user):
    """
    Foydalanuvchi haqida kontekst ma'lumotlarini yig'adi.
    """
    context = "Platform ma'lumotlari:\n"

    profile = getattr(user, 'profile', None)
    if profile:
        interests = profile.interests if (hasattr(profile, 'interests') and isinstance(profile.interests, list)) else []
        about = getattr(profile, 'about', '') or ''

        context += f"\nFoydalanuvchi qiziqishlari: {', '.join(interests) if interests else 'Kiritilmagan'}\n"
        context += f"Foydalanuvchi haqida: {about or 'Ma`lumot yo`q'}\n"

    return context


def ask_gpt(user, user_message, mode="mentor", history=None):
    """
    AI ASSISTANT funksiyasi.
    Ikkita rejimni qo'llab-quvvatlaydi:
    1. 'mentor': Shaxsiy akademik maslahatchi.
    2. 'law': Rasmiy oliy ta'lim nizomlari bo'yicha RAG maslahatchisi.
    """
    if mode == "law":
        # RAG qidiruv tizimi orqali mos nizomlarni olamiz
        rag_context = RAGService.search(user_message, limit=5)
        
        system_instruction = f"""
Siz O'zbekiston Respublikasi Oliy ta'lim vazirligi va oliygohlarning rasmiy Huquqiy va Nizomlar bo'yicha maslahatchisisiz. Ismingiz "Adliya & Nizomlar AI".

QUYIDAGI RASMIY NIZOMLAR VA ME'YORIY HUJJATLARGA TAYANING:
{rag_context}

JAVOB BERISH TARTIBI:
1. Agar savolga qoidalarda ANIQ javob bo'lsa — qoidaga havola qilib, to'liq, aniq javob bering.
2. Agar savolga qoidalarda TO'LIQ javob bo'lmasa — qoidalardagi ENG YAQin ma'lumotni keltiring va: "Ushbu ma'lumot bizning nizomlar bazamizda to'liq ko'rsatilmagan, lekin..." deb davom eting.
3. Quyidagi mavzularda DOIMO yordam bering: Stipendiyalar, O'qishni ko'chirish/transfer, GPA baholash, Akademik tartib-intizom, Kiyinish madaniyati (dress-code).
4. Agar savol boshqa mavzuda bo'lsa, nizomlardan aloqador bo'limni toping va tavsiyanomalar bering.
5. Javobni DOIMO O'zbek tilida bering (foydalanuvchi boshqa tilda yozsa ham, javob o'zbekcha bo'lsin).
6. Markdown formatini ishlating (ro'yxat, **qalin matn**).
7. Hech qachon "ma'lumot yo'q" deb to'xtatib qo'ymang — har doim foydali va qo'shimcha yo'nalish bering.

FOYDALANUVCHI MA'LUMOTI: Savolni rus, o'zbek, qozoq yoki boshqa tilda berishi mumkin. Javob doimo o'zbekcha bo'lsin.
"""
    else:
        context = get_platform_context(user)
        system_instruction = f"""
Siz platformaning aqlli yordamchisisiz. Ismingiz "AI Yordamchi".
Vazifangiz: Foydalanuvchilarga motivatsiya berish, savollarga javob berish,
mos imkoniyatlarni tavsiya qilish.
Do'stona, samimiy va dalda beruvchi ohangda gapiring.

{context}

Foydalanuvchi qiziqishlariga mos takliflarni alohida ta'kidlang.
Javoblarni O'zbek tilida bering.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3 if mode == "law" else 0.7, # Law rejimida aniqlik uchun past harorat
            max_tokens=1000
        )
        if response and response.choices:
            return response.choices[0].message.content
        return "Uzr, hozircha javob bera olmayman."
    except Exception as e:
        print(f"AI Service Error: {str(e)}")
        return "Tizimda xatolik yuz berdi."


def generate_cv_content(user):
    """
    CV GENERATOR funksiyasi.
    Foydalanuvchi profiliga asosan HTML formatida CV yaratadi.
    """
    profile = getattr(user, 'profile', None)
    if not profile:
        return "<p>Profil topilmadi. Avval profilingizni to'ldiring.</p>"

    # Yutuqlar (XP ballar va ijtimoiy yutuqlar)
    achievements = SocialAchievement.objects.filter(user=user, status='approved')
    achievements_text = ""
    if achievements.exists():
        achievements_text = "\n".join([
            f"- {a.get_category_display()}: {a.description} ({a.score} ball)"
            for a in achievements
        ])

    # Avatar URL
    avatar_url = ""
    if hasattr(profile, 'avatar') and profile.avatar:
        avatar_url = f"http://127.0.0.1:9000{profile.avatar.url}"

    user_info = {
        "full_name": getattr(profile, 'full_name', '') or user.username,
        "email": user.email,
        "phone": getattr(profile, 'phone', '') or "Kiritilmagan",
        "university": getattr(profile, 'university_full', '') or "Kiritilmagan",
        "faculty": profile.faculty.name if hasattr(profile, 'faculty') and profile.faculty else "Kiritilmagan",
        "major": profile.major.name if hasattr(profile, 'major') and profile.major else "Kiritilmagan",
        "course": getattr(profile, 'course', '') or "Kiritilmagan",
        "gpa": getattr(profile, 'gpa', '') or "Kiritilmagan",
        "about": getattr(profile, 'about', '') or "Kiritilmagan",
        "interests": getattr(profile, 'interests', []) if isinstance(getattr(profile, 'interests', []), list) else [],
        "avatar_url": avatar_url,
    }

    prompt = f"""
Siz jahon darajasidagi professional rezyume dizayneri va HR mutaxassisisiz. 
Vazifangiz: Foydalanuvchi ma'lumotlari asosida eng zamonaviy, professional va "ATS-friendly" ikki ustunli (two-column) HTML rezyume tayyorlash.

FOYDALANUVCHI MA'LUMOTLARI:
- Ism-sharif: {user_info['full_name']}
- Email: {user_info['email']}
- Telefon: {user_info['phone']}
- Universitet: {user_info['university']}
- Fakultet: {user_info['faculty']}
- Yo'nalish: {user_info['major']}
- Kurs: {user_info['course']} (GPA: {user_info['gpa']})
- Men haqimda: {user_info['about']}
- Qiziqishlar: {', '.join(user_info['interests'])}

YUTUQLAR VA MUVAFFAQIYATLAR:
{achievements_text or 'Hozircha rasmiy tasdiqlangan yutuqlar yo`q.'}

STRUKTURA VA STIL (MAJBURIY):
Sizga berilgan CSS klasslardan foydalaning:
1. <div class="cv-layout"> : Barcha kontentni o'rab turuvchi asosiy konteyner.
2. <div class="cv-sidebar"> : Chap ustun (To'q rangli bo'ladi). 
   Ichida bo'lishi kerak:
   - <div class="cv-photo-container"><img src="{user_info['avatar_url']}" crossorigin="anonymous"/></div>
   - <div class="cv-sidebar-section"><h3>Contact</h3>...</div>
   - <div class="cv-sidebar-section"><h3>Skills</h3>... (Interests asosida ko'nikmalar tuzing)</div>
   - <div class="cv-sidebar-section"><h3>Languages</h3>... (O'zbek, Rus, Ingliz deb faraz qiling)</div>
3. <div class="cv-main"> : O'ng ustun (Oq rangli bo'ladi).
   Ichida bo'lishi kerak:
   - <h1>{user_info['full_name']}</h1>
   - <div class="cv-title">{user_info['major']} Student | {user_info['university']}</div>
   - <div class="cv-content-section"><h2>Professional Summary</h2>... (about ma'lumoti asosida kengaytirib yozing)</div>
   - <div class="cv-content-section"><h2>Education</h2>... (Fakultet va yo'nalishni chiroyli yozing)</div>
   - <div class="cv-content-section"><h2>Achievements</h2>... (Yutuqlarni professional tilda bayon qiling)</div>

MUHIM QOIDALAR:
- Faqat va faqat HTML kodini qaytaring (Markdown ``` bloklarisiz).
- Matnlarni mazmunli, professional va imloviy xatolarsiz to'ldiring.
- O'zbek tilida yozing, ammo professional terminlar (Masalan: "Professional Summary") inglizcha sarlavhalarda bo'lsin.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Siz rezyume mutaxassisisiz. Faqat HTML qaytaring."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        if response and response.choices:
            return response.choices[0].message.content
        return "<p>CV yaratishda xatolik yuz berdi.</p>"
    except Exception as e:
        print(f"CV Generation Error: {str(e)}")
        return f"<p>Xatolik: {str(e)}</p>"
