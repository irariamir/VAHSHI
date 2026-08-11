# تحقیق کامل Hermes — یکی‌شده (lean + arena)

# پژوهش Hermes Agent → طراحی VAHSHI
تاریخ: 2026-08-09  
منابع اصلی: Nous Research hermes-agent، مستندات practitioner، تحلیل حافظه Glukhov

## Hermes چیست؟
ایجنت متن‌باز (MIT) از Nous Research با حلقه یادگیری بسته:
- از تجربه skill می‌سازد
- حافظه را بین سشن‌ها نگه می‌دارد
- روی CLI و پیام‌رسان‌ها (تلگرام و ...) کار می‌کند
- model-agnostic است

## پنج ستون
1. **Memory** — پیوسته و curated
2. **Skills** — حافظه رویه‌ای (SKILL.md)
3. **Soul** — شخصیت ثابت (SOUL.md)
4. **Crons** — کار زمان‌بندی‌شده
5. **Self-improvement** — بهبود skill از روی بازخورد

## معماری حافظه Hermes (الگو)
| لایه | فایل/سیستم | نقش |
|------|------------|-----|
| Identity | SOUL.md | لحن و مرزها — اسلات ۱ پرامپت |
| User model | USER.md (~1375 chars) | پروفایل کاربر |
| Agent notes | MEMORY.md (~2200 chars) | قراردادها و درس‌ها |
| Episodic | SQLite FTS5 sessions | جستجوی تاریخچه |
| Procedural | skills/**/SKILL.md | رویه‌های قابل‌بارگذاری |
| External (اختیاری) | Honcho/Mem0/... | اینجا پیاده نشده |

فلسفه: حافظهٔ کوچکِ همیشه-داخل-پرامپت > دامپ عظیم بازیابی‌نشده.

## مهارت‌ها
- YAML frontmatter + Markdown
- progressive disclosure (اول ایندکس، بعد بدنه)
- سازگار با ایده agentskills.io
- agent می‌تواند skill جدید بنویسد و improve کند

## ترتیب اسمبل پرامپت (Hermes)
1. SOUL.md  
2. راهنمای ابزار  
3. MEMORY + USER  
4. skills guidance  
5. context فایل‌های پروژه  
6. timestamp / platform hints  

## آنچه در Arena نمی‌آید (و راه جایگزین VAHSHI)
| قابلیت Hermes | وضعیت اینجا | راه VAHSHI |
|---------------|-------------|------------|
| پروسس daemon دائمی | نیست | state روی دیسک + boot هر سشن |
| Gateway تلگرام زنده | بدون توکن/سشن | telegram-bot-kit آماده تحویل |
| 60+ tool OS-level | محدود به ابزار Arena | agent.py + ابزارهای Arena |
| LLM provider switch | مدل توسط Arena | N/A |
| vector DB خارجی | نیاز نیست | Markdown + JSONL search |

## نگاشت پیاده‌سازی
```
~/.hermes/          →  /home/user/.vahshi/
SOUL.md             →  SOUL.md
memories/USER.md    →  memories/USER.md
memories/MEMORY.md  →  memories/MEMORY.md
skills/             →  skills/**/SKILL.md
state.db            →  state/store.json + sessions/*.jsonl
cron/               →  cron/jobs.json
config.yaml         →  config.yaml
agent loop          →  Arena model + agent.py control plane
```

## حلقه خودبهبود VAHSHI
برخورد با مسئله → حل → (اختیاری) new-skill → استفاده بعدی → improve-skill از اصطکاک واقعی

---

## نسخه کامل Arena (228k⭐)

# تحقیق کامل Hermes Agent — برای مهندسی معکوس VAHSHI

**تاریخ:** 2026-08-09 | **منبع اصلی:** NousResearch/hermes-agent (228k ⭐, MIT) | **وبسایت:** hermes-agent.nousresearch.com

## خلاصه یک خطی
Hermes یک **ایجنت خودبهبود (self-improving)** است — نه فقط چت‌بات. بعد از هر تسک، فرآیندش رو به **Skill** (حافظه رویه‌ای Markdown) تبدیل می‌کنه و دفعه بعد همون اسکیل رو اجرا می‌کنه. هرچه بیشتر باهاش کار کنی باهوش‌تر میشه.

---

## 1. پنج ستون Hermes (5 Pillars)

| ستون | کار | فایل کلیدی |
|------|-----|-----------|
| **Memory** | حافظه پایدار: MEMORY.md + USER.md + SQLite FTS5 + Honcho/mem0 | `agent/memory_manager.py`, `hermes_state.py` |
| **Skills** | حافظه رویه‌ای: هر Skill یه `SKILL.md` که ایجنت خودش می‌سازه و بهبود میده | `agent/skill_commands.py`, `~/.hermes/skills/` |
| **Soul** | هویت: SOUL.md جایگاه #1 در سیستم پرامپت — شخصیت ایجنت | `~/.hermes/SOUL.md` |
| **Crons** | اتوماسیون زمان‌بندی: تسک‌های طبیعی‌زبان که سر ساعت اجرا میشن | `cron/scheduler.py` |
| **Self-Improving Loop** | حلقه بسته: Observe → Execute → Reflect → Crystallize → Reuse | `run_agent.py` |

### حلقه یادگیری بسته
```
Observe → Execute → Reflect → Crystallize → Reuse
   ↑                                        │
   └────── به صورت خودکار هر تسک ───────────┘
```
- بعد از تسک‌های 5+ ابزار یا حل مسئله سخت، ایجنت از خودش می‌پرسه: «آیا این فرآیند ارزش ذخیره داره؟»
- اگر آره → `SKILL.md` می‌سازه → دفعه بعد مستقیم اون رو اجرا می‌کنه (نه بازآفرینی)
- اسکیل‌ها با استفاده بهبود پیدا می‌کنن (self-curate)

---

## 2. معماری سه‌لایه

```
             ┌─────────────────────────────┐
             │      User Surfaces           │
             │ CLI·TUI·Gateway·Web·ACP·Cron │
             └──────────────┬──────────────┘
                            │
             ┌──────────────▼──────────────┐
             │        Agent Loop            │
             │ prompt→think→tool→obs→memory │
             └─┬──────────┬───────────┬────┘
               │          │           │
      ┌────────▼────┐ ┌───▼────┐ ┌────▼──────────┐
      │System Prompt│ │ Tools  │ │Skills (MD)    │
      │(cache-stable)│ │70+     │ │self-edited    │
      └─────────────┘ └───┬────┘ └───────────────┘
                          │
             ┌────────────▼──────────┐
             │ Execution Environment │
             │local·Docker·SSH·Modal │
             └───────────────────────┘
                          │
             ┌────────────▼──────────┐
             │       Memory          │
             │Frozen·FTS5·Honcho     │
             └───────────────────────┘
```

- **Tier 1 — Surfaces:** CLI, Gateway (20+ پلتفرم: Telegram, Discord, Slack, WhatsApp, Signal...), Web UI, ACP (VS Code)
- **Tier 2 — Core:** AIAgent (run_agent.py) + PromptBuilder + ToolRegistry + ContextCompressor + AuxiliaryClient
- **Tier 3 — Backends:** Terminal backends (local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox)

---

## 3. حافظه — سه لایه + مدل کاربر

1. **Frozen-snapshot persistent memory:** لاگ append-only که تو بخش cache-stable پرامپت تزریق میشه — کوچک، فشرده، همیشه لود
2. **SessionDB (SQLite FTS5):** تمام سشن‌های قبلی با جستجوی فول‌تکست — recall = search + LLM summarize
3. **Skills (procedural memory):** رویه‌ها — جدا از facts
4. **User Modeling (Honcho):** مدل دیالکتیکی کاربر — ترجیحات، تاریخ تصمیمات، الگوهای کاری

فایل‌های فیزیکی:
```
~/.hermes/
├── SOUL.md              # هویت — اسلات #1 پرامپت
├── memories/
│   ├── MEMORY.md        # حقایق پایدار (durable facts)
│   └── USER.md          # پروفایل کاربر
├── skills/              # همه اسکیل‌های فعال
├── state.db             # SQLite + FTS5 — تمام سشن‌ها
├── sessions/            # ایندکس gateway
├── cron/                # جاب‌های زمان‌بندی
└── config.yaml + .env
```

**Periodic Nudge:** ایجنت هر چند ترن یکبار به خودش یادآوری می‌کنه «چی رو باید به حافظه بسپارم؟» تا حافظه curated بمونه نه dump.

---

## 4. Skills — استاندارد agentskills.io

- هر Skill یه پوشه با `SKILL.md` (Markdown) + اختیاری `scripts/`
- **خودساخته توسط ایجنت** (نه فقط انسان) — بعد از تسک موفق ساخته میشه
- **خودبهبود:** با شواهد جدید بازنویسی میشه
- **قابل حمل:** استاندارد باز agentskills.io — بین Hermes, Claude Code, Cursor قابل اشتراک
- **118 باندل + هزاران در Hub:** دسته‌بندی رسمی + کامیونیتی
- **امنیت:** اسکنر امنیتی + تایید دستی (`/skills approval`)

نمونه SKILL.md:
```markdown
---
name: konkoor-planner
description: برنامه هفتگی کنکور بر اساس رشته و ساعت مطالعه
---
# Konkoor Planner
...
## Workflow
1. ارزیابی اولیه
2. تحلیل
...
```

---

## 5. سیستم Tools — 70+ ابزار + MCP

| دسته | ابزارها |
|------|---------|
| File | read_file, write_file, patch, search_files |
| Terminal | terminal (sudo, env, backends) |
| Web | web_search, web_extract (Parallel/Firecrawl) |
| Browser | 10 ابزار اتوماسیون مرورگر |
| Memory | memory (save/retrieve), session_search |
| Skills | skill_manage, skill_search |
| Delegation | delegate (subagent) |
| Code | execute_code (sandbox) |
| Cron | cron jobs |
| Vision | image analysis |

- **Registry pattern:** هر ابزار خودش رو ثبت می‌کنه
- **MCP Client + Server:** هم به سرورهای خارجی وصل میشه، هم خودش سرور میشه
- **Approval:** تشخیص دستورات خطرناک + تایید کاربر

---

## 6. Gateway — 20+ پلتفرم

Single `GatewayRunner` که همه آداپترها رو مدیریت می‌کنه:
- Bundled: Signal, Weixin, QQ, WhatsApp Cloud
- Plugins: Telegram, Discord, Slack, Matrix, Email, Feishu, DingTalk, Line, Teams...
- قابلیت: pairing auth, session continuity, cross-session mirroring, cron delivery

---

## 7. Context Management

- **PromptBuilder:** ساختار 3-tier (stable → context → volatile) برای cache efficiency
- **PromptCaching:** Anthropic cache breakpoints
- **ContextCompressor:** خلاصه‌سازی lossy وقتی به سقف توکن نزدیک میشیم — خلاصه وسط مکالمه، ابتدا و انتها دست‌نخورده
- **AuxiliaryClient:** تسک‌های جانبی (vision, summarization) رو به مدل fallback میفرسته تا هزینه کم شه

---

## 8. Profiles & Isolation

- هر پروفایل = یه `HERMES_HOME` جدا (config, memory, skills, sessions, gateway)
- `hermes -p work` → `~/.hermes/profiles/work/`
- ایزوله‌سازی: هر ایجنت .env و API key جدا — اصل least-privilege
- اشتراک: پروفایل رو میشه به عنوان git repo پکیج کرد و با `hermes profile install` نصب کرد

---

## 9. Cron & Automation

- زمان‌بندی با زبان طبیعی: «هر روز 8 صبح گزارش بده»
- تحویل به هر پلتفرم (CLI, Telegram...)
- اسکن prompt injection برای جاب‌ها

---

## 10. تمایز Hermes vs OpenClaw vs GoClaw

|  | Hermes | OpenClaw | GoClaw |
|--|--------|----------|--------|
| زبان | Python 88% | TS/Node | Go 1.26+React |
| استار | 228k | بالا | 3.1k |
| حافظه | Frozen+FTS5+Honcho | AGENTS.md/SOUL.md | 3-tier+pgvector |
| اسکیل | خودساخته، خودبهبود | انسان‌ساخته (ClawHub 13k+) | Vault+wikilinks |
| خودبهبود | حلقه بسته + DSPy/GEPA | دستی | guardrailed |
| بک‌اند | 7 نوع | Docker/SSH | Docker |

---

## 11. درس‌های کلیدی برای VAHSHI

1. **حلقه یادگیری بسته رو کپی کنیم:** بعد از هر مشاوره مهم، اتومات Skill بساز/بهبود بده
2. **حافظه سه‌لایه:** MEMORY.md (facts) + Session FTS5 (recall) + Skills (procedures)
3. **Periodic Nudge مخفی:** هر 3 پیام یا پیام مهم → بروزرسانی مخفی حافظه — کاربر نفهمه
4. **SOUL.md:** هویت VAHSHI جایگاه #1 پرامپت
5. **Skills به عنوان Markdown:** قابل ویرایش توسط ایجنت و انسان
6. **Gateway-ready:** همین الان Telegram داریم، بقیه پلتفرم‌ها قابل افزودن
7. **Prompt Stability:** سیستم پرامپت mid-conversation عوض نشه — cache-friendly
8. **Tool Registry:** همه قابلیت‌ها به عنوان Tool ثبت بشن

---

*منبع: NousResearch/hermes-agent docs, GitHub, Medium deep-dives — آگوست 2026*