import os, requests, yfinance as yf
from yfinance import EquityQuery

# ===== فلتر السوق =====
MIN_PRICE, MAX_PRICE = 1, 10
MAX_CAP = 500_000_000
MIN_CHG = 3            # أقل تغير % اليوم لدخول القائمة
MIN_DAYVOL = 300_000   # أقل حجم تداول اليوم

# ===== شروط الإشارة =====
VOL_LEN, VOL_MULT = 30, 5.0
QUIET_LEN, QUIET_MAX = 20, 3.0
MOVE = 3.0
FRESH_BARS = 6


def send(text):
    requests.post(
        f"https://api.telegram.org/bot{os.environ['TG_TOKEN']}/sendMessage",
        data={"chat_id": os.environ["TG_CHAT"], "text": text},
        timeout=20,
    )


def get_universe():
    q = EquityQuery("and", [
        EquityQuery("eq", ["region", "us"]),
        EquityQuery("is-in", ["exchange", "NMS", "NYQ", "ASE", "NCM", "NGM"]),
        EquityQuery("btwn", ["intradayprice", MIN_PRICE, MAX_PRICE]),
        EquityQuery("lt", ["intradaymarketcap", MAX_CAP]),
        EquityQuery("gt", ["percentchange", MIN_CHG]),
        EquityQuery("gt", ["dayvolume", MIN_DAYVOL]),
    ])
    out, offset = {}, 0
    while offset < 1000:
        r = yf.screen(q, offset=offset, size=250,
                      sortField="dayvolume", sortAsc=False)
        quotes = r.get("quotes", [])
        if not quotes:
            break
        for x in quotes:
            out[x["symbol"]] = (
                x.get("shortName") or x.get("longName") or x["symbol"],
                x.get("marketCap"),
            )
        offset += 250
        if len(quotes) < 250:
            break
    return out


def check(d):
    hh = d.High.rolling(QUIET_LEN).max().shift(1)
    ll = d.Low.rolling(QUIET_LEN).min().shift(1)
    quiet = (hh - ll) / ll * 100 <= QUIET_MAX

    avgv = d.Volume.rolling(VOL_LEN).mean().shift(1)
    spike = (avgv > 0) & (d.Volume >= avgv * VOL_MULT)

    move = (d.Close - d.Open) / d.Open * 100
    strong = (move >= MOVE) & (d.Close > hh)

    tp = (d.High + d.Low + d.Close) / 3
    day = d.index.date
    vw = (tp * d.Volume).groupby(day).cumsum() / d.Volume.groupby(day).cumsum()

    sig = quiet & spike & strong & (d.Close > vw)
    recent = sig.iloc[:-1].tail(FRESH_BARS)  # نتجاهل الشمعة اللي ما اكتملت
    return recent[recent].index[-1] if recent.any() else None


universe = get_universe()
tickers = list(universe)
print("عدد الأسهم بعد الفلتر:", len(tickers))

for i in range(0, len(tickers), 100):
    chunk = tickers[i:i + 100]
    try:
        df = yf.download(chunk, period="2d", interval="1m", prepost=True,
                         group_by="ticker", progress=False, threads=True)
    except Exception as e:
        print("download error", e)
        continue

    for t in chunk:
        try:
            d = df[t].dropna()
            if len(d) < VOL_LEN + 5:
                continue
            ts = check(d)
            if ts is None:
                continue

            name, cap = universe[t]
            cap_txt = f"{cap/1e6:.0f}M$" if cap else "-"
            time_sa = ts.tz_convert("Asia/Riyadh").strftime("%Y-%m-%d %H:%M")
            send(
                f"📛 السهم: {name}\n"
                f"🔖 الرمز: {t}\n"
                f"🔥 التنبيه: سيولة مفاجئة بعد خمول\n"
                f"💰 السعر: {d.Close[ts]:.2f}\n"
                f"🏢 القيمة السوقية: {cap_txt}\n"
                f"🕐 الوقت: {time_sa} (السعودية)"
            )
        except Exception as e:
            print(t, e)
