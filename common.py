import os, csv, requests
from datetime import datetime, timezone


def t12(dt, seconds=False):
    """وقت بنظام 12 ساعة: 5:38 م  أو  5:38:07 م"""
    h = dt.hour % 12 or 12
    suffix = "ص" if dt.hour < 12 else "م"
    sec = f":{dt.second:02d}" if seconds else ""
    return f"{h}:{dt.minute:02d}{sec} {suffix}"


def send(text):
    for i in range(0, len(text), 3800):
        try:
            requests.post(
                f"https://api.telegram.org/bot{os.environ['TG_TOKEN']}/sendMessage",
                data={"chat_id": os.environ["TG_CHAT"],
                      "text": text[i:i + 3800],
                      "disable_web_page_preview": True},
                timeout=15,
            )
        except Exception as e:
            print("telegram", e)


def _fmt(ts):
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def recently_logged(file, sym, close_ts, minutes=30):
    if not os.path.exists(file):
        return False
    now = close_ts.astimezone(timezone.utc).replace(tzinfo=None)
    with open(file, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[1] == sym:
                try:
                    t = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if abs((now - t).total_seconds()) < minutes * 60:
                    return True
    return False


def log_signal(file, sym, name, price, close_ts):
    os.makedirs("data", exist_ok=True)
    new = not os.path.exists(file)
    with open(file, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts_utc", "symbol", "name", "price"])
        w.writerow([_fmt(close_ts), sym, name, round(float(price), 4)])
