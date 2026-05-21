# core/logic.py

MAX_POINTS_MAP = {
    1: 20, # Kitobxonlik
    2: 20, # 5 tashabbus
    3: 10, # GPA
    4: 5,  # Odob-axloq
    5: 10, # Tanlovlar
    6: 5,  # Davomat
    7: 10, # Ma'rifat
    8: 5,  # Volontyor
    9: 5,  # Tashriflar
    10: 5, # Sport
    11: 5, # Boshqa
}

SUB_CATEGORY_MAP = {
    "1": "Ma'naviy-ma'rifiy tadbirlar",
    "2": "Umumxalq bayramlari",
    "3": "Umumxalq hasharlari",
    "4": "Tashabbuskor volontyorlik",
    "5": "To'garakda ishtirok (10 ball)",
    "6": "To'garak tashkil etganlik (20 ball)",
    "7": "Xalqaro miqyosda",
    "8": "Respublika miqyosida",
    "9": "Viloyat/Hududiy miqyosda",
    "10": "OTM ichki bosqichida",
    "11": "OTM terma jamoasi a'zosi (5 ball)",
    "12": "Sport seksiya/to'garak (3 ball)",
    "13": "Sport musobaqasi ishtirokchisi (1 ball)",
    "14": "Hamkor tadbir tashkil etish (3 ball)",
    "15": "Xiyobonlarda tadbir (2 ball)",
    "16": "Tadbirda faol ishtirok (1 ball)",
    # Kitobxonlik
    "101": "10-12 ta badiiy adabiyot (Maks: 20 ball)",
    "102": "7-9 ta badiiy adabiyot (Maks: 15 ball)",
    "103": "4-6 ta badiiy adabiyot (Maks: 10 ball)",
    # 5 tashabbus
    "201": "OTMda tashkil etilgan to'garakdagi faol ishtirok (10 ball)",
    "202": "Madaniyat va san'at to'garaklarida ishtirok (10 ball)",
    "203": "Sport yo'nalishida seksiyalarda ishtirok (10 ball)",
    "204": "Axborot texnologiyalari yo'nalishida to'garaklarda ishtirok (10 ball)",
    "205": "Kitobxonlik va adabiyot to'garaklarida ishtirok (10 ball)",
    "206": "Bandlik yo'nalishida to'garaklarda ishtirok (10 ball)",
    "207": "To'garak tashkil etish va samarali faoliyat (20 ball)",
    # Madaniy tashriflar
    "901": "Har oyda kamida bir marotaba (5 ball)",
    "902": "Har ikki oyda kamida bir marotaba (3 ball)",
    "903": "Semestrda kamida bir marotaba (1 ball)",
}

def calculate_score(achievement):
    cat = achievement.category
    
    # 1. Admin qo'lda ball qo'ygan bo'lsa (va uni saqlab qolish kerak bo'lsa),
    # lekin u maksimal balldan oshib ketmasligi kerak.
    max_allowed = float(MAX_POINTS_MAP.get(int(cat), 5))
    
    # Kitobxonlik (1), Odob-axloq (4), Volontyorlik (8), Tashriflar (9), Boshqa (11) uchun manual entry
    if cat in [1, 4, 8, 9, 11] and achievement.score > 0:
        return float(min(float(achievement.score), max_allowed))

    sub = achievement.sub_category or ""
    rank = achievement.rank

    # Helper to check ID or Name
    def is_match(target_ids, target_names):
        if str(sub) in target_ids:
            return True
        for name in target_names:
            if name.lower() in str(sub).lower():
                return True
        return False

    score = 0

    # 1. Kitobxonlik (Maksimal 20 ball)
    if cat == 1:
        if is_match(["101"], ["10-12"]):
            score = 20
        elif is_match(["102"], ["7-9"]):
            score = 15
        elif is_match(["103"], ["4-6"]):
            score = 10
        else:
            score = 10

    # 2. 5 muhim tashabbus (Maksimal 20 ball)
    elif cat == 2:
        if is_match(["207"], ["tashkil"]):
            score = 20
        elif is_match(["201", "202", "203", "204", "205", "206"], ["ishtirok"]):
            score = 10
        else:
            score = 10

    # 4. Odob-axloq va dress-kod (Maksimal 5 ball)
    elif cat == 4:
        score = 5

    # 5. Ko'rik-tanlov va olimpiadalar (Maksimal 10 ball)
    elif cat == 5:
        if is_match(["7"], ["Xalqaro"]):
            score = 10
        elif is_match(["8"], ["Respublika"]):
            score = {1: 9, 2: 8, 3: 7}.get(rank, 7)
        elif is_match(["9"], ["Viloyat"]):
            score = {1: 6, 2: 5, 3: 4}.get(rank, 4)
        elif is_match(["10"], ["OTM"]):
            score = {1: 3, 2: 2, 3: 1}.get(rank, 1)

    # 8. Volontyorlik (Maksimal 5 ball)
    elif cat == 8:
        score = 5

    # 9. Madaniy tashriflar (Maksimal 5 ball)
    elif cat == 9:
        if is_match(["901"], ["oyda kamida bir"]):
            score = 5
        elif is_match(["902"], ["ikki oyda"]):
            score = 3
        elif is_match(["903"], ["semestrda"]):
            score = 1
        else:
            score = 1

    # 10. Sport va sog'lom turmush (Maksimal 5 ball)
    elif cat == 10:
        if is_match(["11"], ["terma jamoa"]):
            score = 5
        elif is_match(["12"], ["seksiya"]):
            score = 3
        else:
            score = 1

    # 11. Boshqa ma'naviy faollik (Maksimal 5 ball)
    elif cat == 11:
        if is_match(["14"], ["Hamkor"]):
            score = 3
        elif is_match(["15"], ["Xiyobon", "Adiblar"]):
            score = 2
        else:
            score = 1

    # Hech bo'lmaganda 1 ball qaytarish (agar category topilsa)
    return min(score, max_allowed)