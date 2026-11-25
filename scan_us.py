import time, logging
import yfinance as yf
import pandas as pd
from yfinance import EquityQuery
from common import send, log_signal, recently_logged, t12

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

LOG = "data/signals_us.csv"

# ===== فلتر السوق =====
MIN_PRICE, MAX_PRICE = 1, 10
MAX_CAP = 500_000_000
MIN_CHG = 3
MIN_DAYVOL = 300_000

# ===== شروط الإشارة =====
VOL_LEN, VOL_MULT = 30, 5.0
QUIET_LEN, QUIET_MAX = 20, 3.0
MOVE = 3.0
FRESH_BARS = 6


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
            s = x["symbol"]
            if len(s) == 5 and s[-1] in "WRU":
                continue
            out[s] = (x.get("shortName") or x.get("longName") or s,
                      x.get("marketCap"))
        offset += 250
        if len(quotes) < 250:
            break
    return out


def check(d):
    hh = d.High.rolling(QUIET_LEN).max().shift(1)
    ll = d.Low.rolling(QUIET_LEN).min().shift(1)
    quiet_pct = (hh - ll) / ll * 100
    quiet = quiet_pct <= QUIET_MAX

    avgv = d.Volume.rolling(VOL_LEN).mean().shift(1)
    spike = (avgv > 0) & (d.Volume >= avgv * VOL_MULT)

    move = (d.Close - d.Open) / d.Open * 100
    strong = (move >= MOVE) & (d.Close > hh)

    tp = (d.High + d.Low + d.Close) / 3
    day = d.index.date
    vw = (tp * d.Volume).groupby(day).cumsum() / d.Volume.groupby(day).cumsum()

    sig = quiet & spike & strong & (d.Close > vw)
    recent = sig.iloc[:-1].tail(FRESH_BARS)
    if not recent.any():
        return None

    ts = recent[recent].index[-1]
    today = d.index.normalize() == ts.normalize()
    day_vol = d[today & (d.index <= ts)].Volume.sum()
    prev = d[d.index.normalize() < ts.normalize()]
    prev_close = prev.Close.iloc[-1] if len(prev) else None
    price = d.Close[ts]

    return ts, {
        "price": price,
        "move": move[ts],
        "vol": d.Volume[ts],
        "vmult": d.Volume[ts] / avgv[ts],
        "quiet": quiet_pct[ts],
        "hh": hh[ts],
        "vw": vw[ts],
        "day_vol": day_vol,
        "chg": (price / prev_close - 1) * 100 if prev_close else None,
    }


def build_message(t, name, cap, ts, i):
    close_time = (ts + pd.Timedelta(minutes=1)).tz_convert("Asia/Riyadh")
    cap_txt = f"{cap/1e6:,.0f} مليون $" if cap else "-"
    chg_txt = f"{i['chg']:+.1f}%" if i["chg"] is not None else "-"
    return (
        f"🚨 سيولة مفاجئة بعد خمول 🇺🇸\n"
        f"━━━━━━━━━━━━━━\n"
        f"📛 السهم: {name}\n"
        f"🔖 الرمز: {t}\n"
        f"🔥 الحدث: انفجار حجم + اختراق بعد فترة خمول (فريم دقيقة)\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 السعر: {i['price']:.2f}$\n"
        f"📈 حركة الشمعة: {i['move']:+.1f}%\n"
        f"📊 حجم الشمعة: {i['vol']:,.0f} سهم ({i['vmult']:.1f}x المتوسط)\n"
        f"📏 نطاق الخمول السابق: {i['quiet']:.1f}%\n"
        f"🔓 اخترق أعلى سعر قبلها: {i['hh']:.2f}$\n"
        f"〰️ VWAP: {i['vw']:.2f}$\n"
        f"📅 التغير عن آخر سعر أمس: {chg_txt}\n"
        f"🧮 حجم اليوم حتى الآن: {i['day_vol']:,.0f} سهم\n"
        f"🏢 القيمة السوقية: {cap_txt}\n"
        f"━━━━━━━━━━━━━━\n"
        f"📆 التاريخ: {close_time:%Y-%m-%d}\n"
        f"🕐 الوقت: {t12(close_time)} (السعودية)\n"
        f"🔗 https://www.tradingview.com/chart/?symbol={t}"
    )


universe = get_universe()
tickers = list(universe)
print("عدد الأسهم بعد الفلتر:", len(tickers))

for k in range(0, len(tickers), 100):
    chunk = tickers[k:k + 100]
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
            res = check(d)
            if res is None:
                continue
            ts, info = res
            close_ts = ts + pd.Timedelta(minutes=1)
            if recently_logged(LOG, t, close_ts):
                continue
            name, cap = universe[t]
            send(build_message(t, name, cap, ts, info))
            log_signal(LOG, t, name, info["price"], close_ts)
            time.sleep(1)
        except Exception as e:
            print(t, e)
