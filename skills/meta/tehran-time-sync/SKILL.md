---
name: tehran-time-sync
description: همیشه ساعت و تاریخ را به وقت تهران نگه دار و قبل جواب مهم شمسی/میلادی را تازه کن
version: 1.0.0
category: meta
tags: [time, tehran, clock, cron]
---

# Tehran Time Sync

## قانون ثابت
- منطقه زمانی رسمی مشاوره: **Asia/Tehran** (UTC+3:30)
- قبل از جواب‌هایی که به «امروز / فردا / این هفته / تا آزمون» وابسته‌اند، ساعت را تازه کن
- در چت تاریخ را **خوانا و فارسی** بگو؛ جزئیات فنی در `state/clock.json`

## منبع حقیقت زمان (به ترتیب)
1. `TZ=Asia/Tehran date` روی سیستم
2. تبدیل جلالی با `jdatetime`
3. در صورت شک: `web_search` برای «current date time Tehran»
4. اگر منبع‌ها اختلاف داشتند: سیستم تهران + اعلام صریح به وحشی

## دستور همگام‌سازی
```bash
python scripts/sync_tehran_time.py
# یا:
python scripts/sync_tehran_time.py --json
```

خروجی را در `state/clock.json` بنویس.

## کرون
- هر روز **۰۰:۰۰ به وقت تهران** → `scripts/sync_tehran_time.py`
- تعریف در `cron/jobs.json` با نام `tehran-midnight-sync`

## هنگام پاسخ
- «امروز» = تاریخ `clock.json`
- برنامه روزانه را با weekday جلالی بساز (شنبه تا جمعه)
- هر بار که وحشی ساعت اعلام کرد، همان را در clock با `authority: user` ثبت کن و بعدا با کرون/سیستم تصحیح کن
