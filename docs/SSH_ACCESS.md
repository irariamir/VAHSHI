# 🔑 SSH Access — برای AI که با SSH key وصل میشه

این ریپو برای اتصال AI via SSH آماده است. دو راه:

## 1. کلون via SSH (نیاز به Deploy Key)

در گیت‌هاب:
1. برو `irariamir/VAHSHI → Settings → Deploy keys → Add deploy key`
2. کلید عمومی AI رو Paste کن (Title: `vahshi-ai` / Allow write access: ✅ اگر می‌خواد پوش کنه)
3. از طرف AI:

```bash
# clone
git clone git@github.com:irariamir/VAHSHI.git
cd VAHSHI
git checkout arena/019fe630-vahshi

# یا مستقیم برنچ:
git clone --branch arena/019fe630-vahshi git@github.com:irariamir/VAHSHI.git

# بررسی حافظه:
cat data/memories/USER.md
cat data/memories/MEMORY.md
cat data/memories/SOUL.md
cat docs/FOR_AI.md
ls skills/
cat data/export/VAHSHI_snapshot.json | head -n 50

# اجرای سرور:
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 2. کلون via HTTPS (بدون SSH — public)

```bash
git clone --branch arena/019fe630-vahshi https://github.com/irariamir/VAHSHI.git
```

## 3. دسترسی سریع بدون کلون (API)

```bash
curl -s https://raw.githubusercontent.com/irariamir/VAHSHI/arena/019fe630-vahshi/data/memories/USER.md
curl -s https://raw.githubusercontent.com/irariamir/VAHSHI/arena/019fe630-vahshi/docs/FOR_AI.md
curl -s https://raw.githubusercontent.com/irariamir/VAHSHI/arena/019fe630-vahshi/data/export/VAHSHI_snapshot.json
```

## 4. برای AI: چطور حافظه رو بخونه؟

```python
from vahshi.memory.manager import get_memory_manager
mm = get_memory_manager()
print(mm.build_prompt_block())  # SOUL + MEMORY + USER

from vahshi.skills.registry import discover_skills
for s in discover_skills():
    print(s.name, s.description)
```

## 5. امنیت
- این ریپو public نیست؟ اگر private بود، Deploy Key لازمه. اگر publicه، HTTPS کافیه.
- برای نوشتن (push) نیاز به Write accessه — وگرنه فقط Read.

---
*Branch: arena/019fe630-vahshi — PR: #1*
