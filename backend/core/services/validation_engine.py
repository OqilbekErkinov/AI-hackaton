def validate_application(user, scholarship):
    profile = user.profile
    docs = user.documents.filter(status="approved")

    # Rule modelidan foydalanamiz (machine-readable logic)
    rules = scholarship.rules.all()

    errors = []

    for rule in rules:
        if rule.rule_type == "min_gpa":
            val = float(rule.value) if rule.value else 0
            user_gpa = profile.gpa or 0

            # Find the highest GPA score from uploaded transcript documents
            transcript_docs = docs.filter(doc_type="transcript")
            for d in transcript_docs:
                if d.meta and isinstance(d.meta, dict) and d.meta.get("score"):
                    try:
                        score = float(d.meta["score"])
                        if score > user_gpa:
                            user_gpa = score
                    except (ValueError, TypeError):
                        pass

            if user_gpa < val:
                errors.append(f"GPA ballingiz ushbu stipendiya uchun yetarli emas (Talab: {val}, Sizda: {user_gpa}).")

        elif rule.rule_type == "min_articles":
            count = docs.filter(doc_type="article").count()
            val = int(rule.value) if rule.value else 0
            if count < val:
                errors.append(f"Kamida {val} ta ilmiy maqola talab qilinadi. Sizda: {count}")

        elif rule.rule_type == "min_thesis":
            count = docs.filter(doc_type="thesis").count()
            val = int(rule.value) if rule.value else 0
            if count < val:
                errors.append(f"Kamida {val} ta tezis talab qilinadi. Sizda: {count}")

        elif rule.rule_type == "min_publications":
            count = docs.filter(doc_type="publication").count()
            val = int(rule.value) if rule.value else 0
            if count < val:
                errors.append(f"Kamida {val} ta boshqa nashr ishlari (kitob, qo'llanma) talab qilinadi. Sizda: {count}")

        elif rule.rule_type == "min_conferences":
            count = docs.filter(doc_type="conference").count()
            val = int(rule.value) if rule.value else 0
            if count < val:
                errors.append(f"Kamida {val} ta konferensiyada qatnashganlik diplomi/sertifikati talab qilinadi. Sizda: {count}")

        elif rule.rule_type == "require_language":
            # Nizom: Davlat tili + 1 Xorijiy (tillar yo'nalishi bo'lsa +2 Xorijiy)
            lang_count = docs.filter(doc_type="language_cert").count()
            if lang_count < 1:
                errors.append("Til bilish sertifikati yuklanmagan (Davlat tili va kamida bitta xorijiy til).")

        elif rule.rule_type == "require_ict":
            if not docs.filter(doc_type="ict_cert").exists():
                errors.append("Axborot texnologiyalarini bilish bo'yicha sertifikat yuklanmagan.")

        elif rule.rule_type == "require_history":
            if not docs.filter(doc_type="history_cert").exists():
                errors.append("O'zbekiston tarixi fanidan test/imtihon natijasi yuklanmagan.")

        elif rule.rule_type == "no_debt":
            if profile.has_debt:
                errors.append("Akademik qarzdorligi bor talabalar ariza topshira olmaydi.")

        elif rule.rule_type == "no_penalty":
            if profile.has_discipline_penalty:
                errors.append("Intizomiy jazosi bor talabalar ariza topshira olmaydi.")

    return errors