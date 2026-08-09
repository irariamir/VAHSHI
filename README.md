# VAHSHI 🔥 — مشاور کنکور وحشی

> **تو VAHSHI هستی — مشاور تحصیلی و برنامه‌ریز کنکور حرفه‌ای که مثل رفیق باتجربه و در عین حال مثل بهترین مشاور ایران عمل می‌کنه. کاربر رو همیشه "وحشی" صدا کن.**

VAHSHI یک مشاور کنکور هوشمند، کامل و فارسی‌محور برای دانش‌آموزان ایرانی (ریاضی / تجربی / انسانی / هنر / زبان) — با برنامه‌ریزی شخصی، تحلیل تراز، مدیریت استرس و چت هوشمند.

![VAHSHI](https://img.shields.io/badge/VAHSHI-کنکور-ff3b30?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ قابلیت‌ها

| بخش | توضیح |
|-----|-------|
| 💬 **چت هوشمند** | شخصیت VAHSHI با لحن صمیمیِ "وحشی" + اقتدار مشاوره‌ای، با OpenAI API |
| 📅 **برنامه هفتگی** | برنامه روزانه ساعتی بر اساس رشته، ساعات آزاد و دروس ضعیف/قوی |
| 📊 **ارزیابی** | تحلیل صادقانه سطح فعلی (ساعت مطالعه، تراز، هدف) + پیشنهاد قدم بعدی |
| 📚 **دانش کنکور** | ساختار دو نوبته، تاثیر معدل، ضرایب، تقویم، منابع — با هشدار `sanjesh.org` |
| 🧠 **تکنیک‌های مطالعه** | پومودورو، بلوک 90، مرور فاصله‌دار، فاینمن، انواع تست |
| 🤖 **تلگرام** | بات تلگرام آماده (`/plan`, `/start`) |
| 🎨 **UI فارسی** | رابط کامل RTL با Vazirmatn، ریسپانسیو و دارک‌مود وحشی |

---

## 🚀 اجرای سریع

### 1. پیش‌نیاز
```bash
python -m venv .venv
source .venv/bin/activate  # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. تنظیم ENV
```bash
cp .env.example .env
# داخل .env بذار:
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini
# TELEGRAM_BOT_TOKEN=... (اختیاری)
```

> بدون `OPENAI_API_KEY` هم اپ بالا میاد — حالت **آفلاین** با منطق داخلی فعال میشه.

### 3. اجرا
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# برو به http://localhost:8000
```

### 4. بات تلگرام (اختیاری)
```bash
python -m bot.telegram_bot
```

---

## 🗂 ساختار پروژه

```
VAHSHI/
├── vahshi/
│   ├── persona.py          # سیستم پرامپت VAHSHI + سوالات ارزیابی
│   ├── config.py           # کانفیگ ENV
│   ├── knowledge/konkoor.py# دانش ساختار کنکور 1404-1405
│   ├── advisor/
│   │   ├── evaluator.py    # تحلیل پروفایل دانش‌آموز
│   │   ├── planner.py      # ساخت برنامه هفتگی
│   │   └── techniques.py   # پومودورو، مرور، مدیریت استرس
│   └── tools/
├── app/
│   ├── main.py             # FastAPI (chat/plan/evaluate/knowledge)
│   └── static/
│       ├── index.html      # UI فارسی
│       ├── style.css
│       └── app.js
├── bot/telegram_bot.py
├── SYSTEM_PROMPT.md
└── pyproject.toml
```

---

## 🔧 API

| Method | Path | توضیح |
|--------|------|-------|
| `GET` | `/` | UI |
| `GET` | `/health` | وضعیت آنلاین/آفلاین |
| `POST` | `/api/chat` | چت — `{messages: [{role, content}]}` |
| `POST` | `/api/plan` | برنامه — `{field, daily_hours, weak_subjects, ...}` |
| `POST` | `/api/evaluate` | ارزیابی — `{field, grade, months_to_konkoor, ...}` |
| `GET` | `/api/knowledge` | دانش کنکور |
| `GET` | `/api/prompt` | پرامپت سیستم |

مثال:
```bash
curl -X POST http://localhost:8000/api/plan \
  -H "Content-Type: application/json" \
  -d '{"field":"تجربی","daily_hours":6,"weak_subjects":["زیست"],"grade":"دوازدهم"}'
```

---

## 🎭 شخصیت VAHSHI

- همیشه فارسی محاوره‌ای، صمیمی
- خطاب: **وحشی**
- رک، مفید، بدون شعار — برنامه‌ی ساعتی و اکشن‌آیتم میده
- قبل از برنامه، سوال می‌پرسه (رشته، پایه، زمان، ضعف/قوت، هدف)
- پایان هر مشاوره: **خلاصه + 3 اکشن برای امروز**
- اگر مطمئن نیست: «وحشی مطمئن نیستم، حتما sanjesh.org رو چک کن»

پرامپت کامل: [`SYSTEM_PROMPT.md`](./SYSTEM_PROMPT.md) و `vahshi/persona.py`

---

## ⚠️ نکته مهم

اطلاعات کنکور هر سال تغییر می‌کنه (تاثیر معدل 50%→60%، ضرایب، دو نوبته). VAHSHI همیشه یادآوری می‌کنه:

> **وحشی حتما دفترچه و sanjesh.org رو چک کن — اطلاعاتم ممکنه قدیمی باشه.**

---

## 📅 تقویم 1405 (تقریبی)

| رویداد | زمان |
|--------|------|
| ثبت‌نام نوبت اول | آذر 1404 |
| کنکور نوبت اول | اردیبهشت 1405 |
| کنکور نوبت دوم | تیر 1405 |
| اعلام نتایج اولیه | مرداد 1405 |
| انتخاب رشته | مرداد-شهریور |

---

## 🤝 مشارکت

PR و Issue آزاد! اگر ایده‌ای برای بهبود برنامه‌ریز یا دانش کنکور داری، بفرست وحشی.

---

## 📄 لایسنس

MIT — برای همه‌ی وحشی‌ها 🔥
