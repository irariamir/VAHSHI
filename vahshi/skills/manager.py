"""
Skills Manager — CRUD + auto-create (Hermes self-creating)
"""
import pathlib
import datetime

SKILLS_DIR = pathlib.Path("skills")

TEMPLATE = """---
name: {name}
description: {description}
version: 1.0
created: {date}
auto_created: true
---

# {title}

> این اسکیل به صورت خودکار توسط VAHSHI ساخته شده و به مرور بهبود پیدا می‌کند (Hermes self-improving loop).

## هدف
{description}

## Workflow
{workflow}

## نکات
- این اسکیل در صورت استفاده مکرر به صورت مخفی بهبود پیدا می‌کند.
- برای ویرایش دستی، همین فایل را ویرایش کن.

## تاریخچه بهبود
- {date}: نسخه اولیه ساخته شد.
"""

def create_skill(name: str, description: str, workflow: str, title: str = "") -> pathlib.Path:
    slug = name.strip().lower().replace(" ", "-")
    path = SKILLS_DIR / slug
    path.mkdir(parents=True, exist_ok=True)
    md = path / "SKILL.md"
    if md.exists():
        return path
    md.write_text(TEMPLATE.format(
        name=slug,
        description=description,
        workflow=workflow,
        title=title or name,
        date=datetime.datetime.now().strftime("%Y-%m-%d")
    ), encoding="utf-8")
    # hidden log
    log = pathlib.Path("data/memories/_hidden_log.md")
    if log.exists():
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"- [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] skill created: {slug}\n")
    return path

def improve_skill(name: str, note: str):
    p = SKILLS_DIR / name / "SKILL.md"
    if not p.exists():
        return
    txt = p.read_text(encoding="utf-8")
    txt += f"\n- {datetime.datetime.now().strftime('%Y-%m-%d')}: {note}\n"
    p.write_text(txt, encoding="utf-8")

def list_skills() -> list[str]:
    if not SKILLS_DIR.exists():
        return []
    return [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d/"SKILL.md").exists()]
