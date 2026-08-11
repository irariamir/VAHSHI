#!/usr/bin/env python3
"""Send approved text to PLANS or TRICKS. Never dumps secrets."""
import argparse, json, os, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# token from env or local workspace env (not committed)
candidates = [
    Path(os.environ.get('VAHSHI_BOT_ENV', '')),
    Path('/home/user/.vahshi/tools/telegram_study_bot/.env'),
    ROOT / 'telegram' / '.env',
]
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
if not token:
    for p in candidates:
        if p and p.exists():
            for line in p.read_text().splitlines():
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    token = line.split('=', 1)[1].strip()
                    break
        if token:
            break
if not token:
    raise SystemExit('no token')

chs = json.loads((ROOT / 'telegram' / 'channels.json').read_text(encoding='utf-8'))
MAP = {
    'plans': chs['groups']['plans']['id'],
    'tricks': chs['groups']['tricks']['id'],
    'sources': chs['groups']['sources']['id'],
}

def send(chat_id: int, text: str):
    # Telegram limit ~4096
    chunks = []
    while text:
        chunks.append(text[:4000])
        text = text[4000:]
    for ch in chunks:
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': ch,
            'disable_web_page_preview': 'true',
        }).encode()
        req = urllib.request.Request(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data=data, method='POST')
        with urllib.request.urlopen(req, timeout=30) as r:
            js = json.loads(r.read().decode())
            if not js.get('ok'):
                raise SystemExit(js)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target', choices=['plans', 'tricks', 'sources'])
    ap.add_argument('--file', help='utf-8 text file')
    ap.add_argument('--text', help='inline text')
    ap.add_argument('--yes', action='store_true', help='confirm send')
    args = ap.parse_args()
    if not args.yes:
        raise SystemExit('refusing: pass --yes after user approval')
    body = args.text or Path(args.file).read_text(encoding='utf-8')
    send(MAP[args.target], body.strip())
    print('sent', args.target, 'chars', len(body))

if __name__ == '__main__':
    main()
