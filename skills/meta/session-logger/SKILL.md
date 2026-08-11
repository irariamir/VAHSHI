---
name: session-logger
description: ثبت نقاط مهم گفتگو برای جستجوی بعدی (معادل session FTS هرمس)
version: 1.0.0
category: meta
tags: [session, log, search]
---

# Session Logger

## When to Use
- پایان یک تصمیم مهم (برنامه، هدف، منبع)
- وقتی وحشی گزارش عملکرد هفتگی می‌دهد
- قبل از ساخت skill از روی تجربه

## Procedure
```bash
python /home/user/.vahshi/agent.py log user "خلاصه حرف وحشی..."
python /home/user/.vahshi/agent.py log assistant "خلاصه تصمیم/برنامه..."
python /home/user/.vahshi/agent.py search "شیمی"
```

## Notes
- کل چت را دامپ نکن؛ چکیده عملی
- latest.json خودکار به‌روز می‌شود
