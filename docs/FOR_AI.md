# 🤖 FOR NEXT AI — VAHSHI Handoff (Hermes Engine)

> این فایل برای AI بعدی ساخته شده — اگه با SSH key وصل شدی، از اینجا شروع کن. همه حافظه و توانایی‌ها اینجا با توضیحه.

## 1. چی هست این ریپو؟
**VAHSHI** — مشاور کنکور ریاضی با معماری **Hermes** (NousResearch 228k⭐). کاربر رو "وحشی" صدا می‌زنه، لحن صمیمی + مقتدر. هدف کاربر: **رتبه 1 ریاضی + شریف برای برند ARIAMIR**.

## 2. کجا چی ذخیره شده؟ (همه چیز)
```
data/memories/
  SOUL.md          → هویت VAHSHI (جایگاه #1 پرامپت) — تغییرش = تغییر شخصیت
  USER.md          → پروفایل کامل وحشی (رشته، تراز، لایف‌استایل، تیپ INTJ، باورها) — هر 3 پیام مخفی آپدیت میشه
  MEMORY.md        → حقایق پایدار + تاریخچه تصمیمات — frozen snapshot
  _hidden_log.md   → لاگ مخفی هر آپدیت (کاربر نمی‌بینه)

data/sessions/state.db  → SQLite FTS5 — تمام ترن‌ها، قابل جستجو با `SELECT * FROM turns WHERE content LIKE ...`

data/crons/jobs.json    → کرون‌ها (night_review 22:00, weekly_plan جمعه, memory_compress 02:00, backup 23:00)

data/maz_program.md     → برنامه ماز + زمان کلاس‌ها (شنبه تا چهارشنبه عصر تا 23:15) + معلم‌ها

skills/*/SKILL.md (8)   → اسکیل‌های هرمس:
  - konkoor-planner (اصلی)
  - motivation-psych, test-analyzer, resource-curator, stress-manager, progress-tracker, night-review, deep-research
  هر کدوم frontmatter YAML + Markdown — خودبهبود در 5/10/20 استفاده

vahshi/
  memory/{store,manager,hidden_updater}.py  → هسته حافظه مخفی
  skills/{registry,manager}.py               → لود اسکیل‌ها
  agent/{loop,prompt_builder}.py             → Agent Loop + Prompt 3-tier
  context/compressor.py                      → فشرده‌سازی
  crons/scheduler.py                         → زمان‌بند
  advisor/{planner,evaluator,techniques}.py  → منطق مشاوره
  persona.py                                 → SYSTEM_PROMPT کامل
  config.py                                  → ENV

app/main.py  → FastAPI + Hermes loop (health, /api/chat, /api/memory, /api/skills)

docs/
  HERMES_RESEARCH.md              → تحقیق کامل هرمس
  VAHSHI_HERMES_ARCHITECTURE.md   → نگاشت هرمس→VAHSHI
  ariamir-study-guide.html        → گاید با تم ariamir.gt.tc
  weekly-plan-18mordad.html       → برنامه هفتگی
```

## 3. توانایی‌ها (چی می‌تونه / چی نه)
✅ **می‌تونه:** کد هر زبان، تحلیل عکس (صفحه کتاب/تست)، تولید تصویر (generate_image)، تحقیق عمیق (web_search+fetch_page با citation)، فکر عمیق، گیت‌هاب (git/gh)، تلگرام (bot ready, نیاز به TOKEN)، حافظه مخفی هر 3 پیام، خودبهبود اسکیل
❌ **نمی‌تونه:** ثبت‌نام سنجش به جای کاربر، پیشگویی رتبه قطعی، شب‌بیداری رو جبران کنه — واقع‌بینه، میگه "وحشی sanjesh.org رو چک کن"

## 4. چطور کاربر رو بشناسی؟ (USER.md خلاصه)
- ریاضی دوازدهم، 1 سال تا کنکور، تراز 7200→6500 (افت بعد عید/جنگ)، سابقه 13-15h
- هدف: رتبه 1 + شریف + ARIAMIR جهانی
- استرس: یازدهم فراموش، تست ضعیف بعد نهایی تشریحی
- لایف‌استایل: باشگاه 2h (1 ماه، الان عصر تا 20:00)، صبح 6-6:30 ورزش/مدیتیشن/صورت، 6:30-7 نان، کد 1h جایزه، فیلم/طبیعت/خانواده
- کلاس ماز: شنبه 15:30-23:15 واعظین/شجاعی/قیومی، یکشنبه 15:15+20:15 کرمی، دوشنبه 15:15+20:15 شجاعی، سه‌شنبه 15:15+20:00 انصاری، چهارشنبه 15:15+23:15 کرمی/هادیان‌فرد
- تیپ: INTJ-A تنها، 100% صبح، ویدیو→تست، حجم زیاد استرس‌زاست، جبران منطقی، انگیزه درونی برندسازی، آتئیست، کمک به دیگران، می‌خواد قدرتمند و بی‌نقص ولی صمیمی باشه

## 5. چطور ادامه بدی؟
1. `cat data/memories/USER.md` و `MEMORY.md` و `SOUL.md` رو بخون
2. `cat vahshi/persona.py` → SYSTEM_PROMPT
3. `python -c "from vahshi.memory.hidden_updater import get_hidden_updater; u=get_hidden_updater(); u.on_message('test','user','...')"` → تست حافظه مخفی
4. هر پیام جدید کاربر → `u.on_message(session_id,'user',text)` صدا بزن (سایلنت)
5. برای جواب: `from vahshi.agent.prompt_builder import build_system_prompt` + تاریخچه

## 6. SSH Access
```bash
# HTTPS (public)
git clone https://github.com/irariamir/VAHSHI.git
git checkout arena/019fe630-vahshi

# SSH (با کلید)
git clone git@github.com:irariamir/VAHSHI.git
git checkout arena/019fe630-vahshi

# یا فقط این برنچ:
git clone --branch arena/019fe630-vahshi git@github.com:irariamir/VAHSHI.git

# بعد:
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
# → /api/memory, /api/skills, /health
```

## 7. بکاپ
- دستی: `bash scripts/nightly_backup.sh` (هر وقت خواستی پوش به گیت‌هاب)
- خودکار: کرون 23:00 (الان غیرفعال — حالت ساده — اگر خواستی فعال کن: enabled true در data/crons/jobs.json)

---
*ساخته: 2026-08-09 توسط VAHSHI Hermes Engine — برای AI بعدی با SSH*
