"""
VAHSHI Web App - FastAPI + Hermes Engine
- Agent Loop + Hidden Updater + Memory + Skills + Crons
"""
import os
import sys
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pathlib

from vahshi.persona import SYSTEM_PROMPT, get_evaluation_prompt
from vahshi.advisor.planner import build_weekly_plan, PlanRequest, quick_tips
from vahshi.advisor.evaluator import StudentProfile, evaluate_student
from vahshi.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# Hermes engine
from vahshi.agent.loop import VahshiAgent
from vahshi.agent.prompt_builder import build_system_prompt
from vahshi.memory.manager import get_memory_manager
from vahshi.memory.hidden_updater import get_hidden_updater
from vahshi.skills.registry import discover_skills, list_skill_names
from vahshi.crons.scheduler import get_scheduler
from vahshi.context.compressor import compress

app = FastAPI(title="VAHSHI", version="0.2.0", description="مشاور کنکور حرفه‌ای — Hermes Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client (optional)
client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    except Exception as e:
        print(f"[VAHSHI] OpenAI init failed: {e}")

BASE_DIR = pathlib.Path(__file__).parent

# init Hermes subsystems (silent)
mm = get_memory_manager()
updater = get_hidden_updater()
scheduler = get_scheduler()  # starts background thread
print(f"[VAHSHI] Hermes Engine — memory: {mm.read('soul')[:30]}... | skills: {len(discover_skills())} | cron: {len(scheduler.list_jobs())} jobs")

# --- Models ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    session_id: str | None = None

class PlanBody(BaseModel):
    field: str = "تجربی"
    daily_hours: float = 6
    weak_subjects: list[str] = []
    strong_subjects: list[str] = []
    grade: str = "دوازدهم"

class EvaluateBody(BaseModel):
    field: str = "تجربی"
    grade: str = "دوازدهم"
    months_to_konkoor: int = 10
    daily_hours: float = 4
    strong_subjects: list[str] = []
    weak_subjects: list[str] = []
    target: str = ""
    azmoon_taraz: int | None = None

# --- Helpers ---
FALLBACK_RESPONSES = {
    "سلام": "سلام وحشی! 😎 من VAHSHI هستم — مشاور کنکورت. بگو ببینم رشته‌ات چیه و تا کنکور چقدر وقت داری؟",
    "برنامه": "وحشی برای برنامه دقیق باید اول ارزیابی‌ات کنم. رشته، پایه، ساعات مطالعه و هدفت رو بگو تا همین الان برنامه هفتگی‌ات رو بسازم.",
}

def fallback_chat(user_text: str, history: list[dict]) -> str:
    t = user_text.strip()
    if any(k in t for k in ["سلام", "درود", "hi", "hello"]):
        return FALLBACK_RESPONSES["سلام"] + "\n\n" + get_evaluation_prompt()
    if "برنامه" in t:
        return FALLBACK_RESPONSES["برنامه"] + "\n\n" + get_evaluation_prompt()
    if any(k in t for k in ["استرس", "اضطراب", "خسته", "ناامید"]):
        return """وحشی کاملا درکت می‌کنم ❤️ استرس کنکور طبیعیه.

**3 کار فوری:**
1. تنفس 4-7-8 رو همین الان 3 بار انجام بده
2. امروز فقط 2 تا پومودورو (50 دقیقه) بخون — همین کافیه، کمال‌گرا نباش
3. شب 7 ساعت بخواب، فردا مغزت 30% بهتر کار می‌کنه

اگه بیشتر توضیح بدی دقیقا چی اذیتت می‌کنه، راهکار دقیق‌تر می‌دم."""
    return f"""وحشی پیامت رو گرفتم: "{t}"

من الان در حالت **آفلاین (بدون API Key)** هستم. برای جواب هوشمند، باید `OPENAI_API_KEY` رو در `.env` بذاری.

ولی نگران نباش — می‌تونی از بخش‌های زیر استفاده کنی:
- 📅 **برنامه هفتگی** → تب برنامه
- 📊 **ارزیابی** → تب ارزیابی
- 💬 **چت هوشمند** → بعد از ست کردن API Key

یا همینجا بگو رشته و ساعت مطالعه‌ات چقدره تا با منطق داخلی راهنماییت کنم."""

# single agent instance per session
_agents: dict[str, VahshiAgent] = {}
def get_agent(sid: str) -> VahshiAgent:
    if sid not in _agents:
        _agents[sid] = VahshiAgent(session_id=sid)
    return _agents[sid]

async def call_llm(messages: list[dict], session_id: str = "default") -> str:
    # Hermes loop: hidden updater + prompt builder + compressor
    agent = get_agent(session_id)
    # messages includes history; last is user
    # trigger hidden updater via agent step
    history = messages  # already includes system? we handle
    # strip old system for rebuilding
    user_history = [m for m in history if m["role"] != "system"]
    if not user_history:
        return fallback_chat("", history)
    last_user = user_history[-1]["content"] if user_history[-1]["role"] == "user" else ""
    
    # let agent do hidden update + provide extra context
    # we need to give full user_history to agent.step
    built_messages, extra = agent.step(last_user, user_history)

    # if offline → fallback but still with memory-enhanced prompt
    if client is None:
        reply = fallback_chat(last_user, history)
        agent.on_assistant(reply)
        return reply

    # compress if long
    built_messages = compress(built_messages, max_tokens=12000)

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=built_messages,
            temperature=0.7,
            max_tokens=1400,
        )
        reply = resp.choices[0].message.content
        agent.on_assistant(reply)
        return reply
    except Exception as e:
        return f"وحشی خطا در ارتباط با مدل: {e}\n\n(حالت آفلاین فعال شد)\n\n" + fallback_chat(last_user, history)

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = BASE_DIR / "static" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>VAHSHI</h1><p>static/index.html not found</p>")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "mode": "online" if client else "offline",
        "model": OPENAI_MODEL if client else None,
        "hermes": {
            "memory": True,
            "skills": len(discover_skills()),
            "skill_names": list_skill_names(),
            "cron_jobs": len(scheduler.list_jobs()),
            "hidden_updater": True,
        }
    }

@app.get("/api/prompt")
async def get_prompt():
    return {"system_prompt": build_system_prompt(), "evaluation": get_evaluation_prompt()}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    sid = req.session_id or "default"
    reply = await call_llm(msgs, session_id=sid)
    return {"reply": reply, "session_id": sid}

@app.post("/api/plan")
async def plan(body: PlanBody):
    req = PlanRequest(
        field=body.field,
        daily_hours=body.daily_hours,
        weak_subjects=body.weak_subjects,
        strong_subjects=body.strong_subjects,
        grade=body.grade,
    )
    md = build_weekly_plan(req)
    tip = quick_tips(body.field)
    # hidden: log plan request
    mm.sync_turn("plan", "user", f"plan request: {body.field} {body.daily_hours}h weak={body.weak_subjects}")
    updater.on_message("plan", "user", f"برنامه {body.field} {body.daily_hours} ساعت")
    return {"plan": md, "tip": tip}

@app.post("/api/evaluate")
async def evaluate(body: EvaluateBody):
    profile = StudentProfile(
        field=body.field,
        grade=body.grade,
        months_to_konkoor=body.months_to_konkoor,
        daily_hours=body.daily_hours,
        strong_subjects=body.strong_subjects,
        weak_subjects=body.weak_subjects,
        target=body.target,
        azmoon_taraz=body.azmoon_taraz,
    )
    analysis = evaluate_student(profile)
    # hidden updater — این پیام مهمه، سایلنت ذخیره میشه
    updater.on_message("eval", "user", f"ارزیابی: {body.field} {body.grade} {body.daily_hours}h هدف {body.target} ضعف {body.weak_subjects}")
    return {"analysis": analysis}

@app.get("/api/knowledge")
async def knowledge():
    from vahshi.knowledge.konkoor import KONKOOR_INFO, get_disclaimer
    return {"info": KONKOOR_INFO, "disclaimer": get_disclaimer()}

@app.get("/api/memory")
async def memory_api():
    """Hermes memory inspector — برای دیباگ (در پروداکشن می‌تونی ببندی)"""
    d = mm.get_durable()
    # hidden log tail
    import pathlib
    log = pathlib.Path("data/memories/_hidden_log.md")
    log_tail = log.read_text(encoding="utf-8").splitlines()[-20:] if log.exists() else []
    return {"memory": d["memory"][:3000], "user": d["user"][:3000], "soul": d["soul"][:2000], "hidden_log": log_tail}

@app.get("/api/skills")
async def skills_api():
    from vahshi.skills.registry import discover_skills
    skills = discover_skills()
    return {"skills": [{"name": s.name, "description": s.description, "path": str(s.path)} for s in skills]}

@app.get("/api/crons")
async def crons_api():
    return {"jobs": scheduler.list_jobs()}

@app.post("/api/hidden/nudge")
async def hidden_nudge():
    """دستی تریگر hidden updater — برای تست"""
    updater.counter += 2  # force next = important
    return {"status": "nudged", "counter": updater.counter}

# Static
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
