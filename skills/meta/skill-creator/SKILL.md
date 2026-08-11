---
name: skill-creator
description: از تجربه سخت، مهارت قابل‌استفاده دوباره بساز (حلقه خودبهبود Hermes)
version: 1.0.0
category: meta
tags: [skills, learning-loop, hermes]
---

# Skill Creator

## When to Use
- مسئله چندمرحله‌ای سخت حل شد و احتمال تکرار دارد
- وحشی الگوی تکراری دارد (مثلاً هر یکشنبه ریویو غلط‌ها)
- روش مشاوره‌ای جدیدی برای این کاربر جواب داد

## Procedure
1. اسم کوتاه kebab-case انتخاب کن
2. دسته درست: assessment | planning | konkur | psychology | resources | tools | meta
3. بدنه skill: When / Steps / Pitfalls / Verification
4. بساز:
```bash
python /home/user/.vahshi/agent.py new-skill my-skill planning "توضیح یک‌خطی" --body "$(cat <<'EOF'
# Title
## When to Use
...
## Procedure
1.
## Pitfalls
-
## Verification
-
EOF
)"
```
5. بعداً با بازخورد واقعی improve کن:
```bash
python /home/user/.vahshi/agent.py improve-skill my-skill "اگر ساعتش زیر ۳ بود بلوک مرور را نصف کن"
```

## Quality bar
- مهارت = رویه، نه مقاله
- بدون عدد جعلی کنکور
- قابل اجرای دوباره بدون چت قبلی
