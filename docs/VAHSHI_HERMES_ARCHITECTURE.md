# VAHSHI × Hermes — معماری پیاده‌شده

> هرمس 5 ستون داره — ما هر 5 تا رو برای VAHSHI (مشاور کنکور) مهندسی کردیم، با تمرکز روی حافظه مخفی و اسکیل‌های مشاوره.

## نگاشت 1:1

| Hermes | VAHSHI | فایل |
|--------|--------|------|
| **SOUL.md** (هویت #1 پرامپت) | `data/memories/SOUL.md` + `vahshi/soul/loader.py` | cache-stable tier |
| **MEMORY.md + USER.md** (حافظه پایدار) | `data/memories/MEMORY.md` + `USER.md` + `vahshi/memory/manager.py` | frozen snapshot |
| **SessionDB FTS5** | `data/sessions/state.db` + `vahshi/memory/store.py` | جستجوی فول‌تکست |
| **Hidden Nudge** | `vahshi/memory/hidden_updater.py` — هر 3 پیام یا پیام مهم → سایلنت آپدیت | periodic nudge |
| **Skills (SKILL.md)** | `skills/*/SKILL.md` (8 اسکیل) + `vahshi/skills/registry.py` | procedural memory |
| **Self-Improving Loop** | `hidden_updater._maybe_evolve_skill()` — با 5/10/20 استفاده اسکیل رو خودکار بهبود میده | Observe→Crystallize |
| **Prompt Builder 3-tier** | `vahshi/agent/prompt_builder.py` — stable→context→volatile | prompt caching ready |
| **Context Compressor** | `vahshi/context/compressor.py` — خلاصه وسط، حفظ ابتدا/انتها | lossy summarization |
| **Agent Loop** | `vahshi/agent/loop.py` — VahshiAgent.step() | prompt→think→tool→memory |
| **Tools Registry** | `vahshi/tools/registry.py` + `toolsets` | 9 ابزار + 3 تولست |
| **Gateway** | `bot/telegram_bot.py` + `gateway/` ready | 20+ پلتفرم قابل افزودن |
| **Crons** | `vahshi/crons/scheduler.py` — 3 جاب پیش‌فرض + thread | daily 22:00, weekly, 02:00 |
| **Profiles** | `HERMES_HOME`-like via `data/` isolation | چند پروفایل با data جدا |

## حافظه مخفی — چطور کار می‌کنه؟

```python
# هر پیام کاربر:
updater.on_message(session_id, "user", text)
  → 1. ذخیره در FTS5
  → 2. اگر مهم (رشته/هدف/ضعف/تراز/استرس) یا counter%3==0:
        - USER.md رو سایلنت آپدیت کن (مثلا "رشته: تجربی")
        - MEMORY.md append (حقایق)
        - لاگ در _hidden_log.md (کاربر نمی‌بینه)
  → 3. اگر "برنامه" 3 بار تکرار شد → usage++ → در 5/10 بار اسکیل رو auto-improve کن
```

**پیام مهم = regex تشخیص:**
- رشته، پایه، هدف (پزشکی/مهندسی/...)
- ساعت مطالعه
- ضعف/قوت (زیست/شیمی/...)
- تراز، استرس

کاربر هیچ‌وقت نمی‌بینه «حافظه بروز شد» — فقط فایل‌ها عوض میشن.

## اسکیل‌ها — 8 تا مخصوص مشاور

| اسکیل | کار |
|-------|------|
| `konkoor-planner` | برنامه هفتگی — اصلی |
| `motivation-psych` | انگیزش + CBT |
| `test-analyzer` | تحلیل آزمون + دفتر اشتباهات |
| `resource-curator` | پیشنهاد منابع per رشته/سطح |
| `stress-manager` | مدیریت استرس جلسه |
| `progress-tracker` | پیگیری ساعت/تراز/تست |
| `night-review` | مرور شبانه 22:00 (cron) |
| `deep-research` | تحقیق عمیق با citation |

هر اسکیل `SKILL.md` با frontmatter YAML — قابل ویرایش توسط تو یا خود ایجنت.

## Crons — پیش‌فرض

```json
[
  {"id":"night_review","schedule":"daily 22:00","prompt":"جمع‌بندی روزانه"},
  {"id":"weekly_plan","schedule":"weekly friday 18:00","prompt":"برنامه هفته بعد"},
  {"id":"memory_compress","schedule":"daily 02:00","prompt":"فشرده‌سازی + بهبود اسکیل"}
]
```
Thread دائم هر 60 ثانیه چک می‌کنه — در `_hidden_log.md` لاگ میشه.

## API جدید (Hermes inspector)

- `GET /health` → حالا `hermes: {skills, cron_jobs, hidden_updater}`
- `GET /api/memory` → MEMORY.md + USER.md + SOUL + hidden_log tail
- `GET /api/skills` → لیست اسکیل‌ها
- `GET /api/crons` → جاب‌ها
- `POST /api/hidden/nudge` → فورس nudge

## آدرس فایل‌ها

```
VAHSHI/
├── data/
│   ├── memories/SOUL.md, MEMORY.md, USER.md, _hidden_log.md
│   ├── sessions/state.db (FTS5)
│   └── crons/jobs.json
├── skills/*/SKILL.md (8)
├── vahshi/
│   ├── memory/{store,manager,hidden_updater}.py
│   ├── skills/{registry,manager}.py
│   ├── soul/loader.py
│   ├── agent/{loop,prompt_builder}.py
│   ├── context/compressor.py
│   ├── crons/scheduler.py
│   └── tools/registry.py
└── app/main.py (Hermes loop integrated)
```

## ویژه برای تو وحشی

- **حافظه مخفی:** تو فقط چت می‌کنی، من پشت صحنه پروفایلت رو می‌سازم — دفعه بعد میگم «وحشی یادته گفتی زیست ضعیفه؟»
- **اسکیل خودبهبود:** هرچه بیشتر «برنامه» بخوای، اسکیل برنامه‌ریز دقیق‌تر میشه — بدون دخالت تو
- **امکانات مشاور:** هر 8 اسکیل نصب شد + cron شبانه فعال
- **قابل حمل:** کل `data/` و `skills/` رو زیپ کن، هرجا ببر — پروفایلت باهاته

---

*الهام از Hermes 228k⭐ — ولی قلبش VAHSHI و فارسی و کنکوری.*
