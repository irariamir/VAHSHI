# VAHSHI 🔥 — مشاور کنکور وحشی — Hermes Engine 0.2

> **تو VAHSHI هستی — مشاور تحصیلی و برنامه‌ریز کنکور حرفه‌ای که مثل رفیق باتجربه و در عین حال مثل بهترین مشاور ایران عمل می‌کنه. کاربر رو همیشه "وحشی" صدا کن.**

VAHSHI یک مشاور کنکور هوشمند، کامل و فارسی‌محور — با **معماری Hermes** (228k⭐)، حافظه مخفی، 8 اسکیل خودبهبود و cron هوشمند.

## قانون
- حقیقت پایدار = این ریپو
- چت = سبک و اجرایی
- تلگرام پلن/تریک = فقط بعد تأیید

## ساختار (یکی‌شده: lean + Hermes)
- `soul/` هویت (SOUL.md جایگاه #1 پرامپت)
- `memories/` یا `data/memories/` — کاربر و حافظه عامل (USER.md, MEMORY.md)
- `skills/` مهارت‌ها (8 اسکیل هرمس) — SKILL.md
- `plans/` یا `data/` — برنامه‌ها (weekly-plan, maz_program, ghalamchi)
- `telegram/` کانال‌ها و ارسال تأییدشده
- `scripts/agent.py` کنترل محلی
- `vahshi/` هسته هرمس (memory, agent, skills, context)

## همگام‌سازی
```bash
./scripts/sync_from_github.sh
./scripts/sync_to_github.sh "msg"
# یا دستی:
git add -A && git commit -m "update" && git push origin main
git push origin arena/019fe630-vahshi
```

## 🆕 Hermes Engine
| Hermes | VAHSHI |
|--------|--------|
| SOUL.md + MEMORY.md + USER.md | `data/memories/` — frozen snapshot |
| SessionDB FTS5 | `data/sessions/state.db` |
| Hidden Nudge هر 3 پیام | `vahshi/memory/hidden_updater.py` — سایلنت |
| Skills SKILL.md | `skills/*` — 8 اسکیل |
| Cron | `vahshi/crons/scheduler.py` |

📄 جزئیات: `docs/HERMES_RESEARCH.md` و `docs/VAHSHI_HERMES_ARCHITECTURE.md` و `docs/FOR_AI.md`

## ✨ قابلیت‌ها
- چت هوشمند + حافظه مخفی هر 3 پیام
- برنامه هفتگی ساعتی
- 8 اسکیل مشاوره
- تلگرام bot ready
- UI فارسی RTL

---
*Branch اصلی: `main` — حافظه الان روی main هم هست. Branch کامل: `arena/019fe630-vahshi` — PR #1*
