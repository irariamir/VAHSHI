"""
VAHSHI Cron Scheduler — Hermes cron inspired
زمان‌بندی با زبان طبیعی، تحویل به هر پلتفرم
"""
import pathlib
import json
import datetime
import threading
import time

CRON_DIR = pathlib.Path("data/crons")
CRON_FILE = CRON_DIR / "jobs.json"

DEFAULT_JOBS = [
    {
        "id": "night_review",
        "schedule": "daily 22:00",
        "prompt": "وحشی گزارش روزانه رو جمع‌بندی کن: امروز چقدر خوندی؟ چی موند؟ فردا چی بخونی؟",
        "delivery": "memory",
        "enabled": True
    },
    {
        "id": "weekly_plan",
        "schedule": "weekly friday 18:00",
        "prompt": "برنامه هفته بعد وحشی رو بر اساس پیشرفت این هفته بساز",
        "delivery": "memory",
        "enabled": True
    },
    {
        "id": "memory_compress",
        "schedule": "daily 02:00",
        "prompt": "_internal: فشرده‌سازی حافظه و بهبود اسکیل‌ها",
        "delivery": "internal",
        "enabled": True
    }
]

class CronScheduler:
    def __init__(self):
        CRON_DIR.mkdir(parents=True, exist_ok=True)
        if not CRON_FILE.exists():
            CRON_FILE.write_text(json.dumps(DEFAULT_JOBS, ensure_ascii=False, indent=2), encoding="utf-8")
        self.jobs = json.loads(CRON_FILE.read_text(encoding="utf-8"))
        self._thread = None

    def list_jobs(self):
        return self.jobs

    def add_job(self, job: dict):
        self.jobs.append(job)
        self._save()

    def _save(self):
        CRON_FILE.write_text(json.dumps(self.jobs, ensure_ascii=False, indent=2), encoding="utf-8")

    def run_pending(self):
        # simple loop — در نسخه واقعی با croniter دقیق‌تر میشه
        now = datetime.datetime.now().strftime("%H:%M")
        for job in self.jobs:
            if not job.get("enabled"):
                continue
            if now in job.get("schedule", ""):
                # hidden execution
                log = pathlib.Path("data/memories/_hidden_log.md")
                with open(log, "a", encoding="utf-8") as f:
                    f.write(f"- [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] cron fired: {job['id']} → {job['prompt'][:60]}\n")

    def start_background(self):
        def loop():
            while True:
                try:
                    self.run_pending()
                except: pass
                time.sleep(60)
        if self._thread is None:
            self._thread = threading.Thread(target=loop, daemon=True)
            self._thread.start()

# singleton
sched = None
def get_scheduler():
    global sched
    if sched is None:
        sched = CronScheduler()
        sched.start_background()
    return sched
