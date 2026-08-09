"""
VAHSHI Tools Registry — Hermes toolsets inspired
"""
TOOLS = {
    "read_file": {"desc": "خواندن فایل", "module": "vahshi.tools.file_tools"},
    "write_file": {"desc": "نوشتن فایل", "module": "vahshi.tools.file_tools"},
    "web_search": {"desc": "جستجوی وب", "module": "vahshi.tools.web_tools"},
    "web_extract": {"desc": "استخراج صفحه", "module": "vahshi.tools.web_tools"},
    "plan": {"desc": "برنامه هفتگی", "module": "vahshi.advisor.planner"},
    "evaluate": {"desc": "ارزیابی", "module": "vahshi.advisor.evaluator"},
    "memory": {"desc": "حافظه", "module": "vahshi.memory.manager"},
    "skill_search": {"desc": "جستجوی اسکیل", "module": "vahshi.skills.registry"},
    "image_analyze": {"desc": "تحلیل عکس", "module": "vahshi.tools.vision"},
}

TOOLSETS = {
    "hermes-cli": ["read_file", "write_file", "web_search", "plan", "evaluate"],
    "hermes-telegram": ["web_search", "plan", "evaluate", "memory"],
    "vahshi-full": list(TOOLS.keys()),
}

def get_toolset(name: str) -> list[str]:
    return TOOLSETS.get(name, TOOLSETS["vahshi-full"])
