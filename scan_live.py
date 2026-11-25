import os, time, threading
from collections import deque
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import yfinance as yf
from yfinance import EquityQuery
from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from common import send, log_signal, t12

LOG = "data/signals_live.csv"

# ===== الفلتر =====
MIN_PRICE, MAX_PRICE = 1, 10
MAX_CAP = 500_000_000
MIN_CHG = 2
MIN_DAYVOL = 200_000
MAX_SYMS = 29          # حد Alpaca المجاني 30 (واحد محجوز)
REFRESH_SEC = 60       # تحديث القائمة كل دقيقة

# ===== الإشارة =====
VOL_LEN, VOL_MULT = 30, 5.0
QUIET_LEN, QUIET_MAX = 20, 3.0
MOVE = 3.0
MIN_BAR_VOL = 2000     # أقل حجم (IEX) للشمعة
COOLDOWN = 600         # ثواني بين تنبيهين لنفس السهم

KEY, SECRET = os.environ["ALPACA_KEY"], os.environ["ALPACA_SECRET"]
DUMMY = "SPY"

rest = StockHistoricalDataClient(KEY, SECRET)
stream = StockDataStream(KEY, SECRET, feed=DataFeed.IEX)

hist, cur, info, last_alert = {}, {}, {}, {}
subscribed = {DUMMY}


def get_universe():
    q = EquityQuery("and", [
        EquityQuery("eq", ["region", "us"]),
        EquityQuery("is-in", ["exchange", "NMS", "NYQ", "ASE", "NCM", "NGM"]),
        EquityQuery("btwn", ["intradayprice", MIN_PRICE, MAX_PRICE]),
        EquityQuery("lt", ["intradaymarketcap", MAX_CAP]),
        EquityQuery("gt", ["percentchange", MIN_CHG]),
        EquityQuery("gt", ["dayvolume", MIN_DAYVOL]),
    ])
    r = yf.screen(q, size=60, sortField="percentchange", sortAsc=False)
    out = {}
    for x in r.get("quotes", []):
        s = x["symbol"]
        if "." in s or "-" in s or (len(s) == 5 and s[-1] in "WRU"):
            continue
        out[s] = (x.get("shortName") or x.get("longName") or s,
                  x.get("marketCap"), x.get("regularMarketChangePercent"))
        if len(out) >= MAX_SYMS:
            break
    return out


def load_hist(sym):
    try:
        now = datetime.now(timezone.utc)
        r = rest.get_stock_bars(StockBarsRequest(
            symbol_or_symbols=sym, timeframe=TimeFrame.Minute,
            start=now - timedelta(hours=4), end=now, feed=DataFeed.IEX))
        bars = r.data.get(sym, [])
        hist[sym] = deque(
            ({"o": b.open, "h": b.high, "l": b.low, "c": b.close, "v": b.volume}
             for b in bars), maxlen=120)
    except Exception as e:
        print("hist", sym, e)
        hist[sym] = deque(maxlen=120)


def build(sym, c, ts, quiet, hh, avgv, move):
    name, cap, chg = info.get(sym, (sym, None, None))
    t = ts.astimezone(ZoneInfo("Asia/Riyadh"))
    cap_txt = f"{cap/1e6:,.0f} مليون $" if cap else "-"
    chg_txt = f"{chg:+.1f}%" if chg is not None else "-"
    return (
        f"⚡ تنبيه لحظي: سيولة مفاجئة بعد خمول 🇺🇸\n"
        f"━━━━━━━━━━━━━━\n"
        f"📛 السهم: {name}\n"
        f"🔖 الرمز: {sym}\n"
        f"🔥 الحدث: انفجار حجم + اختراق بعد فترة خمول (لحظي)\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 السعر: {c['c']:.2f}$\n"
        f"📈 حركة الشمعة الحالية: {move:+.1f}%\n"
        f"📊 حجم الشمعة (IEX): {c['v']:,.0f} سهم ({c['v']/avgv:.1f}x المتوسط)\n"
        f"📏 نطاق الخمول السابق: {quiet:.1f}%\n"
        f"🔓 اخترق أعلى سعر قبلها: {hh:.2f}$\n"
        f"📅 التغير اليوم: {chg_txt}\n"
        f"🏢 القيمة السوقية: {cap_txt}\n"
        f"━━━━━━━━━━━━━━\n"
        f"📆 التاريخ: {t:%Y-%m-%d}\n"
        f"🕐 الوقت: {t12(t, seconds=True)} (السعودية)\n"
        f"🔗 https://www.tradingview.com/chart/?symbol={sym}"
    )


def check(sym, c, ts):
    h = hist[sym]
    if len(h) < max(VOL_LEN, QUIET_LEN) or c["v"] < MIN_BAR_VOL:
        return
    if time.time() - last_alert.get(sym, 0) < COOLDOWN:
        return
    last = list(h)
    q = last[-QUIET_LEN:]
    hh = max(x["h"] for x in q)
    ll = min(x["l"] for x in q)
    if ll <= 0:
        return
    quiet = (hh - ll) / ll * 100
    if quiet > QUIET_MAX:
        return
    avgv = sum(x["v"] for x in last[-VOL_LEN:]) / VOL_LEN
    if avgv <= 0 or c["v"] < avgv * VOL_MULT:
        return
    move = (c["c"] - c["o"]) / c["o"] * 100
    if move < MOVE or c["c"] <= hh:
        return
    last_alert[sym] = time.time()
    send(build(sym, c, ts, quiet, hh, avgv, move))
    close_ts = ts.replace(second=0, microsecond=0) + timedelta(minutes=1)
    log_signal(LOG, sym, info.get(sym, (sym,))[0], c["c"], close_ts)


async def on_trade(t):
    sym = t.symbol
    if sym not in hist:
        return
    ts = t.timestamp
    m = ts.replace(second=0, microsecond=0)
    c = cur.get(sym)
    if c is None or c["m"] != m:
        if c is not None:
            hist[sym].append({k: c[k] for k in ("o", "h", "l", "c", "v")})
        c = cur[sym] = {"m": m, "o": t.price, "h": t.price,
                        "l": t.price, "c": t.price, "v": 0}
    c["h"] = max(c["h"], t.price)
    c["l"] = min(c["l"], t.price)
    c["c"] = t.price
    c["v"] += t.size
    check(sym, c, ts)


def refresher():
    while True:
        time.sleep(REFRESH_SEC)
        try:
            u = get_universe()
            info.update(u)
            new = set(u)
            rem = subscribed - new - {DUMMY}
            add = new - subscribed
            if rem:
                stream.unsubscribe_trades(*rem)
            for s in add:
                load_hist(s)
            if add:
                stream.subscribe_trades(on_trade, *add)
            subscribed.difference_update(rem)
            subscribed.update(add)
            for s in rem:
                hist.pop(s, None)
                cur.pop(s, None)
            print("watching:", sorted(subscribed))
        except Exception as e:
            print("refresh", e)


def stopper():
    h, m = map(int, os.environ.get("RUN_UNTIL", "22:05").split(":"))
    while True:
        n = datetime.now(timezone.utc)
        if (n.hour, n.minute) >= (h, m):
            print("done")
            os._exit(0)
        time.sleep(20)


u = get_universe()
info.update(u)
for s in u:
    load_hist(s)
subscribed.update(u)
stream.subscribe_trades(on_trade, DUMMY, *u)
print("watching:", sorted(subscribed))
send("✅ بدأ السكانر اللحظي (Alpaca IEX)")

threading.Thread(target=refresher, daemon=True).start()
threading.Thread(target=stopper, daemon=True).start()
stream.run()
