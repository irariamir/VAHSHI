"""
VAHSHI Skills Registry — Hermes skills inspired (agentskills.io)
هر Skill = پوشه با SKILL.md + metadata
"""
import pathlib
import yaml
import re

SKILLS_DIR = pathlib.Path("skills")
DATA_SKILLS = pathlib.Path("data/skills")

class Skill:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.md_path = path / "SKILL.md"
        self.name = path.name
        self.description = ""
        self.content = ""
        self.meta = {}
        if self.md_path.exists():
            raw = self.md_path.read_text(encoding="utf-8")
            # parse frontmatter
            if raw.startswith("---"):
                parts = raw.split("---", 2)
                if len(parts) >= 3:
                    try:
                        self.meta = yaml.safe_load(parts[1]) or {}
                    except:
                        self.meta = {}
                    self.content = parts[2].strip()
                    self.name = self.meta.get("name", self.name)
                    self.description = self.meta.get("description", "")
                else:
                    self.content = raw
            else:
                self.content = raw
                # try to extract description from first lines
                m = re.search(r"#\s*(.*)", raw)
                if m:
                    self.description = m.group(1).strip()

    def to_prompt_block(self) -> str:
        return f"<skill name=\"{self.name}\">\n{self.content[:2500]}\n</skill>"

def discover_skills() -> list[Skill]:
    skills = []
    for base in [SKILLS_DIR, DATA_SKILLS]:
        if not base.exists():
            continue
        for p in base.iterdir():
            if p.is_dir() and (p / "SKILL.md").exists():
                skills.append(Skill(p))
    return skills

def get_skill(name: str) -> Skill | None:
    for s in discover_skills():
        if s.name == name or s.path.name == name:
            return s
    return None

def list_skill_names() -> list[str]:
    return [s.name for s in discover_skills()]

def skills_prompt_block(limit: int = 6) -> str:
    """بلوک خلاصه اسکیل‌ها برای تزریق به پرامپت — cache-friendly"""
    skills = discover_skills()
    if not skills:
        return ""
    blocks = []
    for s in skills[:limit]:
        # short version
        short = s.description or s.content[:120].replace("\n", " ")
        blocks.append(f"- **{s.name}**: {short}")
    return "## Skills available\n" + "\n".join(blocks)
