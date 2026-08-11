"""
VAHSHI Telegram Bot
Requires: python-telegram-bot, OPENAI_API_KEY optional
Run: python -m bot.telegram_bot
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from vahshi.persona import SYSTEM_PROMPT
from vahshi.config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# OpenAI client
client = None
if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

SYSTEM = SYSTEM_PROMPT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام وحشی! 🔥 من VAHSHI هستم — مشاور کنکورت.\n\n"
        "بگو رشته‌ات چیه و تا کنکور چقدر وقت داری تا برات برنامه بچینم.\n"
        "دستورات:\n"
        "/plan — برنامه هفتگی\n"
        "/eval — ارزیابی\n"
        "/help — راهنما"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "وحشی راهنما:\n"
        "- هر سوالی درباره کنکور، برنامه، منابع، استرس داری بپرس\n"
        "- عکس سوال بفرست تا حل کنم\n"
        "- /plan برای برنامه هفتگی\n"
        "- اطلاعاتم رو با sanjesh.org چک کن"
    )

async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from vahshi.advisor.planner import build_weekly_plan, PlanRequest
    # simple default
    md = build_weekly_plan(PlanRequest(field="تجربی", daily_hours=6, weak_subjects=["زیست"]))
    # Telegram has 4096 char limit
    for chunk in [md[i:i+4000] for i in range(0, len(md), 4000)]:
        await update.message.reply_text(chunk)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    if client:
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role":"system","content":SYSTEM},{"role":"user","content":user_text}],
                temperature=0.7,
                max_tokens=1000,
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"وحشی خطا: {e}"
    else:
        reply = (
            f"وحشی پیامت رو گرفتم: {user_text}\n\n"
            "من الان بدون API Key هستم — برای جواب هوشمند OPENAI_API_KEY رو ست کن.\n"
            "ولی می‌تونی /plan بزنی تا برنامه بگیری."
        )
    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set in .env — bot cannot start")
        return
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("VAHSHI Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
