from openai import OpenAI
import os
from .ai_service import get_platform_context

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-proj-placeholder")
client = OpenAI(api_key=OPENAI_API_KEY)


def ask_mentor(user, user_message, history=None):
    """
    AI MENTOR funksiyasi.
    3 bosqichda ishlaydi:
    1. Diagnostika — foydalanuvchini bilish (3-5 savol)
    2. Maqsad — aniqlashtirish
    3. Roadmap — kunlik/haftalik/oylik reja
    """
    platform_context = get_platform_context(user)
    profile = getattr(user, 'profile', None)
    mentorship_data = {}

    if profile and hasattr(profile, 'mentorship_data'):
        mentorship_data = profile.mentorship_data or {}

    phase = mentorship_data.get("phase", "diagnostic")

    system_instruction = f"""
Siz platformaning "Shaxsiy AI Mentori"siz.
Vazifangiz: Foydalanuvchini akademik va shaxsiy maqsadlariga erishishda yo'llash.

ISH TARTIBI:
1. Diagnostika bosqichi (phase=diagnostic):
   - Foydalanuvchining hozirgi holati, bilimi, intizomini bilish uchun 3-5 ta savol ber.
   - Savollarni BITTADAN ber (hammasi birdan emas).
2. Maqsad bosqichi (phase=goal_set):
   - Foydalanuvchi orzusini (IELTS, Harvard, ish topish va h.k.) aniq qadamlarga bo'l.
3. Aktiv bosqich (phase=active):
   - Kunlik, Haftalik, Oylik reja tuz (Markdown jadval formatida).
   - Har haftada yangi vazifalar ber.

HOZIRGI HOLAT:
{platform_context}
Bosqich: {phase}

KO'RSATMALAR:
- Professional, dalda beruvchi, tahliliy ohangda gapir.
- Yo'l xaritasini Markdown jadval formatida taqdim et.
- IELTS/boshqa malakalar haqida aniq statistik talablarni kel.
- O'zbek tilida javob ber.
"""

    messages = [{"role": "system", "content": system_instruction}]

    # Oldingi suhbat tarixini qo'shish
    if history:
        for msg in history:
            role = "user" if msg.is_user else "assistant"
            messages.append({"role": role, "content": msg.text})

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content

        # Bosqichni avtomatik yangilash
        if profile and hasattr(profile, 'mentorship_data'):
            if not isinstance(profile.mentorship_data, dict):
                profile.mentorship_data = {}

            if "Roadmap" in reply or "Reja" in reply or "haftalik" in reply.lower():
                profile.mentorship_data["phase"] = "active"
                profile.save()
            elif phase == "diagnostic" and len(history or []) > 4:
                profile.mentorship_data["phase"] = "goal_set"
                profile.save()

        return reply
    except Exception as e:
        print(f"Mentor Service Error: {str(e)}")
        return "Mentor hozircha band, iltimos keyinroq urinib ko'ring."
