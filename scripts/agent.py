#!/usr/bin/env python3
"""
VAHSHI Runtime — Hermes-inspired agent brain for the Arena workspace.

This is the local control plane the counselor persona uses across turns:
- boot context assembly (SOUL → USER → MEMORY → skills index → state)
- silent memory curation
- skill registry + scaffolding
- session logging + FTS-like search over past turns
- intake tracking for Konkur counseling
- optional cron job listing

It does NOT call an external LLM API. In Arena, the model is the reasoning
engine; this module is the persistent nervous system on disk.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
    TEHRAN = ZoneInfo("Asia/Tehran")
except Exception:  # pragma: no cover
    TEHRAN = timezone.utc

HOME = Path(__file__).resolve().parent
SOUL = HOME / "SOUL.md"
USER = HOME / "memories" / "USER.md"
MEMORY = HOME / "memories" / "MEMORY.md"
SKILLS = HOME / "skills"
INDEX = SKILLS / "INDEX.md"
STATE = HOME / "state" / "store.json"
SESSIONS = HOME / "sessions"
CRON = HOME / "cron" / "jobs.json"
LOGS = HOME / "logs"

USER_LIMIT = 1400
MEMORY_LIMIT = 2200


def now_tehran() -> datetime:
    return datetime.now(TEHRAN)


def ts() -> str:
    return now_tehran().isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ─── State ───────────────────────────────────────────────────────────────────

def load_state() -> dict:
    return load_json(STATE, {})


def save_state(state: dict) -> None:
    save_json(STATE, state)


def touch_boot(state: dict) -> dict:
    state["last_boot"] = ts()
    state["session_count"] = int(state.get("session_count") or 0) + 1
    save_state(state)
    return state


# ─── Memory ──────────────────────────────────────────────────────────────────

def char_count(path: Path) -> int:
    # rough: ignore markdown headings noise lightly
    return len(read_text(path))


def memory_status() -> dict:
    return {
        "user_chars": char_count(USER),
        "user_limit": USER_LIMIT,
        "memory_chars": char_count(MEMORY),
        "memory_limit": MEMORY_LIMIT,
        "user_over": char_count(USER) > USER_LIMIT,
        "memory_over": char_count(MEMORY) > MEMORY_LIMIT,
    }


def append_bullet(path: Path, section_heading: str, bullet: str) -> None:
    """Insert a bullet under a ## section; create section if missing."""
    text = read_text(path)
    line = f"- {bullet.strip()}"
    if line in text:
        return
    pattern = rf"(## {re.escape(section_heading)}\n)"
    if re.search(pattern, text):
        text = re.sub(pattern, rf"\1{line}\n", text, count=1)
    else:
        text = text.rstrip() + f"\n\n## {section_heading}\n{line}\n"
    write_text(path, text)


def replace_field_block(path: Path, key: str, value: str) -> None:
    """Replace '- key: ...' style lines in USER/MEMORY."""
    text = read_text(path)
    pat = rf"(- {re.escape(key)}:\s*).*"
    if re.search(pat, text):
        text = re.sub(pat, rf"\1{value}", text)
    else:
        text = text.rstrip() + f"\n- {key}: {value}\n"
    write_text(path, text)


def silent_memory_write(
    *,
    target: str,
    kind: str,
    content: str,
    section: str | None = None,
) -> dict:
    """
    target: 'user' | 'memory'
    kind: 'bullet' | 'field'
    """
    path = USER if target == "user" else MEMORY
    before = len(read_text(path))
    if kind == "field":
        # content format: "key=value"
        if "=" not in content:
            raise ValueError("field content must be key=value")
        key, value = content.split("=", 1)
        replace_field_block(path, key.strip(), value.strip())
    else:
        append_bullet(path, section or "یادداشت‌ها", content)
    after = len(read_text(path))
    state = load_state()
    stats = state.setdefault("stats", {})
    stats["memory_writes"] = int(stats.get("memory_writes") or 0) + 1
    save_state(state)
    return {
        "target": target,
        "path": str(path),
        "chars_before": before,
        "chars_after": after,
        "over_limit": after > (USER_LIMIT if target == "user" else MEMORY_LIMIT),
        "at": ts(),
    }


# ─── Skills ──────────────────────────────────────────────────────────────────

@dataclass
class SkillMeta:
    name: str
    path: Path
    description: str
    category: str


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def list_skills() -> list[SkillMeta]:
    out: list[SkillMeta] = []
    if not SKILLS.exists():
        return out
    for path in sorted(SKILLS.rglob("SKILL.md")):
        raw = read_text(path)
        meta = parse_frontmatter(raw)
        cat = path.parent.parent.name if path.parent.parent != SKILLS else path.parent.name
        # skills/<cat>/<name>/SKILL.md
        parts = path.relative_to(SKILLS).parts
        category = parts[0] if len(parts) > 1 else "misc"
        name = meta.get("name") or (parts[1] if len(parts) > 2 else path.parent.name)
        desc = meta.get("description") or ""
        out.append(SkillMeta(name=name, path=path, description=desc, category=category))
    return out


def load_skill(name: str) -> str:
    for s in list_skills():
        if s.name == name or s.path.parent.name == name:
            return read_text(s.path)
    raise FileNotFoundError(f"skill not found: {name}")


def create_skill(
    name: str,
    description: str,
    category: str,
    body: str,
    tags: list[str] | None = None,
) -> Path:
    safe = re.sub(r"[^a-z0-9\-]+", "-", name.lower()).strip("-")
    folder = SKILLS / category / safe
    folder.mkdir(parents=True, exist_ok=True)
    tag_line = ", ".join(tags or [category])
    content = (
        f"---\n"
        f"name: {safe}\n"
        f"description: {description}\n"
        f"version: 1.0.0\n"
        f"category: {category}\n"
        f"tags: [{tag_line}]\n"
        f"---\n\n"
        f"{body.rstrip()}\n"
    )
    path = folder / "SKILL.md"
    write_text(path, content)
    state = load_state()
    stats = state.setdefault("stats", {})
    stats["skills_created"] = int(stats.get("skills_created") or 0) + 1
    save_state(state)
    _rebuild_index_hint(safe, description, category)
    return path


def improve_skill(name: str, note: str) -> Path:
    text = load_skill(name)
    # find path again
    path = None
    for s in list_skills():
        if s.name == name or s.path.parent.name == name:
            path = s.path
            break
    assert path is not None
    section = "\n## Lessons Learned (auto)\n"
    bullet = f"- ({ts()[:10]}) {note.strip()}\n"
    if "## Lessons Learned (auto)" in text:
        text = text.rstrip() + "\n" + bullet
    else:
        text = text.rstrip() + "\n" + section + bullet
    # bump patch version if present
    def bump(m: re.Match) -> str:
        parts = m.group(1).split(".")
        if len(parts) == 3 and parts[2].isdigit():
            parts[2] = str(int(parts[2]) + 1)
            return f"version: {'.'.join(parts)}"
        return m.group(0)

    text = re.sub(r"version:\s*([0-9.]+)", bump, text, count=1)
    write_text(path, text)
    state = load_state()
    stats = state.setdefault("stats", {})
    stats["skills_improved"] = int(stats.get("skills_improved") or 0) + 1
    save_state(state)
    return path


def _rebuild_index_hint(name: str, description: str, category: str) -> None:
    idx = read_text(INDEX)
    marker = f"| {name} |"
    if marker in idx:
        return
    line = f"| {name} | {description} |\n"
    heading = f"## {category}\n"
    if heading in idx:
        # append after first table header block roughly at end of file section
        idx = idx.rstrip() + "\n" + line
    else:
        idx = idx.rstrip() + f"\n\n## {category}\n| skill | when to load |\n|-------|----------------|\n" + line
    write_text(INDEX, idx)


# ─── Sessions ────────────────────────────────────────────────────────────────

def session_path(day: str | None = None) -> Path:
    day = day or now_tehran().strftime("%Y-%m-%d")
    return SESSIONS / f"{day}.jsonl"


def log_turn(role: str, content: str, meta: dict | None = None) -> dict:
    rec = {
        "ts": ts(),
        "role": role,
        "content": content,
        "meta": meta or {},
    }
    path = session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    # latest pointer
    write_text(SESSIONS / "latest.json", json.dumps(rec, ensure_ascii=False, indent=2))
    state = load_state()
    if role == "user":
        state["meaningful_turns"] = int(state.get("meaningful_turns") or 0) + 1
        save_state(state)
    return rec


def iter_sessions() -> list[dict]:
    rows: list[dict] = []
    if not SESSIONS.exists():
        return rows
    for path in sorted(SESSIONS.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def search_sessions(query: str, limit: int = 20) -> list[dict]:
    q = query.lower().strip()
    hits = []
    for row in reversed(iter_sessions()):
        blob = (row.get("content") or "") + json.dumps(row.get("meta") or {}, ensure_ascii=False)
        if q in blob.lower():
            hits.append(row)
            if len(hits) >= limit:
                break
    return hits


# ─── Intake ──────────────────────────────────────────────────────────────────

INTAKE_KEYS = [
    "stream",
    "grade",
    "goal",
    "daily_hours",
    "strengths",
    "weaknesses",
    "time_to_konkur",
    "school_or_free",
]


def update_intake(**fields: Any) -> dict:
    state = load_state()
    intake = state.setdefault("intake", {"complete": False, "fields": {}})
    f = intake.setdefault("fields", {})
    for k, v in fields.items():
        if k in INTAKE_KEYS and v is not None:
            f[k] = v
            # mirror into USER.md quietly
            label = {
                "stream": "رشته",
                "grade": "پایه/وضعیت",
                "goal": "هدف (رشته/دانشگاه/رتبه)",
                "daily_hours": "ساعت مطالعه روزانه فعلی",
                "strengths": "نقاط قوت",
                "weaknesses": "نقاط ضعف",
                "time_to_konkur": "زمان تا کنکور",
                "school_or_free": "مدرسه/کلاس حضوری",
            }[k]
            replace_field_block(USER, label, str(v))
    intake["complete"] = all(f.get(k) not in (None, "", "؟") for k in INTAKE_KEYS)
    state["flags"] = state.get("flags") or {}
    state["flags"]["awaiting_intake"] = not intake["complete"]
    save_state(state)
    return intake


# ─── Boot context ────────────────────────────────────────────────────────────

def build_boot_context(max_skill_list: int = 50) -> str:
    state = touch_boot(load_state())
    skills = list_skills()
    skill_lines = "\n".join(
        f"- [{s.category}] {s.name}: {s.description}" for s in skills[:max_skill_list]
    )
    mem_stat = memory_status()
    intake = (state.get("intake") or {}).get("fields") or {}
    parts = [
        "# VAHSHI BOOT CONTEXT",
        f"booted_at: {state.get('last_boot')}",
        f"session_count: {state.get('session_count')}",
        f"meaningful_turns: {state.get('meaningful_turns')}",
        f"intake_complete: {(state.get('intake') or {}).get('complete')}",
        f"memory_status: user {mem_stat['user_chars']}/{mem_stat['user_limit']} | "
        f"memory {mem_stat['memory_chars']}/{mem_stat['memory_limit']}",
        "",
        "## SOUL.md",
        read_text(SOUL),
        "",
        "## USER.md",
        read_text(USER),
        "",
        "## MEMORY.md",
        read_text(MEMORY),
        "",
        "## Skills registry",
        skill_lines or "(none)",
        "",
        "## Intake snapshot",
        json.dumps(intake, ensure_ascii=False, indent=2),
        "",
        "## Protocol",
        "- Keep counselor persona from SOUL.",
        "- Silent memory updates on triggers only.",
        "- Load SKILL.md on demand via `python agent.py skill <name>`.",
        "- Log important turns via `python agent.py log ...`.",
    ]
    ctx = "\n".join(parts)
    write_text(LOGS / "last_boot_context.md", ctx)
    return ctx


# ─── Cron ────────────────────────────────────────────────────────────────────

def list_cron() -> list[dict]:
    return load_json(CRON, [])


def add_cron(name: str, every: str, action: str) -> list[dict]:
    jobs = list_cron()
    jobs.append({"name": name, "every": every, "action": action, "created": ts()})
    save_json(CRON, jobs)
    return jobs


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VAHSHI Hermes-like control plane")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("boot", help="Assemble and print boot context")
    sub.add_parser("status", help="Print compact status JSON")
    sub.add_parser("skills", help="List skills")

    p_skill = sub.add_parser("skill", help="Print a skill body")
    p_skill.add_argument("name")

    p_new = sub.add_parser("new-skill", help="Create skill from args")
    p_new.add_argument("name")
    p_new.add_argument("category")
    p_new.add_argument("description")
    p_new.add_argument("--body", default="# Steps\n\n1. TODO\n")

    p_imp = sub.add_parser("improve-skill", help="Append lesson to skill")
    p_imp.add_argument("name")
    p_imp.add_argument("note")

    p_mem = sub.add_parser("mem", help="Silent memory write")
    p_mem.add_argument("target", choices=["user", "memory"])
    p_mem.add_argument("kind", choices=["bullet", "field"])
    p_mem.add_argument("content")
    p_mem.add_argument("--section", default="یادداشت‌ها")

    p_log = sub.add_parser("log", help="Append session turn")
    p_log.add_argument("role", choices=["user", "assistant", "system"])
    p_log.add_argument("content")

    p_search = sub.add_parser("search", help="Search past sessions")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=20)

    p_in = sub.add_parser("intake", help="Update intake fields key=value ...")
    p_in.add_argument("pairs", nargs="*")

    p_cron = sub.add_parser("cron-add")
    p_cron.add_argument("name")
    p_cron.add_argument("every")
    p_cron.add_argument("action")
    sub.add_parser("cron-list")

    args = parser.parse_args(argv)

    if args.cmd == "boot":
        print(build_boot_context())
        return 0
    if args.cmd == "status":
        st = load_state()
        st["memory"] = memory_status()
        st["skills_count"] = len(list_skills())
        print(json.dumps(st, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "skills":
        for s in list_skills():
            print(f"{s.category:12} {s.name:28} {s.description}")
        return 0
    if args.cmd == "skill":
        print(load_skill(args.name))
        return 0
    if args.cmd == "new-skill":
        path = create_skill(args.name, args.description, args.category, args.body)
        print(path)
        return 0
    if args.cmd == "improve-skill":
        path = improve_skill(args.name, args.note)
        print(path)
        return 0
    if args.cmd == "mem":
        result = silent_memory_write(
            target=args.target, kind=args.kind, content=args.content, section=args.section
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "log":
        print(json.dumps(log_turn(args.role, args.content), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "search":
        print(json.dumps(search_sessions(args.query, args.limit), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "intake":
        fields = {}
        for pair in args.pairs:
            if "=" in pair:
                k, v = pair.split("=", 1)
                fields[k] = v
        print(json.dumps(update_intake(**fields), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "cron-add":
        print(json.dumps(add_cron(args.name, args.every, args.action), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "cron-list":
        print(json.dumps(list_cron(), ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
