---
name: telegram-bot-kit
description: پروژه آماده ربات تلگرام یادآور مطالعه (توکن با کاربر)
version: 1.0.0
category: tools
tags: [telegram, bot]
---

# Telegram Bot Kit

## Reality
در Arena سشن تلگرام لاگین‌شده نداریم. تحویل = کد + راهنما.

## Deliverable path
`/home/user/.vahshi/tools/telegram_study_bot/`

## Features to include when building
- /start /plan /done /report /motivate
- یادآور ساعت‌های مطالعه
- ثبت دقیقه و تست
- پیام شبانه جمع‌بندی

## Deploy path for وحشی
1. BotFather → token
2. `.env` ← token
3. `pip install -r requirements.txt`
4. `python bot.py`
5. اختیاری: Railway/Render
