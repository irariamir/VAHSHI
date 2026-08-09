"""
VAHSHI Web App - FastAPI
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pathlib

from vahshi.persona import SYSTEM_PROMPT, get_evaluation_prompt
from vahshi.advisor.planner import build_weekly_plan, PlanRequest, quick_tips
from vahshi.advisor.evaluator import StudentProfile, evaluate_student
from vahshi.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

app = FastAPI(title="VAHSHI", version="0.1.0", description="مشاور کنکور حرفه‌ای")

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

# --- Models ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    field: str | None = None

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
    # quick keyword matching
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
    # default
    return f"""وحشی پیامت رو گرفتم: "{t}"

من الان در حالت **آفلاین (بدون API Key)** هستم. برای جواب هوشمند، باید `OPENAI_API_KEY` رو در `.env` بذاری.

ولی نگران نباش — می‌تونی از بخش‌های زیر استفاده کنی:
- 📅 **برنامه هفتگی** → تب برنامه
- 📊 **ارزیابی** → تب ارزیابی
- 💬 **چت هوشمند** → بعد از ست کردن API Key

یا همینجا بگو رشته و ساعت مطالعه‌ات چقدره تا با منطق داخلی راهنماییت کنم."""

async def call_llm(messages: list[dict]) -> str:
    if client is None:
        # fallback
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return fallback_chat(last_user, messages)

    # prepend system prompt if not present
    if not any(m["role"] == "system" for m in messages):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1200,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"وحشی خطا در ارتباط با مدل: {e}\n\n(حالت آفلاین فعال شد)\n\n" + fallback_chat(messages[-1]["content"] if messages else "", messages)

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def home():
    html_path = BASE_DIR / "static" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>VAHSHI</h1><p>static/index.html not found</p>")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "online" if client else "offline", "model": OPENAI_MODEL if client else None}

@app.get("/api/prompt")
async def get_prompt():
    return {"system_prompt": SYSTEM_PROMPT, "evaluation": get_evaluation_prompt()}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = await call_llm(msgs)
    return {"reply": reply}

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
    return {"analysis": analysis}

@app.get("/api/knowledge")
async def knowledge():
    from vahshi.knowledge.konkoor import KONKOOR_INFO, get_disclaimer
    return {"info": KONKOOR_INFO, "disclaimer": get_disclaimer()}

# Static
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
