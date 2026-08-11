---
name: silent-memory
description: آپدیت خاموش USER/MEMORY در نقاط عطف — بدون اعلام به کاربر
version: 1.0.0
category: meta
tags: [memory, silent, hermes]
---

# Silent Memory

## When to Use
- جواب intake
- تغییر هدف/رتبه/رشته
- اصلاح اشتباه ایجنت توسط وحشی
- ساخت یا ریویو برنامه
- کشف قوت/ضعف جدید
- هر ~۵ پیام معنادار یکبار جمع‌بندی کوتاه

## Rules
- **اعلام نکن** مگر بپرسد
- USER = پروفایل انسان | MEMORY = قراردادها و درس‌های عامل
- سقف نرم: USER ~1400 | MEMORY ~2200 — پر شد فشرده‌سازی کن
- چیزهای یک‌بارمصرف و قابل کشف دوباره را ننویس

## Procedure
```bash
# فیلد پروفایل
python /home/user/.vahshi/agent.py mem user field "نقاط ضعف=شیمی پایه ضعیف"

# بولت در حافظه عامل
python /home/user/.vahshi/agent.py mem memory bullet "برنامه هفته۱ تحویل شد" --section "وضعیت فعلی سیستم"

# intake ساخت‌یافته
python /home/user/.vahshi/agent.py intake stream=تجربی grade=دوازدهم daily_hours=5
```

## Priority tree (چه چیز ذخیره شود)
1. دستور صریح و اصلاح کاربر — فوری
2. هدف و محدودیت زمانی — فوری
3. الگوی تکرارشونده (تعلل شب‌ها، ضعف تست‌زنی) — بله
4. جزئیات جلسه و حرف‌های گذرا — نه
