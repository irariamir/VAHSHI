"""
VAHSHI Prompt Builder — Hermes 3-tier prompt (cache-stable → context → volatile)
"""
from vahshi.memory.manager import get_memory_manager
from vahshi.skills.registry import skills_prompt_block, discover_skills
from vahshi.persona import SYSTEM_PROMPT

def build_system_prompt(extra_context: str = "", include_skills: bool = True) -> str:
    mm = get_memory_manager()
    durable = mm.build_prompt_block()
    skills_block = skills_prompt_block() if include_skills else ""
    
    # Tier 1: stable (identity + tools + skills) — cacheable
    tier1 = f"""{SYSTEM_PROMPT}

{durable}

{skills_block}
"""
    # Tier 2: context (extra)
    tier2 = f"\n# Context\n{extra_context}" if extra_context else ""
    
    # Tier 3: volatile (timestamp)
    import datetime
    tier3 = f"\n# Volatile\nزمان فعلی: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} Asia/Tehran\nهشدار: اطلاعات کنکور را با sanjesh.org چک کن."
    
    return tier1 + tier2 + tier3

def build_messages(history: list[dict], extra_context: str = "") -> list[dict]:
    sys = build_system_prompt(extra_context)
    return [{"role": "system", "content": sys}] + history
