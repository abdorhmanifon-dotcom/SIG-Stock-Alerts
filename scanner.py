# -*- coding: utf-8 -*-
"""مراقب تداول: نفس منطق مؤشر Pine (الإشارات المؤكدة ✅ فقط) ويرسل تلقرام."""
import os, json, time
import numpy as np
import pandas as pd

# ====================== الإعدادات ======================
SYMBOLS = ["2030", "2381", "4030", "1301", "1304", "1322", "1323", "1324", "1325",
           "2090", "2150", "4143", "1212", "1214", "2040", "2110", "2320", "2160",
           "4145", "4147", "1833", "1834", "4031", "4260", "4261", "4011", "1830",
           "4292", "4050", "4051", "4191", "4162", "4163", "2100", "2270"]
TFS = ["30m", "1h", "4h", "1d"]
PREFIX = "My Alerts"
TZ = "Asia/Riyadh"
DELAY_MIN = 15          # تأخير بيانات Yahoo التقريبي (دقائق)
SCAN_LAST = 2           # نفحص آخر كم شمعة مغلقة (والمكرر ما يتكرر بفضل state.json)
TREND_FILTER = "mark"   # none = بدون | mark = تمييز عكس الاتجاه | only = مع الاتجاه فقط
MIN_SCORE = 3           # أقل درجة توافق من 5 (0 = بدون فلتر)
EXTRA_PATTERNS = False  # الشموع الإضافية (نجوم، جنود، داخلية، ملقط، دوجي...) False = مطفية لتقليل الإزعاج
GAP_DAY_OPEN_ONLY = True  # في فريمات الدقائق/الساعات: الفجوة تُحسب فقط عند أول شمعة باليوم
STATE_FILE = "state.json"

# نفس معاملات المؤشر
ATR_LEN = 14; RSI_LEN = 14; RSI_MA = 9; RSI_OS = 35; RSI_OB = 65; RSI_LOOK = 5
MB_BODY = 0.90; MB_ATR = 0.8; VOL_LEN = 20; VOL_MULT = 2.0
FAKE_MAX = 10; MAX_TOUCHES = 3; TOUCH_ATR = 0.15; TRACK_MAX = 30
FLIP_TOL = 0.3; FLIP_MAX = 30
GAP_ATR = 0.1; GAP_KEEP = 3
WICK = 0.6; NEAR_LOOK = 20; TREND_LEN = 50; DIV_MAX = 60
PIV = {"30m": (3, 1.0), "1h": (3, 1.0), "4h": (4, 1.5), "1d": (5, 2.0)}   # (شموع القمة، أقل حركة ATR)
TF_TXT = {"30m": "30m", "1h": "1H", "4h": "4H", "1d": "D"}
TF_MIN = {"30m": 30, "1h": 60, "4h": 240, "1d": 1440}

CANDLE_EV = [("bullRev", 1, "✅ شمعة ابتلاع إيجابية", False), ("bearRev", -1, "✅ شمعة ابتلاع سلبية", False),
             ("rejBot", 1, "✅ رفض هبوط إيجابي عند القاع", False), ("rejTop", -1, "✅ رفض صعود سلبي عند القمة", False),
             ("ms", 1, "✅ نجمة الصباح", True), ("es", -1, "✅ نجمة المساء", True),
             ("sold", 1, "✅ ثلاثة جنود بيض", True), ("crow", -1, "✅ ثلاثة غربان سود", True),
             ("inB", 1, "✅ اختراق شمعة داخلية للأعلى", True), ("inS", -1, "✅ كسر شمعة داخلية للأسفل", True),
             ("pierce", 1, "✅ شمعة خارقة إيجابية", True), ("dark", -1, "✅ غطاء سحابي سلبي", True),
             ("twBot", 1, "✅ ملقط قاع", True), ("twTop", -1, "✅ ملقط قمة", True),
             ("djBot", 1, "✅ دوجي عند قاع", True), ("djTop", -1, "✅ دوجي عند قمة", True)]


# ====================== البيانات ======================
def _clean(df):
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
    df = df.dropna(subset=["open", "high", "low", "close"])
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(TZ)
    return df[~df.index.duplicated()].sort_index()


def fetch_symbol(code):
    import yfinance as yf
    t = yf.Ticker(f"{code}.SR")
    out = {}
    for key, interval, period in (("30m", "30m", "59d"), ("1h", "60m", "200d"), ("1d", "1d", "3y")):
        try:
            d = t.history(period=period, interval=interval, auto_adjust=False)
            out[key] = _clean(d) if d is not None and len(d) else None
        except Exception as e:
            print("fetch error", code, key, e)
            out[key] = None
        time.sleep(0.2)
    return out


def session_only(df):
    return df[(df.index.hour >= 10) & (df.index.hour < 15)]


def make_4h(h1):
    d = session_only(h1)
    if d.empty:
        return None
    grp = d.index.normalize() + pd.to_timedelta(((d.index.hour - 10) // 4) * 4 + 10, unit="h")
    g = d.groupby(grp)
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                        "close": g["close"].last(), "volume": g["volume"].sum()})
    out["end"] = [x + pd.Timedelta(hours=4 if x.hour == 10 else 1) for x in out.index]
    return out


def add_end(df, tf):
    df = df.copy()
    if tf == "1d":
        df["end"] = df.index.normalize() + pd.Timedelta(hours=15, minutes=10)
    else:
        df["end"] = df.index + pd.Timedelta(minutes=TF_MIN[tf])
    return df


def drop_forming(df, now):
    return df[df["end"] <= now - pd.Timedelta(minutes=DELAY_MIN)]


# ====================== المؤشرات ======================
def rma(s, n):
    return s.ewm(alpha=1 / n, adjust=False).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def calc(df):
    df = df.copy()
    c, h, l = df["close"], df["high"], df["low"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    df["atr"] = rma(tr, ATR_LEN)
    d = c.diff()
    rs = rma(d.clip(lower=0), RSI_LEN) / rma((-d).clip(lower=0), RSI_LEN)
    df["rsi"] = 100 - 100 / (1 + rs)
    df["rsima"] = df["rsi"].rolling(RSI_MA).mean()
    m = ema(c, 12) - ema(c, 26)
    df["macd"] = m
    df["macds"] = ema(m, 9)
    vb = df["volume"].rolling(VOL_LEN).mean()
    vd = df["volume"].rolling(VOL_LEN).std(ddof=0) * VOL_MULT
    df["volbasis"] = vb
    df["volspike"] = df["volume"] > (vb + vd)
    df["ema"] = ema(c, TREND_LEN)
    return df


def trend_array(df, tf, d4):
    if tf in ("4h", "1d") or d4 is None or d4.empty:
        return (df["close"] > df["ema"]).fillna(False).values
    a = pd.DataFrame({"avail": d4["end"].values, "bull": (d4["close"] > d4["ema"]).values}).sort_values("avail")
    q = pd.DataFrame({"t": df["end"].values})
    m = pd.merge_asof(q, a, left_on="t", right_on="avail", direction="backward")
    return m["bull"].fillna(False).astype(bool).values


def prev_levels(idx, daily, tf):
    """قمة/قاع أمس والأسبوع الماضي لكل شمعة (بدون نظرة للمستقبل)."""
    n = len(idx)
    nan = np.full(n, np.nan)
    if daily is None or daily.empty:
        return nan, nan, nan, nan
    dd = daily.index.normalize().tz_localize(None).values
    dh, dl = daily["high"].values, daily["low"].values
    bidx = idx.normalize().tz_localize(None)
    # أمس
    if tf != "1d":
        pos = np.searchsorted(dd, bidx.values, side="left") - 1
        ok = pos >= 0
        pdH = np.where(ok, dh[pos.clip(0)], np.nan)
        pdL = np.where(ok, dl[pos.clip(0)], np.nan)
    else:
        pdH, pdL = nan, nan
    # الأسبوع الماضي (أسبوع ينتهي الجمعة)
    dix = daily.index.normalize().tz_localize(None)
    wk = dix + pd.to_timedelta((4 - dix.weekday) % 7, unit="D")
    wdf = pd.DataFrame({"wk": wk, "h": dh, "l": dl}).groupby("wk").agg(h=("h", "max"), l=("l", "min")).sort_index()
    wkeys = wdf.index.values
    bwk = bidx + pd.to_timedelta((4 - bidx.weekday) % 7, unit="D")
    pos = np.searchsorted(wkeys, bwk.values, side="left") - 1
    ok = pos >= 0
    pwH = np.where(ok, wdf["h"].values[pos.clip(0)], np.nan)
    pwL = np.where(ok, wdf["l"].values[pos.clip(0)], np.nan)
    return pdH, pdL, pwH, pwL


def candle_flags(df):
    o, h, l, c, A = df["open"], df["high"], df["low"], df["close"], df["atr"]
    body = (c - o).abs()
    rng = h - l
    upW = h - df[["open", "close"]].max(axis=1)
    loW = df[["open", "close"]].min(axis=1) - l
    bu, be = c > o, c < o
    S = lambda x, k=1: x.shift(k)
    B = lambda x, k=1: x.shift(k, fill_value=False)
    nh = h >= h.rolling(NEAR_LOOK).max().shift(1)
    nl = l <= l.rolling(NEAR_LOOK).min().shift(1)
    f = {}
    f["bullRev"] = bu & B(be) & (o <= S(c)) & (c >= S(o)) & (body > S(body))
    f["bearRev"] = be & B(bu) & (o >= S(c)) & (c <= S(o)) & (body > S(body))
    hammer = (rng > 0) & (loW / rng >= WICK) & (body / rng <= 0.35)
    star = (rng > 0) & (upW / rng >= WICK) & (body / rng <= 0.35)
    f["rejBot"] = hammer & nl
    f["rejTop"] = star & nh
    f["ms"] = B(be, 2) & (S(body, 2) > A * 0.5) & (S(body) < S(body, 2) * 0.4) & bu & (c > (S(o, 2) + S(c, 2)) / 2)
    f["es"] = B(bu, 2) & (S(body, 2) > A * 0.5) & (S(body) < S(body, 2) * 0.4) & be & (c < (S(o, 2) + S(c, 2)) / 2)
    f["sold"] = (bu & B(bu) & B(bu, 2) & (c > S(c)) & (S(c) > S(c, 2)) & (o > S(o)) & (S(o) > S(o, 2))
                 & (body > A * .4) & (S(body) > A * .4) & (S(body, 2) > A * .4))
    f["crow"] = (be & B(be) & B(be, 2) & (c < S(c)) & (S(c) < S(c, 2)) & (o < S(o)) & (S(o) < S(o, 2))
                 & (body > A * .4) & (S(body) > A * .4) & (S(body, 2) > A * .4))
    f["inB"] = (S(h) < S(h, 2)) & (S(l) > S(l, 2)) & (c > S(h, 2))
    f["inS"] = (S(h) < S(h, 2)) & (S(l) > S(l, 2)) & (c < S(l, 2))
    f["pierce"] = B(be) & (S(body) > A * .4) & bu & (o < S(l)) & (c > (S(o) + S(c)) / 2) & (c < S(o))
    f["dark"] = B(bu) & (S(body) > A * .4) & be & (o > S(h)) & (c < (S(o) + S(c)) / 2) & (c > S(o))
    f["twTop"] = B(bu) & be & ((h - S(h)).abs() <= A * .05) & nh
    f["twBot"] = B(be) & bu & ((l - S(l)).abs() <= A * .05) & nl
    dj = (rng >= A * .5) & (rng > 0) & (body / rng <= 0.1)
    f["djTop"] = dj & nh
    f["djBot"] = dj & nl
    return {k: v.fillna(False).values.astype(bool) for k, v in f.items()}


# ====================== المنطق الرئيسي ======================
def new_swing(price, idx, rsiv, macdv):
    return dict(price=price, idx=idx, rsiV=rsiv, macdV=macdv, brkC=False, brkBar=0, fkOn=False, fkUsed=False,
                fkBar=0, fkExt=np.nan, fkRsiX=np.nan, fkMacdX=np.nan, touches=0, tArm=False, dead=False)


def prune(arr):
    while len(arr) > TRACK_MAX:
        k = next((j for j, s in enumerate(arr) if s["dead"]), 0)
        arr.pop(k)


def lvl(p):
    return f" @{p:.2f}"


def div_tag(r, m):
    return " + دايفرجنس RSI و MACD" if r and m else " + دايفرجنس RSI" if r else " + دايفرجنس MACD" if m else ""


def dvt(r, m):
    return " (RSI + MACD)" if r and m else " (RSI)" if r else " (MACD)"


def analyze(df, tf, trend, lv, scan_last=SCAN_LAST):
    """يرجع {رقم الشمعة: [نصوص الأحداث]} لآخر scan_last شموع."""
    n = len(df)
    if n < 60:
        return {}
    L = R = PIV[tf][0]
    minSwing = PIV[tf][1]
    o, h, l, c, v = (df[k].values for k in ("open", "high", "low", "close", "volume"))
    atr, rsi, rsim = df["atr"].values, df["rsi"].values, df["rsima"].values
    macd, macds, volb, vsp = df["macd"].values, df["macds"].values, df["volbasis"].values, df["volspike"].values
    pdH, pdL, pwH, pwL = lv
    cf = candle_flags(df)
    dates = df.index.normalize()
    lo = n - scan_last
    raw = {}

    def add(i, d, text):
        if i >= lo:
            raw.setdefault(i, []).append((d, text))

    highs, lows = [], []
    lastType, lastPiv = 0, np.nan
    flipUp = dict(on=False, lvl=np.nan, bar=0)
    flipDn = dict(on=False, lvl=np.nan, bar=0)
    gaps = []
    dvH = dvL = None

    def step(arr, sg, i, a):
        best = fake = ret = None
        fk_r = fk_m = False
        tol = a * TOUCH_ATR
        for s in arr:
            if s["dead"]:
                continue
            P = s["price"]
            if not s["brkC"] and (c[i] - P) * sg > 0:
                s.update(brkC=True, brkBar=i, touches=0, tArm=True)
                if best is None or (P - best["price"]) * sg > 0:
                    best = s
            just = False
            wick = h[i] if sg > 0 else l[i]
            if not s["fkOn"] and not s["fkUsed"] and (wick - P) * sg > 0:
                s.update(fkOn=True, fkBar=i, fkExt=(l[i] if sg > 0 else h[i]), fkRsiX=rsi[i], fkMacdX=macd[i])
                just = True
            elif s["fkOn"]:
                f = max if sg > 0 else min
                s["fkRsiX"] = f(s["fkRsiX"], rsi[i])
                s["fkMacdX"] = f(s["fkMacdX"], macd[i])
            if s["fkOn"] and not just:
                if (s["fkExt"] - c[i]) * sg > 0:
                    r = (s["rsiV"] - s["fkRsiX"]) * sg > 0
                    m = (s["macdV"] - s["fkMacdX"]) * sg > 0
                    if fake is None or (P - fake["price"]) * sg > 0:
                        fake, fk_r, fk_m = s, r, m
                    s.update(fkOn=False, fkUsed=False, brkC=False, tArm=True)
                elif i - s["fkBar"] >= FAKE_MAX:
                    s.update(fkOn=False, fkUsed=True)
            if s["brkC"] and not s["fkOn"] and i > s["brkBar"] and (P - c[i]) * sg > 0:
                s.update(brkC=False, fkUsed=False, touches=0, tArm=True)
            near = h[i] if sg > 0 else l[i]
            far = l[i] if sg > 0 else h[i]
            tch = ((P - far) * sg >= -tol) if s["brkC"] else ((near - P) * sg >= -tol)
            after = (not s["brkC"]) or i > s["brkBar"]
            if tch and after:
                if s["tArm"]:
                    s["touches"] += 1
                    s["tArm"] = False
                    if s["touches"] > MAX_TOUCHES:
                        s["dead"] = True
                    elif s["brkC"]:
                        ret = (P, s["touches"])
            elif not tch:
                s["tArm"] = True
        return best, fake, fk_r, fk_m, ret

    for i in range(30, n):
        a = atr[i]
        if np.isnan(a):
            continue
        # ---------- القمم والقيعان ----------
        p = i - R
        isPH = isPL = False
        if p - L >= 0:
            isPH = h[p] > h[p - L:p].max() and h[p] > h[p + 1:i + 1].max()
            isPL = l[p] < l[p - L:p].min() and l[p] < l[p + 1:i + 1].min()
        if isPH and isPL:
            isPH = isPL = False
        if isPH:
            ph = h[p]
            ok = rep = False
            if lastType == 1:
                if ph > lastPiv:
                    ok = rep = True
            elif lastType == -1:
                ok = (ph - lastPiv) >= a * minSwing
            else:
                ok = True
            if ok:
                if rep and highs and not highs[-1]["brkC"]:
                    highs.pop()
                highs.append(new_swing(ph, p, rsi[p], macd[p]))
                prune(highs)
                lastType, lastPiv = 1, ph
            # دايفرجنس مستقل
            if dvH is not None and p - dvH[3] <= DIV_MAX:
                rDn, mDn = rsi[p] < dvH[1], macd[p] < dvH[2]
                rUp, mUp = rsi[p] > dvH[1], macd[p] > dvH[2]
                if ph > dvH[0] and (rDn or mDn):
                    add(i, -1, "✅ دايفرجنس سلبي عادي (انعكاس)" + dvt(rDn, mDn))
                elif ph < dvH[0] and (rUp or mUp):
                    add(i, -1, "✅ دايفرجنس سلبي مخفي (استمرار هابط)" + dvt(rUp, mUp))
            dvH = (ph, rsi[p], macd[p], p)
        if isPL:
            pl = l[p]
            ok = rep = False
            if lastType == -1:
                if pl < lastPiv:
                    ok = rep = True
            elif lastType == 1:
                ok = (lastPiv - pl) >= a * minSwing
            else:
                ok = True
            if ok:
                if rep and lows and not lows[-1]["brkC"]:
                    lows.pop()
                lows.append(new_swing(pl, p, rsi[p], macd[p]))
                prune(lows)
                lastType, lastPiv = -1, pl
            if dvL is not None and p - dvL[3] <= DIV_MAX:
                rUp, mUp = rsi[p] > dvL[1], macd[p] > dvL[2]
                rDn, mDn = rsi[p] < dvL[1], macd[p] < dvL[2]
                if pl < dvL[0] and (rUp or mUp):
                    add(i, 1, "✅ دايفرجنس إيجابي عادي (انعكاس)" + dvt(rUp, mUp))
                elif pl > dvL[0] and (rDn or mDn):
                    add(i, 1, "✅ دايفرجنس إيجابي مخفي (استمرار صاعد)" + dvt(rDn, mDn))
            dvL = (pl, rsi[p], macd[p], p)

        # ---------- اختراق / كسر / وهمي / إعادة اختبار ----------
        bestH, fkBear, fbR, fbM, retH = step(highs, 1, i, a)
        bestL, fkBull, flR, flM, retL = step(lows, -1, i, a)
        if bestH:
            add(i, 1, "✅ اختراق قمة بإغلاق (تصير دعم)" + lvl(bestH["price"]))
        if bestL:
            add(i, -1, "✅ كسر قاع بإغلاق (يصير مقاومة)" + lvl(bestL["price"]))
        if retH:
            add(i, 1, "✅ إعادة اختبار قمة مخترقة (دعم)" + lvl(retH[0]) + f" (لمسة {retH[1]}/{MAX_TOUCHES})")
        if retL:
            add(i, -1, "✅ إعادة اختبار قاع مكسور (مقاومة)" + lvl(retL[0]) + f" (لمسة {retL[1]}/{MAX_TOUCHES})")
        if fkBear:
            add(i, -1, "✅ الاختراق الوهمي السلبي" + lvl(fkBear["price"]) + div_tag(fbR, fbM))
        if fkBull:
            add(i, 1, "✅ الكسر الوهمي الإيجابي" + lvl(fkBull["price"]) + div_tag(flR, flM))

        # ---------- تبادل الأدوار ----------
        fu = flipUp["on"] and i > flipUp["bar"] and l[i] <= flipUp["lvl"] + a * FLIP_TOL and c[i] > flipUp["lvl"]
        fd = flipDn["on"] and i > flipDn["bar"] and h[i] >= flipDn["lvl"] - a * FLIP_TOL and c[i] < flipDn["lvl"]
        if fu or (flipUp["on"] and (i - flipUp["bar"] > FLIP_MAX or c[i] < flipUp["lvl"] - a)):
            flipUp["on"] = False
        if fd or (flipDn["on"] and (i - flipDn["bar"] > FLIP_MAX or c[i] > flipDn["lvl"] + a)):
            flipDn["on"] = False
        if fkBear and flipUp["on"] and fkBear["price"] == flipUp["lvl"]:
            flipUp["on"] = False
        if fkBull and flipDn["on"] and fkBull["price"] == flipDn["lvl"]:
            flipDn["on"] = False
        if bestH:
            flipUp.update(on=True, lvl=bestH["price"], bar=i)
        if bestL:
            flipDn.update(on=True, lvl=bestL["price"], bar=i)
        if fu:
            add(i, 1, "✅ تبادل الأدوار الإيجابي")
        if fd:
            add(i, -1, "✅ تبادل الأدوار السلبي")

        # ---------- الفجوات ----------
        gClosedUp = gClosedDn = gRetUp = gRetDn = gNewUp = gNewDn = False
        for g in gaps[:]:
            if g["up"]:
                if l[i] <= g["bot"]:
                    gClosedUp = True
                    gaps.remove(g)
                elif not g["tested"] and l[i] <= g["top"]:
                    g["tested"] = True
                    gRetUp = True
            else:
                if h[i] >= g["top"]:
                    gClosedDn = True
                    gaps.remove(g)
                elif not g["tested"] and h[i] >= g["bot"]:
                    g["tested"] = True
                    gRetDn = True
        dayOpen = (tf == "1d") or (not GAP_DAY_OPEN_ONLY) or dates[i] != dates[i - 1]
        gmin = a * GAP_ATR
        if dayOpen and o[i] > c[i - 1] and l[i] > c[i - 1] and (o[i] - c[i - 1]) >= gmin:
            gNewUp = True
            gaps.append(dict(up=True, top=o[i], bot=c[i - 1], tested=l[i] < o[i]))
            ups = [g for g in gaps if g["up"]]
            while len(ups) > GAP_KEEP:
                gaps.remove(ups.pop(0))
        if dayOpen and o[i] < c[i - 1] and h[i] < c[i - 1] and (c[i - 1] - o[i]) >= gmin:
            gNewDn = True
            gaps.append(dict(up=False, top=c[i - 1], bot=o[i], tested=h[i] > o[i]))
            dns = [g for g in gaps if not g["up"]]
            while len(dns) > GAP_KEEP:
                gaps.remove(dns.pop(0))
        if gNewUp: add(i, 1, "✅ فجوة سعرية صاعدة جديدة")
        if gNewDn: add(i, -1, "✅ فجوة سعرية هابطة جديدة")
        if gRetUp: add(i, 1, "✅ إعادة اختبار الفجوة الإيجابية")
        if gRetDn: add(i, -1, "✅ إعادة اختبار الفجوة السلبية")
        if gClosedUp: add(i, -1, "✅ إغلاق الفجوة الصاعدة")
        if gClosedDn: add(i, 1, "✅ إغلاق الفجوة الهابطة")

        if i < lo:
            continue
        # ---------- أحداث لا تحتاج حالة (فقط لآخر الشموع) ----------
        rg, bd = h[i] - l[i], abs(c[i] - o[i])
        bull, bear = c[i] > o[i], c[i] < o[i]
        if rg > 0 and bd / rg >= MB_BODY and rg >= a * MB_ATR:
            add(i, 1 if bull else -1, "✅ ماربوزو إيجابي" if bull else "✅ ماربوزو سلبي")
        if vsp[i] and (bull or bear):
            add(i, 1 if bull else -1, "✅ شمعة حجم عالي إيجابية" if bull else "✅ شمعة حجم عالي سلبية")
        if i >= RSI_LOOK and not np.isnan(rsim[i - 1]):
            xUp = rsi[i] > rsim[i] and rsi[i - 1] <= rsim[i - 1]
            xDn = rsi[i] < rsim[i] and rsi[i - 1] >= rsim[i - 1]
            if xUp and rsi[i - RSI_LOOK + 1:i + 1].min() <= RSI_OS:
                add(i, 1, "✅ انعكاس RSI إيجابي")
            if xDn and rsi[i - RSI_LOOK + 1:i + 1].max() >= RSI_OB:
                add(i, -1, "✅ انعكاس RSI سلبي")
        for key, d, text, extra in CANDLE_EV:
            if extra and not EXTRA_PATTERNS:
                continue
            if cf[key][i]:
                add(i, d, text)
        for lv_, name in ((pdH[i], "أمس"), (pwH[i], "الأسبوع الماضي")):
            if not np.isnan(lv_) and h[i] > lv_ and o[i] <= lv_ and c[i] < lv_:
                add(i, -1, f"✅ سحب سيولة فوق قمة {name}" + lvl(lv_))
        for lv_, name in ((pdL[i], "أمس"), (pwL[i], "الأسبوع الماضي")):
            if not np.isnan(lv_) and l[i] < lv_ and o[i] >= lv_ and c[i] > lv_:
                add(i, 1, f"✅ سحب سيولة تحت قاع {name}" + lvl(lv_))

    # ---------- الدرجة ⭐ وفلتر الاتجاه ----------
    out = {}
    for i, items in raw.items():
        rg, bd = h[i] - l[i], abs(c[i] - o[i])
        volOk = (not np.isnan(volb[i])) and v[i] > volb[i]
        body_ok = rg > 0 and bd / rg >= 0.5
        sBull = int(trend[i]) + int(volOk) + int(rsi[i] > 50) + int(c[i] > o[i] and body_ok) + int(macd[i] > macds[i])
        sBear = int(not trend[i]) + int(volOk) + int(rsi[i] < 50) + int(c[i] < o[i] and body_ok) + int(macd[i] < macds[i])
        texts = []
        for d, t in items:
            sc = sBull if d > 0 else sBear
            aligned = (d > 0 and trend[i]) or (d < 0 and not trend[i])
            if sc < MIN_SCORE:
                continue
            if TREND_FILTER == "only" and not aligned:
                continue
            tag = f" ⭐{sc}/5"
            if TREND_FILTER == "mark" and not aligned:
                tag += " ⚠عكس الاتجاه"
            texts.append(t + tag)
        if texts:
            out[i] = texts
    return out


# ====================== التشغيل ======================
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f), False
        except Exception:
            pass
    return {"sent": {}}, True


def save_state(st, now):
    cut = (now - pd.Timedelta(days=10)).isoformat()
    st["sent"] = {k: t for k, t in st["sent"].items() if t >= cut}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=0)


def send_telegram(text):
    if os.environ.get("DRY"):
        print("---- [DRY] ----\n" + text)
        return
    import requests
    tok, chat = os.environ.get("TG_TOKEN"), os.environ.get("TG_CHAT")
    if not tok or not chat:
        print("TG_TOKEN / TG_CHAT غير موجودين")
        return
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                      data={"chat_id": chat, "text": text, "disable_web_page_preview": True}, timeout=30)
    if r.status_code != 200:
        print("telegram error", r.status_code, r.text[:200])


def send_chunked(lines):
    buf = ""
    for ln in lines:
        if len(buf) + len(ln) + 1 > 3500:
            send_telegram(buf)
            buf = ""
        buf += ln + "\n"
    if buf.strip():
        send_telegram(buf)


def main():
    now = pd.Timestamp.now(tz=TZ)
    st, first = load_state()
    lines, new_keys = [], {}
    for code in SYMBOLS:
        data = fetch_symbol(code)
        daily = data.get("1d")
        if daily is None or len(daily) < 60:
            print("لا توجد بيانات يومية كافية:", code)
            continue
        h1 = data.get("1h")
        h1s = session_only(h1) if h1 is not None else None
        d4_all = make_4h(h1) if h1 is not None else None
        d4c = calc(drop_forming(d4_all, now)) if d4_all is not None and len(d4_all) > 60 else None
        frames = {}
        if data.get("30m") is not None:
            frames["30m"] = add_end(session_only(data["30m"]), "30m")
        if h1s is not None and len(h1s):
            frames["1h"] = add_end(h1s, "1h")
        if d4_all is not None:
            frames["4h"] = d4_all
        frames["1d"] = add_end(daily, "1d")
        for tf in TFS:
            df = frames.get(tf)
            if df is None:
                continue
            df = drop_forming(df, now)
            if len(df) < 80:
                continue
            df = calc(df)
            trend = trend_array(df, tf, d4c)
            lv = prev_levels(df.index, daily, tf)
            try:
                res = analyze(df, tf, trend, lv)
            except Exception as e:
                print("analyze error", code, tf, repr(e))
                continue
            for i, texts in res.items():
                ts = df.index[i]
                fresh = []
                for t in texts:
                    key = f"{code}|{tf}|{ts.isoformat()}|{t}"
                    if key not in st["sent"]:
                        fresh.append(t)
                        new_keys[key] = now.isoformat()
                if fresh and not first:
                    lines.append(f"{PREFIX} | {code} {TF_TXT[tf]} | " + " • ".join(fresh) +
                                 f" | 🕒 {df['end'].iloc[i]:%H:%M %d/%m}")
        print("تم:", code)
    st["sent"].update(new_keys)
    if first:
        send_telegram("✅ المراقب اشتغل. من الحين تجيك الإشارات المؤكدة على الأسهم اللي حددتها.")
    elif lines:
        send_chunked(lines)
    save_state(st, now)


if __name__ == "__main__":
    main()
