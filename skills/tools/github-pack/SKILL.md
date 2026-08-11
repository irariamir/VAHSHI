---
name: github-pack
description: بسته‌بندی ریپو برای بکاپ برنامه و مهارت‌ها
version: 1.0.0
category: tools
tags: [github, git]
---

# GitHub Pack

## Reality
پوش مستقیم به اکانت او از اینجا بدون credential نیست.

## Procedure
1. ساختار تمیز در workspace
2. README فارسی
3. `.gitignore` (نه کلید)
4. دستورات:
```bash
cd repo && git init && git add . && git commit -m "..."
# روی ماشین وحشی:
# gh auth login && git remote add origin ... && git push
```

## What to put in repo
- plans/
- trackers/
- optional: mirror of skills (بدون secrets)
