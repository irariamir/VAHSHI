"""
Evaluator - تحلیل اولیه دانش‌آموز
"""
from dataclasses import dataclass
from typing import Literal

Field = Literal["تجربی", "ریاضی", "انسانی", "هنر", "زبان"]
Level = Literal["دهم", "یازدهم", "دوازدهم", "پشت‌کنکوری", "فارغ‌التحصیل"]

@dataclass
class StudentProfile:
    field: str = ""
    grade: str = ""
    months_to_konkoor: int = 10
    daily_hours: float = 0
    strong_subjects: list = None
    weak_subjects: list = None
    target: str = ""
    azmoon_taraz: int | None = None
    sleep_hours: float = 7
    school_hours: float = 6

    def __post_init__(self):
        if self.strong_subjects is None:
            self.strong_subjects = []
        if self.weak_subjects is None:
            self.weak_subjects = []

def evaluate_student(p: StudentProfile) -> str:
    """تحلیل صادقانه وضعیت"""
    lines = []
    lines.append(f"### تحلیل وضعیت وحشی\n")
    lines.append(f"- رشته: **{p.field or 'نامشخص'}** | پایه: **{p.grade or 'نامشخص'}** | تا کنکور: **{p.months_to_konkoor} ماه**")
    lines.append(f"- مطالعه فعلی: **{p.daily_hours} ساعت/روز** | هدف: **{p.target or 'نامشخص'}**")

    # سطح
    if p.daily_hours == 0:
        lines.append("\n> وحشی هنوز استارت نزدی؟ اشکال نداره، از همین امروز شروع می‌کنیم. مهم پیوستگیه نه کمال.")
    elif p.daily_hours < 4:
        lines.append("\n> وحشی با زیر 4 ساعت، برای رتبه خوب باید شیب رو تند کنی. ولی نگران نباش، پله‌پله می‌بریم بالا.")
    elif p.daily_hours < 7:
        lines.append("\n> وحشی رنج خوبیه. اگه با کیفیت بخونی (تست + مرور)، ترکونده‌ای.")
    else:
        lines.append("\n> وحشی دمت گرم! 7+ ساعت یعنی جدی هستی. فقط حواست به فرسودگی باشه — کیفیت > کمیت.")

    if p.azmoon_taraz:
        if p.azmoon_taraz < 5000:
            lines.append(f"- تراز {p.azmoon_taraz}: پایه‌ات ضعیفه وحشی، باید برگردیم عقب و مفاهیم پایه رو ببندیم. عجله برای تست سنگین نکن.")
        elif p.azmoon_taraz < 6000:
            lines.append(f"- تراز {p.azmoon_taraz}: متوسط رو به خوب. با برنامه منظم 2-3 ماهه می‌تونی 1000 تا بکشی بالا.")
        elif p.azmoon_taraz < 7000:
            lines.append(f"- تراز {p.azmoon_taraz}: عالیه وحشی! تو محدوده رقابتی هستی. الان تمرکز روی نکته‌تست و آزمون‌خطاست.")
        else:
            lines.append(f"- تراز {p.azmoon_taraz}: وحشی تو دیگه وحشی واقعی هستی! فقط تثبیت و مدیریت آزمون می‌خوای.")

    if p.weak_subjects:
        lines.append(f"\n**نقاط ضعف اعلامی:** {', '.join(p.weak_subjects)} → اولویت 1 در برنامه")
    if p.strong_subjects:
        lines.append(f"**نقاط قوت:** {', '.join(p.strong_subjects)} → حفظ با مرور هفتگی، نه حذف")

    lines.append("\n---\n**قدم بعدی:** بر اساس این تحلیل، برنامه هفتگی اختصاصی می‌دم. آماده‌ای وحشی؟")
    return "\n".join(lines)
