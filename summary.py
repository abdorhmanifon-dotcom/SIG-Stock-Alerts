import os, logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from common import send, t12

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

TARGET, STOP = 5.0, 3.0      # هدف +5% ووقف -3% لقياس النتائج (عدّلها)
FILES = {"live": "data/signals_live.csv", "us": "data/signals_us.csv"}
RES = "data/results.csv"
SA, NY = ZoneInfo("Asia/Riyadh"), ZoneInfo("America/New_York")

now = datetime.now(timezone.utc)
today = now.astimezone(NY).strftime("%Y-%m-%d")
ICON = {"target": "🎯", "stop": "🛑", "none": "➖"}


def outcome(d, ts, price):
    a = d[d.index >= ts]
    if a.empty:
        return None
    tp, sl = price * (1 + TARGET / 100), price * (1 - STOP / 100)
    res = "none"
    for _, r in a.iterrows():
        if r.Low <= sl:        # لو الاثنين بنفس الشمعة نحسبها وقف (تحفظ)
            res = "stop"
            break
        if r.High >= tp:
            res = "target"
            break
    t_hi = a.High.idxmax()
    return {
        "peak": (a.High.max() / price - 1) * 100,
        "low": (a.Low.min() / price - 1) * 100,
        "last": (a.Close.iloc[-1] / price - 1) * 100,
        "mins": int((t_hi - ts).total_seconds() // 60),
        "outcome": res,
    }


def day_summary():
    parts = []
    for src, f in FILES.items():
        if os.path.exists(f):
            x = pd.read_csv(f)
            x["source"] = src
            parts.append(x)
    if not parts:
        send(f"📊 ملخص {today}\nما فيه إشارات اليوم.")
        return
    sig = pd.concat(parts)
    sig["ts"] = pd.to_datetime(sig["ts_utc"], utc=True)
    sig = sig[(sig["ts"] >= now - timedelta(hours=16)) & (sig["ts"] <= now)]
    if sig.empty:
        send(f"📊 ملخص {today}\nما فيه إشارات اليوم.")
        return

    srcs = sig.groupby("symbol")["source"].apply(lambda s: "+".join(sorted(set(s))))
    first = sig.sort_values("ts").drop_duplicates("symbol")
    syms = list(first["symbol"])

    data = {}
    for i in range(0, len(syms), 100):
        chunk = syms[i:i + 100]
        try:
            df = yf.download(chunk, period="2d", interval="1m", prepost=True,
                             group_by="ticker", progress=False, threads=True)
        except Exception as e:
            print("download", e)
            continue
        for t in chunk:
            try:
                d = df[t] if isinstance(df.columns, pd.MultiIndex) else df
                data[t] = d.dropna()
            except Exception:
                pass

    out = []
    for _, r in first.iterrows():
        d = data.get(r["symbol"])
        if d is None or d.empty:
            continue
        o = outcome(d, r["ts"], r["price"])
        if o is None:
            continue
        out.append({
            "date": today, "symbol": r["symbol"], "name": r["name"],
            "source": srcs[r["symbol"]], "first_source": r["source"],
            "signal_ts": r["ts"].strftime("%Y-%m-%d %H:%M:%S"),
            "price": r["price"], **o,
        })
    if not out:
        send(f"📊 ملخص {today}\nما قدرت أجيب بيانات للإشارات.")
        return

    res = pd.DataFrame(out).sort_values("peak", ascending=False)
    if os.path.exists(RES):
        old = pd.read_csv(RES)
        old = old[old["date"] != today]
        allr = pd.concat([old, res])
    else:
        allr = res
    os.makedirs("data", exist_ok=True)
    allr.to_csv(RES, index=False)

    n = len(res)
    tg = (res["outcome"] == "target").sum()
    st = (res["outcome"] == "stop").sum()
    lines = [
        f"📊 ملخص اليوم {today}",
        f"عدد الأسهم اللي جاتها إشارة: {n}",
        "━━━━━━━━━━━━━━",
        f"🎯 وصلت +{TARGET:.0f}% قبل الوقف: {tg}",
        f"🛑 ضربت -{STOP:.0f}% قبل الهدف: {st}",
        f"➖ ولا واحد منهم: {n - tg - st}",
        f"📈 متوسط أعلى ارتفاع بعد التنبيه: {res['peak'].mean():+.1f}%",
        f"📉 متوسط أدنى نزول بعد التنبيه: {res['low'].mean():+.1f}%",
        f"🏁 متوسط الحالة الحالية عن سعر التنبيه: {res['last'].mean():+.1f}%",
        "━━━━━━━━━━━━━━",
    ]
    for k, (_, r) in enumerate(res.iterrows(), 1):
        t_sa = pd.Timestamp(r["signal_ts"], tz="UTC").tz_convert(SA)
        lines.append(
            f"{k}) {r['symbol']} {ICON[r['outcome']]} | {t12(t_sa)} | "
            f"تنبيه {r['price']:.2f}$ | أعلى {r['peak']:+.1f}% (بعد {r['mins']} د) | "
            f"أدنى {r['low']:+.1f}% | الآن {r['last']:+.1f}% | {r['source']}"
        )
    send("\n".join(lines))


def week_summary():
    if not os.path.exists(RES):
        return
    r = pd.read_csv(RES)
    r["d"] = pd.to_datetime(r["date"])
    w = r[r["d"] >= pd.Timestamp(today) - pd.Timedelta(days=4)]
    if w.empty:
        return
    n = len(w)
    tg = (w["outcome"] == "target").sum()
    st = (w["outcome"] == "stop").sum()
    lines = [
        f"🗓 ملخص الأسبوع (حتى {today})",
        f"إجمالي الإشارات: {n}",
        "━━━━━━━━━━━━━━",
        f"🎯 هدف +{TARGET:.0f}%: {tg} ({tg/n*100:.0f}%)",
        f"🛑 وقف -{STOP:.0f}%: {st} ({st/n*100:.0f}%)",
        f"➖ بدون: {n - tg - st}",
        f"📈 متوسط أعلى ارتفاع: {w['peak'].mean():+.1f}%",
        f"📉 متوسط أدنى نزول: {w['low'].mean():+.1f}%",
        f"⏱ متوسط الوقت لأعلى نقطة: {w['mins'].mean():.0f} دقيقة",
        "━━━━━━━━━━━━━━",
        "حسب أول سكانر التقط السهم:",
    ]
    for src, label in (("live", "اللحظي"), ("us", "yfinance")):
        x = w[w["first_source"] == src]
        if len(x):
            t2 = (x["outcome"] == "target").sum()
            s2 = (x["outcome"] == "stop").sum()
            lines.append(f"• {label}: {len(x)} إشارة | 🎯 {t2} | 🛑 {s2} | متوسط الأعلى {x['peak'].mean():+.1f}%")
    lines.append("━━━━━━━━━━━━━━")
    lines.append("أفضل 5 أسهم بالأسبوع:")
    for _, r2 in w.sort_values("peak", ascending=False).head(5).iterrows():
        lines.append(f"• {r2['symbol']} ({r2['date']}): أعلى {r2['peak']:+.1f}%")
    send("\n".join(lines))


day_summary()
if now.weekday() == 4:
    week_summary()
