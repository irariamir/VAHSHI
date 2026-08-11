# VAHSHI — Handoff for AI with SSH

**برای AI که با SSH key وصل شده:**

1. `git clone --branch arena/019fe630-vahshi git@github.com:irariamir/VAHSHI.git`
2. `cat docs/FOR_AI.md` — همه توضیحات
3. `cat data/memories/USER.md` — پروفایل وحشی
4. `cat vahshi/persona.py` — شخصیت

Quick start:
```bash
pip install -r requirements.txt
python -c "from vahshi.agent.prompt_builder import build_system_prompt; print(build_system_prompt()[:500])"
```

*Full snapshot: data/export/VAHSHI_snapshot.json*
