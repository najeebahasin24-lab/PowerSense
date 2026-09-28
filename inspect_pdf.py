import fitz

doc = fitz.open(r"C:\Users\hp\.gemini\antigravity-ide\brain\b678501c-d583-4e0c-8f02-6ace25df98db\.user_uploaded\media_1790083767617.pdf")
for i in [0, 1, 3, 4, 6, 7, 8, 9]:
    page = doc[i]
    print(f"=== Page {i+1} ===")
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    txt = s["text"].strip()
                    if txt:
                        print(f"  size={s['size']:.1f}, font={s['font']}, color={s['color']:06x}: {txt[:45]}")
