"""
VAHSHI Hidden Updater — بروزرسانی مخفی حافظه و اسکیل‌ها
Hermes periodic nudge inspired

- هر 3 پیام یا پیام مهم → به صورت سایلنت MEMORY.md / USER.md و اسکیل‌ها رو آپدیت می‌کنه
- کاربر هیچ لاگی نمی‌بینه — فقط در فایل‌ها ثبت میشه
- تشخیص پیام مهم: هدف، رشته، ضعف/قوت، ساعت مطالعه، استرس، تاریخ کنکور
"""
import re
import pathlib
from .manager import get_memory_manager

IMPORTANT_PATTERNS = [
    (r"(رشته\s*[:：]?\s*(تجربی|ریاضی|انسانی|هنر|زبان))", "رشته"),
    (r"(دهم|یازدهم|دوازدهم|پشت\s*کنکور)", "پایه"),
    (r"(پزشکی|دندان|دارو|مهندسی|حقوق|روانشناسی|هدفم|میخوام.*دانشگاه)", "هدف"),
    (r"(\d+\s*ساعت.*مطالعه|روزانه.*\d+)", "ساعت مطالعه"),
    (r"(ضعیف.*|قوی.*|زیست|فیزیک|شیمی|ریاضی|عربی|ادبیات)", "ضعف/قوت"),
    (r"(استرس|اضطراب|خسته|ناامید|اهمال|کمال\s*گرا)", "روانشناسی"),
    (r"(تراز\s*\d+|قلم.?چی|گاج|ماز)", "تراز"),
]

def is_important(text: str) -> tuple[bool, str]:
    for pat, tag in IMPORTANT_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True, tag
    return False, ""

class HiddenUpdater:
    def __init__(self):
        self.mm = get_memory_manager()
        self.counter = 0
        self.log_path = pathlib.Path("data/memories/_hidden_log.md")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("# Hidden Updater Log (internal — not shown to user)\n", encoding="utf-8")

    def _log(self, msg: str):
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"- [{ts}] {msg}\n")

    def _extract_and_update_user(self, text: str):
        # رشته
        m = re.search(r"رشته[^:：]*[:：]?\s*(تجربی|ریاضی|انسانی|هنر|زبان)", text)
        if m:
            self._update_user_field("رشته", m.group(1))
        m = re.search(r"(دهم|یازدهم|دوازدهم|پشت.?کنکوری)", text)
        if m:
            self._update_user_field("پایه", m.group(1))
        m = re.search(r"(\d+(?:\.\d+)?)\s*ساعت", text)
        if m:
            self._update_user_field("ساعت مطالعه", m.group(1) + " ساعت")
        # هدف — capture next words
        if "پزشکی" in text:
            self._update_user_field("هدف", "پزشکی")
        elif "مهندسی" in text:
            self._update_user_field("هدف", "مهندسی")
        # ضعف
        # simple heuristic: if mentions ضعیف + subject
        weak = re.findall(r"(زیست|شیمی|فیزیک|ریاضی|عربی|ادبیات|فلسفه|اقتصاد)", text)
        if weak and ("ضعیف" in text or "ضعف" in text):
            self._update_user_field("نقاط ضعف", ", ".join(set(weak)))

    def _update_user_field(self, field: str, value: str):
        p = pathlib.Path("data/memories/USER.md")
        txt = p.read_text(encoding="utf-8")
        # replace line like "- رشته: نامشخص" -> "- رشته: تجربی"
        pattern = rf"(- {re.escape(field)}:\s*)(.*)"
        if re.search(pattern, txt):
            txt = re.sub(pattern, rf"\g<1>{value}", txt)
        else:
            txt += f"\n- {field}: {value}"
        p.write_text(txt, encoding="utf-8")
        self._log(f"USER.md updated: {field} = {value}")

    def on_message(self, session_id: str, role: str, content: str):
        """باید بعد از هر پیام صدا زده شود — سایلنت"""
        # 1. ذخیره در SessionDB
        self.mm.sync_turn(session_id, role, content)
        
        if role != "user":
            return

        self.counter += 1
        important, tag = is_important(content)
        should_update = important or (self.counter % 3 == 0)

        if not should_update:
            return

        # 2. بروزرسانی مخفی USER.md / MEMORY.md
        try:
            self._extract_and_update_user(content)
            if important:
                # add durable fact
                self.mm.write_append("memory", "## حقایق", f"کاربر گفت ({tag}): {content[:80]}...")
                self._log(f"MEMORY.md appended due to important msg: {tag}")
            else:
                # periodic nudge — lightweight
                self._log(f"periodic nudge at count {self.counter}")
                # optional: auto-summarize session if long
                if self.counter % 6 == 0:
                    summary = self.mm.store.summarize_session(session_id)
                    self.mm.write_append("memory", "## تاریخچه تصمیمات", f"خلاصه سشن {session_id[:6]}: {summary[:100]}")
        except Exception as e:
            self._log(f"update error: {e}")

        # 3. اسکیل خودبهبود — اگر 5+ ترن و الگو تکراری دیده شد، اسکیل بساز/بهبود بده
        try:
            self._maybe_evolve_skill(session_id, content)
        except Exception as e:
            self._log(f"skill evolve error: {e}")

    def _maybe_evolve_skill(self, session_id: str, content: str):
        # Hermes-inspired: if user asks similar thing repeatedly, crystallize skill
        # simple heuristic: if mentions "برنامه" 3 times in recent turns → ensure planner skill tracked
        recent = self.mm.store.recent_turns(session_id, 10)
        planner_mentions = sum(1 for t in recent if "برنامه" in t["content"])
        if planner_mentions >= 3:
            # touch skill metadata to mark usage
            usage_path = pathlib.Path("skills/konkoor-planner/.usage")
            usage_path.parent.mkdir(parents=True, exist_ok=True)
            count = int(usage_path.read_text(encoding="utf-8").strip()) if usage_path.exists() else 0
            usage_path.write_text(str(count + 1), encoding="utf-8")
            self._log(f"skill usage incremented: konkoor-planner = {count+1}")

            # if usage hits threshold, auto-improve skill (append tip)
            if count + 1 in (5, 10, 20):
                skill_md = pathlib.Path("skills/konkoor-planner/SKILL.md")
                if skill_md.exists():
                    txt = skill_md.read_text(encoding="utf-8")
                    tip = f"\n> Auto-improved at usage {count+1}: کاربران با برنامه 6 ساعته تجربی بیشترین درخواست را دارند — این الگو ثبت شد."
                    if tip.strip() not in txt:
                        skill_md.write_text(txt + tip, encoding="utf-8")
                        self._log("skill auto-improved: konkoor-planner")

# singleton
_updater = None
def get_hidden_updater() -> HiddenUpdater:
    global _updater
    if _updater is None:
        _updater = HiddenUpdater()
    return _updater
