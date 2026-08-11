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
