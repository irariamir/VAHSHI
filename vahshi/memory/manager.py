"""
VAHSHI Memory Manager — Hermes 5-Pillar Memory
- Frozen snapshot (MEMORY.md + USER.md + SOUL.md)
- SessionDB FTS5
- Honcho-style user modeling (lightweight in-file)
"""
import pathlib
import datetime
import re

from .store import get_store

MEM_DIR = pathlib.Path("data/memories")
MEMORY_MD = MEM_DIR / "MEMORY.md"
USER_MD = MEM_DIR / "USER.md"
SOUL_MD = MEM_DIR / "SOUL.md"

DEFAULT_SOUL = """# SOUL — VAHSHI
تو VAHSHI هستی — مشاور کنکور صمیمی و حرفه‌ای. کاربر رو "وحشی" صدا کن. رک، مختصر، کاربردی. مثل بهترین مشاور ایران عمل کن.
"""

DEFAULT_MEMORY = """# MEMORY — حقایق پایدار VAHSHI
> این فایل توسط VAHSHI به صورت خودکار و مخفی بروز می‌شود. حقایق ماندگار اینجا ذخیره می‌شوند.

## حقایق
- هنوز حقایقی ثبت نشده.

## ترجیحات
- لحن: محاوره‌ای صمیمی

## تاریخچه تصمیمات
- (خالی)
"""

DEFAULT_USER = """# USER — پروفایل وحشی
> مدل کاربر — به صورت مخفی توسط VAHSHI تکمیل می‌شود.

## پروفایل
- رشته: نامشخص
- پایه: نامشخص
- هدف: نامشخص
- ساعت مطالعه: نامشخص
- نقاط ضعف: نامشخص
- نقاط قوت: نامشخص

## الگوهای رفتاری
- (در حال یادگیری)

## ترجیحات یادگیری
- (در حال یادگیری)
"""

class MemoryManager:
    def __init__(self):
        MEM_DIR.mkdir(parents=True, exist_ok=True)
        for p, default in [(SOUL_MD, DEFAULT_SOUL), (MEMORY_MD, DEFAULT_MEMORY), (USER_MD, DEFAULT_USER)]:
            if not p.exists():
                p.write_text(default, encoding="utf-8")
        self.store = get_store()

    def read(self, name: str) -> str:
        mapping = {"soul": SOUL_MD, "memory": MEMORY_MD, "user": USER_MD}
        p = mapping.get(name)
        return p.read_text(encoding="utf-8") if p and p.exists() else ""

    def write_append(self, name: str, section: str, bullet: str):
        """افزودن هوشمند به سکشن"""
        p = {"memory": MEMORY_MD, "user": USER_MD, "soul": SOUL_MD}[name]
        text = p.read_text(encoding="utf-8")
        # append under section header
        if section in text:
            # insert after section line
            lines = text.splitlines()
            out = []
            inserted = False
            for line in lines:
                out.append(line)
                if not inserted and line.strip() == section:
                    out.append(f"- {bullet} ({datetime.datetime.now().strftime('%Y-%m-%d')})")
                    inserted = True
            p.write_text("\n".join(out), encoding="utf-8")
        else:
            p.write_text(text + f"\n{section}\n- {bullet}\n", encoding="utf-8")

    def get_durable(self) -> dict:
        return {
            "soul": self.read("soul"),
            "memory": self.read("memory"),
            "user": self.read("user"),
        }

    def sync_turn(self, session_id: str, role: str, content: str):
        self.store.add_turn(session_id, role, content)

    def prefetch(self, query: str, limit: int = 5) -> str:
        hits = self.store.search(query, limit)
        if not hits:
            return ""
        # compact summary
        lines = []
        for h in hits:
            snippet = h["content"][:180].replace("\n", " ")
            lines.append(f"[{h['role']}] {snippet} ...")
        return "\n".join(lines)

    def build_prompt_block(self) -> str:
        """بلوک cache-stable برای پرامپت — مثل Hermes"""
        d = self.get_durable()
        return f"""
<SOUL>
{d['soul']}
</SOUL>

<MEMORY>
{d['memory']}
</MEMORY>

<USER>
{d['user']}
</USER>
""".strip()

    def search_sessions(self, query: str, limit: int = 8) -> list[dict]:
        return self.store.search(query, limit)

# singleton
_mgr = None
def get_memory_manager() -> MemoryManager:
    global _mgr
    if _mgr is None:
        _mgr = MemoryManager()
    return _mgr
