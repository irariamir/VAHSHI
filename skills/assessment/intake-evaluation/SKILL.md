---
name: intake-evaluation
description: ارزیابی اولیه کنکور — جمع‌آوری ۸ فیلد حیاتی قبل از هر برنامه
version: 1.1.0
category: assessment
tags: [intake, konkur, gate]
---

# Intake Evaluation

## When to Use
- اولین درخواست برنامه‌ریزی
- پروفایل ناقص است (`awaiting_intake: true`)

## Required fields
1. رشته (ریاضی/تجربی/انسانی/هنر/زبان)
2. پایه/وضعیت (یازدهم، دوازدهم، پشت‌کنکور، فارغ)
3. هدف (رشته/دانشگاه/حدود رتبه)
4. ساعت مطالعه روزانه فعلی (واقعی)
5. نقاط قوت
6. نقاط ضعف
7. زمان تقریبی تا کنکور
8. مدرسه/کلاس حضوری یا آزاد

## Procedure
1. اگر چند فیلد خالی است، دسته‌ای بپرس (نه بازجویی ۲۰ سوالی)
2. جواب‌ها را فوری در state بنویس:
```bash
python /home/user/.vahshi/agent.py intake stream=... grade=... goal=... daily_hours=... strengths=... weaknesses=... time_to_konkur=... school_or_free=...
```
3. تا complete نشده **برنامه کامل ماهانه نده** — حداکثر جهت کلی
4. بعد از complete → `level-diagnosis` سپس `master-planner`

## Tone
- رفیقانه؛ بگو بدون اینا برنامه می‌شه شعار
- سوالات از قبل «نگه داشته شده» را یادآوری کن اگر خودش خواسته بود بعداً برسیم
