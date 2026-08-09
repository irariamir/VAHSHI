"""
VAHSHI Agent Loop — Hermes AIAgent inspired (synchronous orchestration)
prompt → think → tool → obs → memory → continue
"""
import uuid
from vahshi.memory.hidden_updater import get_hidden_updater
from vahshi.memory.manager import get_memory_manager
from .prompt_builder import build_messages

class VahshiAgent:
    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.mm = get_memory_manager()
        self.updater = get_hidden_updater()

    def step(self, user_text: str, history: list[dict]) -> tuple[list[dict], str]:
        """
        یک ترن کامل:
        - ذخیره مخفی
        - ساخت پرامپت با حافظه + اسکیل‌ها
        - بازگشت پیام‌های جدید برای LLM
        """
        # hidden update (silent)
        self.updater.on_message(self.session_id, "user", user_text)
        
        # build prompt-aware history
        # history already contains user_text as last
        # we inject memory prefetch if query is search-like
        extra = ""
        if any(k in user_text for k in ["یادته", "قبلا", "گفتی", "برنامه قبلی"]):
            prefetch = self.mm.prefetch(user_text, 3)
            if prefetch:
                extra = f"یادآوری از سشن‌های قبلی:\n{prefetch}"

        messages = build_messages(history, extra_context=extra)
        return messages, extra

    def on_assistant(self, content: str):
        self.updater.on_message(self.session_id, "assistant", content)
        # also store via hidden updater's mm sync
        self.mm.sync_turn(self.session_id, "assistant", content)
