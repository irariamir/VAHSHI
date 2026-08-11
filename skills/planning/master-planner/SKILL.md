---
name: master-planner
description: ساخت برنامه هفتگی/ماهانه عملی بعد از intake کامل
version: 1.0.0
category: planning
tags: [plan, weekly, monthly]
---

# Master Planner

## Gate
بدون intake کامل وارد نشو → `intake-evaluation`

## Inputs
- فیلدهای intake + level-diagnosis
- محدودیت مدرسه/خواب/ورزش

## Design principles
1. اولویت = اثر کنکوری (ضریب × ضعف × قابلیت رشد در بازه)
2. هر روز: بلوک آموزش + تست + مرور (حتی کوتاه)
3. یک درس ضعیف را در هفته خفه نکن — توزیع هوشمند
4. روز ریکاوری سبک داشته باش
5. قابل اندازه‌گیری: ساعت، تعداد تست، مبحث

## Output structure
- هدف هفته (۱ جمله)
- جدول روزانه (مبحث + دقیقه + نوع کار)
- هدف تست هفتگی
- شاخص موفقیت هفته (۳ مورد)
- چیزهایی که عمداً این هفته نیست

## After delivery
```bash
python /home/user/.vahshi/agent.py mem memory bullet "plan week delivered" --section "وضعیت فعلی سیستم"
python /home/user/.vahshi/agent.py log assistant "plan: ..."
```
stats.plans_created++ via state if needed

## Optional
- `visual-plan` برای تصویر جدول
- `tracker-export` برای excel/markdown
