import os
import re

class RAGService:
    _cached_chunks = None

    @classmethod
    def _get_knowledge_dir(cls):
        # Base directory where core/knowledge resides
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "knowledge")

    @classmethod
    def load_chunks(cls):
        """
        Knowledge base matnlarini kichik, ma'noli bo'laklarga (headings + paragraphs) bo'lib yuklaydi va keshlaydi.
        """
        if cls._cached_chunks is not None:
            return cls._cached_chunks

        chunks = []
        kb_dir = cls._get_knowledge_dir()
        
        if not os.path.exists(kb_dir):
            print(f"RAG WARNING: Knowledge directory not found at {kb_dir}")
            return []

        for fn in os.listdir(kb_dir):
            if fn.endswith(".md"):
                fp = os.path.join(kb_dir, fn)
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()

                # Markdown faylini sarlavhalar (h2, h3 va h1) bo'yicha ajratamiz
                sections = re.split(r'\n(?=#{1,3}\s)', content)
                for sec in sections:
                    sec = sec.strip()
                    if not sec:
                        continue
                    
                    # Birinchi satr sarlavha bo'ladi
                    lines = sec.split("\n")
                    heading = lines[0].replace("#", "").strip()
                    body = "\n".join(lines[1:]).strip()
                    
                    chunks.append({
                        "file": fn,
                        "heading": heading,
                        "content": f"Hujjat: {fn[:-3].replace('_', ' ').title()}\nMavzu: {heading}\nQoida matni:\n{body}"
                    })

        cls._cached_chunks = chunks
        print(f"RAG: Loaded {len(chunks)} chunks from Knowledge Base successfully!")
        return chunks

    @classmethod
    def search(cls, query, limit=3):
        """
        Talaba bergan savolga ko'ra eng mos keladigan 3 ta qonunchilik bandini topadi.
        Oddiy, juda tez va ishonchli kalit so'zlar mosligi (keyword matching) algoritmi.
        """
        chunks = cls.load_chunks()
        if not chunks:
            return ""

        query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]
        scored_chunks = []

        for chunk in chunks:
            score = 0
            content_lower = chunk["content"].lower()
            heading_lower = chunk["heading"].lower()
            
            for word in query_words:
                # Sarlavhadagi moslikka yuqori koeffitsient beramiz
                if word in heading_lower:
                    score += 5
                # Matn ichidagi moslik
                score += content_lower.count(word)

            if score > 0:
                scored_chunks.append((score, chunk))

        # Ballar bo'yicha saralash
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [item[1]["content"] for item in scored_chunks[:limit]]
        
        if not top_chunks:
            # Agar moslik topilmasa, eng muhim boshlang'ich qoidalarni qaytaramiz
            return "\n\n---\n\n".join([c["content"] for c in chunks[:limit]])

        return "\n\n---\n\n".join(top_chunks)
