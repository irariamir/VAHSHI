# VAHSHI 🔥 — مشاور کنکور وحشی — Hermes Engine 0.2

> **تو VAHSHI هستی — مشاور تحصیلی و برنامه‌ریز کنکور حرفه‌ای که مثل رفیق باتجربه و در عین حال مثل بهترین مشاور ایران عمل می‌کنه. کاربر رو همیشه "وحشی" صدا کن.**

VAHSHI یک مشاور کنکور هوشمند، کامل و فارسی‌محور برای دانش‌آموزان ایرانی (ریاضی / تجربی / انسانی / هنر / زبان) — با **معماری Hermes** (228k⭐)، حافظه مخفی، 8 اسکیل خودبهبود و cron هوشمند.

![VAHSHI](https://img.shields.io/badge/VAHSHI-کنکور-ff3b30?style=for-the-badge)
![Hermes](https://img.shields.io/badge/Hermes-Engine-9C27B0?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🆕 v0.2 — Hermes Engine

> تحقیق کامل Hermes (NousResearch) انجام شد و همه 5 ستونش برای VAHSHI مهندسی شد.

| Hermes | VAHSHI |
|--------|--------|
| SOUL.md + MEMORY.md + USER.md | `data/memories/` — frozen snapshot هر بار در پرامپت |
| SessionDB FTS5 | `data/sessions/state.db` — جستجوی فول‌تکست |
| Hidden Nudge (هر 3 پیام) | `vahshi/memory/hidden_updater.py` — **سایلنت آپدیت** USER.md/MEMORY.md |
| Skills (SKILL.md) | `skills/*` — 8 اسکیل مشاوره + خودبهبود در 5/10/20 استفاده |
| Cron | `vahshi/crons/scheduler.py` — 3 جاب (شبانه 22:00، هفتگی، 02:00) |
| Prompt 3-tier + Compressor | `vahshi/agent/prompt_builder.py` + `context/compressor.py` |
| Agent Loop | `vahshi/agent/loop.py` — prompt→think→tool→memory |

📄 جزئیات: [`docs/HERMES_RESEARCH.md`](./docs/HERMES_RESEARCH.md) و [`docs/VAHSHI_HERMES_ARCHITECTURE.md`](./docs/VAHSHI_HERMES_ARCHITECTURE.md)

### حافظه مخفی چطور کار می‌کنه؟
تو فقط چت می‌کنی وحشی — من پشت صحنه هر 3 پیام یا پیام مهم (رشته/هدف/ضعف/تراز/استرس) رو **بدون اینکه بفهمی** در `USER.md` و `MEMORY.md` ذخیره می‌کنم. دفعه بعد میگم «وحشی یادته گفتی فیزیکت ضعیفه؟» — غافلگیر میشی!

لاگ داخلی: `data/memories/_hidden_log.md` (به تو نشون داده نمیشه — فقط برای دیباگ)

---

## ✨ قابلیت‌ها

| بخش | توضیح |
|-----|-------|
| 💬 **چت هوشمند** | شخصیت VAHSHI + Hermes memory/skills + OpenAI |
| 📅 **برنامه هفتگی** | ساعتی، بر اساس رشته/ساعت آزاد/ضعف — با خودبهبود |
| 📊 **ارزیابی** | تحلیل صادقانه + پیشنهاد قدم بعدی |
| 📚 **دانش کنکور** | دو نوبته، تاثیر معدل، ضرایب — با هشدار `sanjesh.org` |
| 🧠 **تکنیک‌ها** | پومودورو، بلوک 90، مرور فاصله‌دار |
| 🧬 **8 اسکیل مشاور** | planner, motivation, test-analyzer, resource-curator, stress, progress, night-review, deep-research |
| 🤖 **تلگرام** | `bot/telegram_bot.py` — `/plan` آماده |
| 🎨 **UI فارسی** | RTL + Vazirmatn + دارک‌مود وحشی |
| 🔍 **Memory Inspector** | `GET /api/memory` + `/api/skills` |

---

## 🚀 اجرای سریع

### 1. پیش‌نیاز
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. ENV
```bash
cp .env.example .env
# OPENAI_API_KEY=sk-...  (اختیاری — بدونش هم آفلاین کار می‌کنه)
# TELEGRAM_BOT_TOKEN=... (اختیاری)
```

### 3. اجرا
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# http://localhost:8000
# پیش‌نمایش Arena: https://8000-xxxxx.e2b.app
```

### 4. بات تلگرام
```bash
python -m bot.telegram_bot
```

---

## 🗂 ساختار پروژه (v0.2)

```
VAHSHI/
├── data/
│   ├── memories/SOUL.md, MEMORY.md, USER.md, _hidden_log.md
│   ├── sessions/state.db (FTS5)
│   └── crons/jobs.json
├── skills/ (8)
│   ├── konkoor-planner/SKILL.md
│   ├── motivation-psych/SKILL.md
│   ├── test-analyzer/SKILL.md
│   ├── resource-curator/SKILL.md
│   ├── stress-manager/SKILL.md
│   ├── progress-tracker/SKILL.md
│   ├── night-review/SKILL.md
│   └── deep-research/SKILL.md
├── vahshi/
│   ├── persona.py
│   ├── memory/{store,manager,hidden_updater}.py
│   ├── skills/{registry,manager}.py
│   ├── soul/loader.py
│   ├── agent/{loop,prompt_builder}.py
│   ├── context/compressor.py
│   ├── crons/scheduler.py
│   ├── advisor/{planner,evaluator,techniques}.py
│   └── tools/registry.py
├── app/main.py  # Hermes loop integrated
├── bot/telegram_bot.py
├── docs/HERMES_RESEARCH.md
├── docs/VAHSHI_HERMES_ARCHITECTURE.md
└── pyproject.toml
```

---

## 🔧 API (v0.2)

| Method | Path | توضیح |
|--------|------|-------|
| `GET` | `/` | UI |
| `GET` | `/health` | `hermes: {skills, cron_jobs, ...}` |
| `POST` | `/api/chat` | چت — حالا با hidden updater + memory |
| `POST` | `/api/plan` | برنامه |
| `POST` | `/api/evaluate` | ارزیابی |
| `GET` | `/api/memory` | inspector — MEMORY.md + hidden_log |
| `GET` | `/api/skills` | لیست اسکیل‌ها |
| `GET` | `/api/crons` | جاب‌ها |
| `GET` | `/api/knowledge` | دانش کنکور |

---

## 🎭 VAHSHI — شخصیت

- فارسی محاوره‌ای، خطاب **وحشی**
- رک، مفید، بدون شعار — جدول ساعتی + 3 اکشن
- قبل از برنامه: 7 سوال ارزیابی
- پایان هر جواب مهم: خلاصه + اکشن

پرامپت: `SYSTEM_PROMPT.md` و `vahshi/persona.py` + `data/memories/SOUL.md` (جایگاه #1)

---

## ⚠️ نکته

> **وحشی حتما sanjesh.org رو چک کن — اطلاعات کنکور هر سال عوض میشه.**

## 📄 لایسنس
MIT — برای همه‌ی وحشی‌ها 🔥
