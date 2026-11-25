import os
import io
import numpy as np
import pandas as pd

# ===================== الإعدادات =====================
SYMBOLS = {
    # ========== السوق السعودي (غير مالي + غير إسمنت) ==========
    "2222.SR": "أرامكو السعودية",
    "1211.SR": "معادن",
    "7010.SR": "الاتصالات السعودية",
    "2010.SR": "سابك",
    "2082.SR": "أكوا باور",
    "4013.SR": "سليمان الحبيب",
    "5110.SR": "الكهرباء السعودية",
    "2020.SR": "سابك للمغذيات الزراعية",
    "7020.SR": "موبايلي",
    "2280.SR": "المراعي",
    "4030.SR": "البحري",
    "2380.SR": "بترو رابغ",
    "7203.SR": "علم",
    "7202.SR": "سلوشنز",
    "4190.SR": "جرير",
    "4300.SR": "دار الأركان",
    "2382.SR": "أديس",
    "2381.SR": "الحفر العربية",
    "2030.SR": "المصافي",
    "4001.SR": "العثيم",
    "2050.SR": "صافولا",
    "1212.SR": "أسترا الصناعية",
    "4002.SR": "المواساة",
    "4004.SR": "دله الصحية",
    "4007.SR": "الحمادي",
    "4009.SR": "السعودي الألماني",
    "1830.SR": "لجام",
    "4142.SR": "كابلات الرياض",
    "1303.SR": "الصناعات الكهربائية",
    "2290.SR": "ينساب",
    "2310.SR": "سبكيم",
    "2330.SR": "المتقدمة",
    "2350.SR": "كيان السعودية",
    "2060.SR": "التصنيع",
    "1201.SR": "تكوين",
    "1202.SR": "مبكو",
    "1210.SR": "بي سي آي",
    "1301.SR": "أسلاك",
    "1304.SR": "اليمامة للحديد",
    "1320.SR": "أنابيب السعودية",
    "1321.SR": "أنابيب الشرق",
    "1322.SR": "أماك",
    "2001.SR": "كيمانول",
    "2090.SR": "جبسكو",
    "2150.SR": "زجاج",
    "2170.SR": "اللجين",
    "2180.SR": "فيبكو",
    "2200.SR": "أنابيب",
    "2220.SR": "معدنية",
    "2223.SR": "لوبريف",
    "2300.SR": "صناعة الورق",
    "2040.SR": "الخزف السعودي",
    "2110.SR": "الكابلات السعودية",
    "2320.SR": "البابطين",
    "2370.SR": "مسك",
    "2270.SR": "سدافكو",
    "4003.SR": "إكسترا",
    "1810.SR": "سيرا",
    "2070.SR": "الدوائية",
    "4015.SR": "جمجوم فارما",
    "4200.SR": "الدريس",
    "4031.SR": "الخدمات الأرضية",
    "4040.SR": "سابتكو",
    "2080.SR": "الغاز",
    "2083.SR": "مرافق",
    "1213.SR": "نسيج",
    "1214.SR": "شاكر",
    "1302.SR": "بوان",
    "2160.SR": "أميانتيت",
    "4011.SR": "لازوردي",
    "4161.SR": "بن داود",
    "4164.SR": "النهدي",
    "6002.SR": "هرفي",
    "6012.SR": "ريدان",
    "6050.SR": "الأسماك",
    "7030.SR": "زين",
    "2100.SR": "وفرة",
    "2130.SR": "صدق",
    "4230.SR": "البحر الأحمر",
    "4061.SR": "أنعام",
    "4240.SR": "سينومي ريتيل",
    "1323.SR": "يو سي آي سي",
    "1831.SR": "مهارة",
    "4008.SR": "ساكو",
    "4191.SR": "أبو معطي",
    "6010.SR": "نادك",
    "2283.SR": "المطاحن الأولى",
    "2284.SR": "المطاحن الحديثة",
    "4016.SR": "أفالون فارما",
    "4017.SR": "فقيه الطبية",
    "1832.SR": "صدر",
    "1833.SR": "الموارد",
    "1834.SR": "سماسكو",
    "6001.SR": "حلواني إخوان",
    "4162.SR": "المنجم للأغذية",
    "4163.SR": "الدواء",
    "4165.SR": "الماجد للعود",
    "7200.SR": "المعمر لأنظمة المعلومات",
    "7204.SR": "برزنتيشن",
    "7211.SR": "عزم",
    "4263.SR": "سال",
    "2081.SR": "الخريف",
    "4145.SR": "أو جي سي",
    "2340.SR": "ارتيكس",
    "2360.SR": "الفخارية",

    # ========== السوق الأمريكي ==========
    # Mega Cap
    "AAPL": "أبل",
    "NVDA": "إنفيديا",
    "MSFT": "مايكروسوفت",
    "GOOGL": "ألفابت",
    "AMZN": "أمازون",
    "AVGO": "برودكوم",
    "META": "ميتا",
    "TSLA": "تسلا",
    "LLY": "إيلي ليلي",
    "WMT": "وولمارت",
    "MU": "ميكرون",
    "AMD": "إيه إم دي",
    "XOM": "إكسون موبيل",
    "JNJ": "جونسون آند جونسون",
    "COST": "كوستكو",
    "CVX": "شيفرون",
    "KO": "كوكا كولا",
    "PLTR": "بالانتير",
    "PG": "بروكتر آند غامبل",
    "ORCL": "أوراكل",
    "CSCO": "سيسكو",
    "UNH": "يونايتد هيلث",
    "MRK": "ميرك",
    "HD": "هوم ديبو",
    "CAT": "كاتربيلر",

    # Large Cap
    "NFLX": "نتفليكس",
    "CRM": "سيلزفورس",
    "ADBE": "أدوبي",
    "PEP": "بيبسيكو",
    "TMO": "ثيرمو فيشر",
    "ACN": "أكسنتشر",
    "LIN": "ليندي",
    "DHR": "داناهر",
    "ABT": "أبوت",
    "TXN": "تكساس إنسترومنتس",
    "QCOM": "كوالكوم",
    "INTU": "إنتيويت",
    "AMGN": "أمجين",
    "ISRG": "إنتيوتيف سرجيكال",
    "BKNG": "بوكينج",
    "GE": "جنرال إلكتريك",
    "UBER": "أوبر",
    "NOW": "سيرفس ناو",
    "PANW": "بالو ألتو",
    "AMAT": "أبلايد ماتيريالز",
    "LRCX": "لام ريسيرش",
    "SBUX": "ستاربكس",
    "MDT": "ميدترونيك",
    "SYK": "سترايكير",
    "BMY": "بريستول مايرز",

    # Mid Cap
    "CRWD": "كراودسترايك",
    "SNOW": "سنوفليك",
    "SMCI": "سوبر مايكرو",
    "MDB": "مونجو دي بي",
    "DDOG": "داتادوغ",
    "NET": "كلاودفلير",
    "ZS": "زي سكيلر",
    "TEAM": "أتلاسيان",
    "FTNT": "فورتينت",
    "WDAY": "ووركداي",
    "ANET": "أريستا نتوركس",
    "ON": "أون سيميكونداكتور",
    "MPWR": "مونوليثيك باور",
    "ALGN": "ألاين تكنولوجي",
    "DXCM": "ديكسكوم",
    "IDXX": "آيدكس",
    "VRSK": "فيريسك",
    "CTAS": "سينتاس",
    "FAST": "فاستينال",
    "ODFL": "أولد دومينيون",
    "ROST": "روس ستورز",
    "DLTR": "دولار تري",
    "TSCO": "تراكتور سابلاي",
    "POOL": "بول كورب",
    "ULTA": "ألتا بيوتي",

    # Small Cap
    "RKLB": "روكيت لاب",
    "ASTS": "أست سبيس موبايل",
    "IONQ": "أيون كيو",
    "JOBY": "جوبي أفييشن",
    "BKSY": "بلاك سكاي",
    "MSTR": "ستراتيجي",
    "UPST": "أبستارت",
    "AFRM": "أفيرم",
    "SOFI": "سوفي",
    "HOOD": "روبن هود",
    "COIN": "كوين بيس",
    "RBLX": "روبلوكس",
    "U": "يونيتي",
    "PATH": "يو آي باث",
    "AI": "سي ثري آي",
    "APP": "أب لوفين",
    "CELH": "سيلسيوس",
    "DUOL": "دولينجو",
    "TOST": "توست",
    "BILL": "بيل هولدنغز",
    "GTLB": "جيت لاب",
    "S": "سينتينيل ون",
    "ESTC": "إيلاستيك",
    "PCOR": "بروكور",
}

# ===== تيليجرام (من Secrets في GitHub، وإلا القيم الاحتياطية) =====
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


# ===== الإعادة التاريخية (غير مستخدمة في التشغيل المجدول) =====
REPLAY_RANGES = None
MAX_REPLAY = 300       # أقصى عدد تنبيهات تُرسل في الإعادة
SEND_CHARTS = True     # إرفاق شارت مع كل تنبيه
CHART_BARS = 500       # عدد الشموع في الشارت البسيط فقط (CHART_STYLE = "simple")
CHART_TEXT = "auto"          # لغة كتابة الشارت: "auto" يكتشف الطريقة الصحيحة تلقائيًا (كولاب/GitHub) | "en" إنجليزي
VOL_MULT = 2                 # شمعة الأحجام: حجم الشمعة ≥ هذا المضاعف × متوسط 20 شمعة (تظهر بالأزرق الداكن)
MARU_BODY = 0.85             # الماربوزو: نسبة الجسم من مدى الشمعة (أخضر كامل للصاعد، أحمر كامل للهابط)

# ===== المتابعة الحية =====
LIVE = True
LIVE_HOURS = 8
CHECK_EVERY_SEC = 120
LIVE_MAX_AGE_MIN = 75
SEND_WATCH = False     # True = إضافة إشارات "ترقب" (لمس المستوى بالذيل قبل اكتمال النموذج)

# ===== جودة التنبيهات (لتقليل العدد) =====
MIN_SCORE = 7              # أقل درجة جودة (من 10) لإرسال التنبيه. ارفعها لتقليل العدد وخفضها لزيادته
LEVEL_COOLDOWN_BARS = 8    # لا نكرر تنبيه على نفس المستوى والفاصل قبل هذا العدد من الشموع (8 شموع × 30د = 4 ساعات)
USE_VOLUME = True          # احتساب حجم التداول في درجة الجودة
TF_PTS = {"1س": 2, "4س": 3, "يومي": 4, "أسبوعي": 5}   # وزن الفريم في الدرجة

# ===== المنطق =====
CHART_INTERVAL = "30m"           # فريم التأكيد (إغلاق الشمعة فوق/تحت المستوى): 15m / 30m / 1h. القمم والقيعان دائمًا من الفريمات الأعلى
ZZ_MULT, ATR_LEN = 3.0, 14       # حساسية ZigZag وفترة ATR
TOL_ATR = 0.8                    # مدى القرب من المستوى (× ATR) لشموع الرفض
RR_TOL_ATR = 0.3                 # مدى لمس المستوى في تبادل الأدوار (× ATR)
RR_HTF_BARS = 20                 # صلاحية المستوى المخترق لتبادل الأدوار (عدد شموع من فريمه)
MAX_CONFIRM = 10                 # أقصى شموع لاكتمال الكسر الوهمي بعد شمعة الكسر
COOLDOWN_BARS = 3                # لا نكرر نفس الرفض/تبادل الأدوار على نفس الفريم قبل هذا العدد من الشموع
WATCH_WICK_ONLY = False          # الترقب فقط عند الكسر بالذيل

PERIODS = {"5m": "60d", "15m": "60d", "30m": "60d", "1h": "730d"}
SECS = {"5m": 300, "15m": 900, "30m": 1800, "1h": 3600}
NAMES = {"5m": "5د", "15m": "15د", "30m": "30د", "1h": "1س"}
HTF = [("1h", "1س", 3600), ("4h", "4س", 14400),
       ("D", "يومي", 86400), ("W", "أسبوعي", 604800)]       # مصادر القمم والقيعان
TF_RANK = {lab: k for k, (_, lab, _) in enumerate(HTF)}


# ===================== البيانات =====================
def load(ticker, interval, period):
    import yfinance as yf
    periods = [period] + (["500d", "365d", "180d"] if interval == "1h" else [])
    df = None
    for p in periods:
        df = yf.download(ticker, interval=interval, period=p,
                         auto_adjust=False, progress=False)
        if df is not None and not df.empty:
            break
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)
    cols = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
    return df[cols].dropna(subset=["open", "high", "low", "close"])


def to_tz(df, tz):
    idx = pd.DatetimeIndex(df.index)
    idx = idx.tz_localize(tz) if idx.tz is None else idx.tz_convert(tz)
    df = df.copy()
    df.index = idx
    df.index.name = "time"
    return df


def market(ticker):
    """(المنطقة الزمنية، دقيقة بداية الجلسة)"""
    return ("Asia/Riyadh", 10 * 60) if ticker.endswith(".SR") else ("America/New_York", 9 * 60 + 30)


AGG = {"open": "first", "high": "max", "low": "min", "close": "last"}


def resample_session(df, minutes, start_min):
    """تجميع شموع حسب بداية الجلسة (يتجنب مشاكل تغيير التوقيت الصيفي)."""
    idx = df.index
    naive = idx.tz_localize(None)
    mins = naive.hour * 60 + naive.minute - start_min
    bucket = np.floor_divide(np.asarray(mins), minutes)
    start = naive.normalize() + pd.to_timedelta(start_min + bucket * minutes, unit="m")
    g = df.groupby(np.asarray(start)).agg(AGG)
    g.index = pd.DatetimeIndex(g.index).tz_localize(idx.tz)
    g.index.name = "time"
    return g


def weekly_from_daily(d, anchor):
    w = d.resample(anchor, closed="right", label="right").agg(AGG).dropna()
    w.index = w.index - pd.Timedelta(days=4)
    return w


# ===================== المؤشرات =====================
def rma(s, n):
    return s.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def atr_series(df, n):
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(),
                    (df["low"] - pc).abs()], axis=1).max(axis=1)
    return rma(tr, n)


# ===================== القمم والقيعان (بالذيول) =====================
def swings(df, mult=ZZ_MULT, atr_len=ATR_LEN, cap=60):
    """ZigZag بالذيول. يرجع: أقرب قمة/قاع غير مكسور (aH,aL) وآخر قمة مخترقة/قاع مكسور (fS,fR)."""
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    atr = atr_series(df, atr_len).values
    hs, hx, ls, lx = [], [], [], []
    direction, ext, fSup, fRes = 0, np.nan, np.nan, np.nan
    n = len(df)
    out = np.full((n, 4), np.nan)
    for i in range(n):
        if np.isnan(ext):
            ext = h[i]
        thr = atr[i] * mult
        bHi = bLo = np.nan
        for k in range(len(hs)):
            if not hx[k] and c[i] > hs[k]:        # الاختراق بالإغلاق
                hx[k] = True
                bHi = hs[k] if np.isnan(bHi) else max(bHi, hs[k])
        for k in range(len(ls)):
            if not lx[k] and c[i] < ls[k]:
                lx[k] = True
                bLo = ls[k] if np.isnan(bLo) else min(bLo, ls[k])
        if not np.isnan(bHi):
            fSup = bHi
        if not np.isnan(bLo):
            fRes = bLo
        if direction <= 0:
            if h[i] >= ext:
                ext = h[i]
            elif l[i] <= ext - thr:
                hs.append(ext); hx.append(False)
                if len(hs) > cap:
                    hs.pop(0); hx.pop(0)
                direction, ext = 1, l[i]
        else:
            if l[i] <= ext:
                ext = l[i]
            elif h[i] >= ext + thr:
                ls.append(ext); lx.append(False)
                if len(ls) > cap:
                    ls.pop(0); lx.pop(0)
                direction, ext = -1, h[i]
        aH = min((p for p, b in zip(hs, hx) if not b), default=np.nan)
        aL = max((p for p, b in zip(ls, lx) if not b), default=np.nan)
        out[i] = (aH, aL, fSup, fRes)
    return pd.DataFrame(out, index=df.index, columns=["aH", "aL", "fS", "fR"])


# ===================== الأحداث =====================
def ev(i, kind, tf, level):
    return {"i": int(i), "kind": kind, "tf": tf, "level": float(level)}


def htf_break_events(df, lv, name):
    c, pc = df["close"], df["close"].shift(1)
    bu = lv["aH"].notna() & (c > lv["aH"]) & (pc <= lv["aH"])
    bd = lv["aL"].notna() & (c < lv["aL"]) & (pc >= lv["aL"])
    out = [ev(i, "اختراق قمة", name, lv["aH"].values[i]) for i in np.flatnonzero(bu.values)]
    out += [ev(i, "كسر قاع", name, lv["aL"].values[i]) for i in np.flatnonzero(bd.values)]
    return out


def fake_events(df, lv, name, rsi_ok):
    """ترقب (لمس المستوى بالذيل أو الإغلاق) ثم اكتمال النموذج بإغلاق خلف شمعة الكسر."""
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    aH, aL = lv["aH"].values, lv["aL"].values
    hp = np.r_[np.nan, h[:-1]]
    lp = np.r_[np.nan, l[:-1]]
    newH = ~np.isnan(aH) & (h > aH) & (hp <= aH)
    newL = ~np.isnan(aL) & (l < aL) & (lp >= aL)
    if WATCH_WICK_ONLY:
        newH &= (c <= aH)
        newL &= (c >= aL)
    out, pendBull, pendBear = [], None, None   # (high, low, bar, level)
    for i in range(len(df)):
        if pendBull is not None and i > pendBull[2]:
            if i - pendBull[2] > MAX_CONFIRM:
                pendBull = None
            elif c[i] > pendBull[0]:
                if rsi_ok[i]:
                    out.append(ev(i, "كسر وهمي صاعد مكتمل", name, pendBull[3]))
                pendBull = None
            elif c[i] < pendBull[1]:
                pendBull = None
        if pendBear is not None and i > pendBear[2]:
            if i - pendBear[2] > MAX_CONFIRM:
                pendBear = None
            elif c[i] < pendBear[1]:
                out.append(ev(i, "كسر وهمي هابط مكتمل", name, pendBear[3]))
                pendBear = None
            elif c[i] > pendBear[0]:
                pendBear = None
        if newH[i]:
            pendBear = (h[i], l[i], i, aH[i])
            out.append(ev(i, "ترقب كسر وهمي هابط", name, aH[i]))
        if newL[i]:
            pendBull = (h[i], l[i], i, aL[i])
            out.append(ev(i, "ترقب كسر وهمي صاعد", name, aL[i]))
    return out


def role_events(df, lv, name, atr, rsi_ok):
    """تبادل الأدوار: إعادة اختبار قمة مخترقة (صارت دعم) أو قاع مكسور (صار مقاومة)."""
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    pc = np.r_[np.nan, c[:-1]]
    fS, fR = lv["fS"].values, lv["fR"].values
    tol = atr * RR_TOL_ATR
    bull = ~np.isnan(fS) & (l <= fS + tol) & (c > o) & (c > fS) & (pc > fS) & rsi_ok
    bear = ~np.isnan(fR) & (h >= fR - tol) & (c < o) & (c < fR) & (pc < fR)
    out = [ev(i, "تبادل أدوار صاعد (دعم)", name, fS[i]) for i in np.flatnonzero(bull)]
    out += [ev(i, "تبادل أدوار هابط (مقاومة)", name, fR[i]) for i in np.flatnonzero(bear)]
    return out


def rejection_events(df, levels, rsi_ok):
    o, h, l, c = (df[x] for x in ("open", "high", "low", "close"))
    body = (c - o).abs()
    upw = h - np.maximum(o, c)
    low_w = np.minimum(o, c) - l
    bull_base = (low_w > body * 1.5) & (low_w > upw * 1.8) & (c > (h + l) / 2)
    bear_base = (upw > body * 1.5) & (upw > low_w * 1.8) & (c < (h + l) / 2)
    tol = atr_series(df, ATR_LEN) * TOL_ATR
    out = []
    for name, lv in levels:
        sAL = lv["aL"].notna() & ((l - lv["aL"]).abs() <= tol) & (c > lv["aL"])
        sFS = lv["fS"].notna() & ((l - lv["fS"]).abs() <= tol) & (c > lv["fS"])
        rAH = lv["aH"].notna() & ((h - lv["aH"]).abs() <= tol) & (c < lv["aH"])
        rFR = lv["fR"].notna() & ((h - lv["fR"]).abs() <= tol) & (c < lv["fR"])
        for i in np.flatnonzero((bull_base & (sAL | sFS)).values):
            if not rsi_ok[i]:
                continue
            if sFS.values[i]:
                out.append(ev(i, "رفض صاعد عند دعم (قمة مخترقة)", name, lv["fS"].values[i]))
            else:
                out.append(ev(i, "رفض صاعد عند قاع", name, lv["aL"].values[i]))
        for i in np.flatnonzero((bear_base & (rAH | rFR)).values):
            if rFR.values[i]:
                out.append(ev(i, "رفض هابط عند مقاومة (قاع مكسور)", name, lv["fR"].values[i]))
            else:
                out.append(ev(i, "رفض هابط عند قمة", name, lv["aH"].values[i]))
    return out


def tidy(events):
    """إزالة التكرار: رفض عند مستوى معكوس إذا وُجد تبادل أدوار بنفس الشمعة والفريم + فترة تهدئة."""
    # إذا وُجد نموذج بنفس الشمعة والفريم والاتجاه والمستوى نحذف الاختراق/الكسر العادي المكرر
    pat_keys = [(e["i"], e["tf"], _is_bull(e["kind"]), e["level"]) for e in events if _is_pattern(e["kind"])]
    events = [e for e in events
              if not (e["kind"] in ("اختراق قمة", "كسر قاع")
                      and any(pi == e["i"] and pt == e["tf"] and pb == _is_bull(e["kind"])
                              and abs(pl - e["level"]) <= 0.003 * e["level"] for pi, pt, pb, pl in pat_keys))]
    role_bull = {(e["i"], e["tf"]) for e in events if e["kind"].startswith("تبادل أدوار صاعد")}
    role_bear = {(e["i"], e["tf"]) for e in events if e["kind"].startswith("تبادل أدوار هابط")}
    out, last = [], {}
    for e in sorted(events, key=lambda x: x["i"]):
        k = e["kind"]
        if k == "رفض صاعد عند دعم (قمة مخترقة)" and (e["i"], e["tf"]) in role_bull:
            continue
        if k == "رفض هابط عند مقاومة (قاع مكسور)" and (e["i"], e["tf"]) in role_bear:
            continue
        if k.startswith(("رفض", "تبادل")):
            key = (k, e["tf"])
            if e["i"] - last.get(key, -999) <= COOLDOWN_BARS:
                continue
            last[key] = e["i"]
        out.append(e)
    # لا نكرر تنبيه على نفس المستوى والفاصل والنوع خلال فترة التهدئة
    res, last2 = [], {}
    for e in out:
        grp = ("break" if e["kind"] in ("اختراق قمة", "كسر قاع")
               else "pattern" if _is_pattern(e["kind"])
               else "fake" if "وهمي" in e["kind"] else "respect")
        key = (e["tf"], round(e["level"], 2), grp)
        if e["i"] - last2.get(key, -999) <= LEVEL_COOLDOWN_BARS:
            continue
        last2[key] = e["i"]
        res.append(e)
    return res


# ===================== النماذج الكلاسيكية =====================
PATTERNS = True            # تفعيل النماذج: قمة/قاع مزدوج، رأس وكتفين (ومقلوب)، قاعدة سعرية
PAT_DT_TOL = 0.6           # القمة/القاع المزدوج: أقصى فرق بين القمتين (× ATR)
PAT_DT_DEPTH = 2.0         # أقل عمق بين القمتين وخط العنق (× ATR)
PAT_HS_HEAD = 0.8          # الرأس أعلى (أو أدنى) من الكتفين بـ (× ATR) على الأقل
PAT_HS_SHOULDER = 1.0      # أقصى فرق بين الكتفين (× ATR)
PAT_NECK_SLOPE = 2.0       # أقصى ميلان لخط العنق: فرق القاعين (× ATR)
PAT_MAX_AGE = 40           # صلاحية النموذج بعد اكتماله (عدد شموع من فريمه)
PAT_BASE = True            # تفعيل القاعدة السعرية (اجعلها False لو كثرت تنبيهاتها)
PAT_BASE_LEN = 20          # القاعدة السعرية: طول النافذة (شموع من فريمها)
PAT_BASE_RANGE = 3.0       # القاعدة السعرية: أقصى مدى (× ATR)
PAT_BASE_TOUCH = 0.35      # القاعدة السعرية: مدى لمس الحد العلوي/السفلي (× ATR)

PATTERN_PREFIXES = ("قمة مزدوجة", "قاع مزدوج", "رأس وكتفين", "اختراق قاعدة", "كسر قاعدة")


def _is_pattern(kind):
    return kind.startswith(PATTERN_PREFIXES)


def pivots(df, mult=ZZ_MULT, atr_len=ATR_LEN):
    """قائمة القمم/القيعان المؤكدة: (النوع H/L، السعر، فهرس الشمعة، فهرس شمعة التأكيد)."""
    h, l = df["high"].values, df["low"].values
    atr = atr_series(df, atr_len).values
    out = []
    direction, ext, ext_i = 0, np.nan, 0
    for i in range(len(df)):
        if np.isnan(ext):
            ext, ext_i = h[i], i
        thr = atr[i] * mult
        if direction <= 0:
            if h[i] >= ext:
                ext, ext_i = h[i], i
            elif l[i] <= ext - thr:
                out.append(("H", ext, ext_i, i))
                direction, ext, ext_i = 1, l[i], i
        else:
            if l[i] <= ext:
                ext, ext_i = l[i], i
            elif h[i] >= ext + thr:
                out.append(("L", ext, ext_i, i))
                direction, ext, ext_i = -1, h[i], i
    return out


def pattern_objects(hdf, label, secs):
    """يبحث عن النماذج في فريم واحد. كل نموذج يبدأ بعد إغلاق شمعة التأكيد (بدون إعادة رسم)."""
    out = []
    pv = pivots(hdf)
    atr = atr_series(hdf, ATR_LEN).values
    idx = hdf.index
    ns = lambda i: int(idx[i].value)
    life = pd.Timedelta(seconds=secs * PAT_MAX_AGE)
    for j in range(len(pv)):
        kind, price, bi, ci = pv[j]
        a = atr[ci]
        if np.isnan(a) or a <= 0:
            continue
        vfrom = idx[ci] + pd.Timedelta(seconds=secs)
        # ---- قمة مزدوجة / قاع مزدوج ----
        if j >= 2 and pv[j - 2][0] == kind and pv[j - 1][0] != kind and 4 <= bi - pv[j - 2][2] <= 80:
            p1, mid, p2 = pv[j - 2][1], pv[j - 1][1], price
            if kind == "H" and abs(p1 - p2) <= PAT_DT_TOL * a and (min(p1, p2) - mid) >= PAT_DT_DEPTH * a:
                out.append(dict(type="neck", name="قمة مزدوجة (كسر خط العنق)", bull=False, tf=label, valid_from=vfrom,
                                until=vfrom + life, inval=max(p1, p2) + 0.5 * a,
                                neck=((ns(pv[j - 2][2]), mid), (ns(bi), mid))))
            if kind == "L" and abs(p1 - p2) <= PAT_DT_TOL * a and (mid - max(p1, p2)) >= PAT_DT_DEPTH * a:
                out.append(dict(type="neck", name="قاع مزدوج (اختراق خط العنق)", bull=True, tf=label, valid_from=vfrom,
                                until=vfrom + life, inval=min(p1, p2) - 0.5 * a,
                                neck=((ns(pv[j - 2][2]), mid), (ns(bi), mid))))
        # ---- رأس وكتفين / مقلوب ----
        if j >= 4 and pv[j - 4][0] == kind and pv[j - 2][0] == kind and pv[j - 3][0] != kind and pv[j - 1][0] != kind:
            ls, n1, hd, n2, rs = pv[j - 4][1], pv[j - 3][1], pv[j - 2][1], pv[j - 1][1], price
            if abs(n1 - n2) <= PAT_NECK_SLOPE * a and abs(ls - rs) <= PAT_HS_SHOULDER * a and bi - pv[j - 4][2] <= 160:
                neck = ((ns(pv[j - 3][2]), n1), (ns(pv[j - 1][2]), n2))
                if kind == "H" and hd - max(ls, rs) >= PAT_HS_HEAD * a:
                    out.append(dict(type="neck", name="رأس وكتفين (كسر خط العنق)", bull=False, tf=label, valid_from=vfrom,
                                    until=vfrom + life, inval=hd + 0.3 * a, neck=neck))
                if kind == "L" and min(ls, rs) - hd >= PAT_HS_HEAD * a:
                    out.append(dict(type="neck", name="رأس وكتفين مقلوب (اختراق خط العنق)", bull=True, tf=label,
                                    valid_from=vfrom, until=vfrom + life, inval=hd - 0.3 * a, neck=neck))
    # ---- القاعدة السعرية (تجميع في نطاق ضيق) ----
    hh, ll = hdf["high"].values, hdf["low"].values
    W = PAT_BASE_LEN
    active = None

    def close_base(b):
        out.append(dict(type="base", tf=label, top=b["top"], bot=b["bot"],
                        valid_from=idx[b["start"]] + pd.Timedelta(seconds=secs),
                        until=idx[b["last"]] + pd.Timedelta(seconds=secs * 4)))

    for j in (range(W, len(hdf)) if PAT_BASE else range(0)):
        a = atr[j]
        if np.isnan(a) or a <= 0:
            continue
        hi, lo = hh[j - W + 1:j + 1].max(), ll[j - W + 1:j + 1].min()
        ok = ((hi - lo) <= PAT_BASE_RANGE * a
              and (hh[j - W + 1:j + 1] >= hi - PAT_BASE_TOUCH * a).sum() >= 2
              and (ll[j - W + 1:j + 1] <= lo + PAT_BASE_TOUCH * a).sum() >= 2)
        if active is not None:
            if ok and hi <= active["top"] + 0.5 * a and lo >= active["bot"] - 0.5 * a:
                active["last"] = j
                continue
            close_base(active)
            active = None
        if ok:
            active = dict(top=hi, bot=lo, start=j, last=j)
    if active is not None:
        close_base(active)
    return out


def _neck_at(neck, t_ns):
    (t1, p1), (t2, p2) = neck
    if t2 == t1:
        return p1
    return p1 + (p2 - p1) * (t_ns - t1) / (t2 - t1)


def pattern_events(df, pats):
    """يحوّل النماذج إلى أحداث: أول إغلاق شمعة التأكيد (30د) خلف خط العنق أو حدود القاعدة."""
    c = df["close"].values
    ns = df.index.as_unit("ns").asi8      # بالنانو ثانية دائمًا (يتفادى اختلاف وحدات pandas)
    n = len(df)
    out = []
    for p in pats:
        s = int(np.searchsorted(ns, p["valid_from"].value))
        if s < 1 or s >= n:
            continue
        end = min(n, int(np.searchsorted(ns, p["until"].value, side="right")))
        if p["type"] == "base":
            if c[s - 1] > p["top"] or c[s - 1] < p["bot"]:
                continue
            for i in range(s, end):
                if c[i] > p["top"]:
                    out.append(ev(i, "اختراق قاعدة سعرية", p["tf"], p["top"]))
                    break
                if c[i] < p["bot"]:
                    out.append(ev(i, "كسر قاعدة سعرية", p["tf"], p["bot"]))
                    break
            continue
        bull, neck = p["bull"], p["neck"]
        nk0 = _neck_at(neck, ns[s - 1])
        if (bull and c[s - 1] > nk0) or ((not bull) and c[s - 1] < nk0):
            continue                                            # انكسر خط العنق قبل اكتمال النموذج
        for i in range(s, end):
            nk = _neck_at(neck, ns[i])
            if bull:
                if c[i] < p["inval"]:
                    break
                if c[i] > nk:
                    e = ev(i, p["name"], p["tf"], nk)
                    e["neck"] = neck
                    out.append(e)
                    break
            else:
                if c[i] > p["inval"]:
                    break
                if c[i] < nk:
                    e = ev(i, p["name"], p["tf"], nk)
                    e["neck"] = neck
                    out.append(e)
                    break
    return out


# ===================== التشغيل على سهم =====================
def marubozu_flags(o, h, l, c):
    """ماربوزو: جسم كبير وذيول صغيرة جدًا."""
    body = np.abs(c - o)
    rng = h - l
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    base = (body > rng * MARU_BODY) & (upper < body * 0.2) & (lower < body * 0.2)
    return base & (c > o), base & (c < o)


def build_levels(df, ticker, loader, tz, sess_start):
    chart_sec = SECS[CHART_INTERVAL]
    src_h, daily, levels, pats = None, None, [], []
    for rule, label, secs in HTF:
        if secs < chart_sec:
            continue
        if rule in ("1h", "4h"):
            if src_h is None:
                hh = loader(ticker, "1h", "730d")
                src_h = to_tz(hh, tz) if hh is not None else (df if chart_sec <= 3600 else None)
            if src_h is None:
                continue
            hdf = resample_session(src_h, 60 if rule == "1h" else 240, sess_start)
        else:
            if daily is None:
                d = loader(ticker, "1d", "5y")
                daily = to_tz(d, tz) if d is not None else None
            if daily is None:
                continue
            hdf = daily if rule == "D" else weekly_from_daily(
                daily, "W-THU" if ticker.endswith(".SR") else "W-FRI")
        lv = swings(hdf).shift(1)                          # آخر شمعة مغلقة فقط (بدون إعادة رسم)
        lv = lv.reindex(df.index, method="ffill")
        # صلاحية المستويات المعكوسة (قمة مخترقة/قاع مكسور) بعد الكسر
        window = pd.Timedelta(seconds=secs * RR_HTF_BARS)
        for col in ("fS", "fR"):
            s = lv[col]
            chg = s.notna() & (s != s.shift(1))
            t_chg = pd.Series(df.index, index=df.index).where(chg).ffill()
            age = pd.Series(df.index, index=df.index) - t_chg
            lv[col] = s.where(age <= window)
        levels.append((label, secs, lv))
        if PATTERNS:
            pats += pattern_objects(hdf, label, secs)
    return levels, pats


def run_symbol(ticker, name, loader=load):
    tz, sess_start = market(ticker)
    raw = loader(ticker, CHART_INTERVAL, PERIODS[CHART_INTERVAL])
    if raw is None or len(raw) < 100:
        print(f"⚠️ لا توجد بيانات كافية لـ {ticker}")
        return None, None
    df = to_tz(raw, tz)
    step = pd.Timedelta(seconds=SECS[CHART_INTERVAL])
    df = df[df.index + step <= pd.Timestamp.now(tz="UTC")].copy()      # بدون الشمعة المفتوحة
    rsi_ok = np.ones(len(df), dtype=bool)      # بدون فلتر RSI
    atr_s = atr_series(df, ATR_LEN)
    atr = atr_s.values
    # أعمدة قياس جودة الشمعة (للدرجة)
    rng_ = (df["high"] - df["low"]).replace(0, np.nan)
    df["_up"] = df["close"] >= df["low"] + 0.7 * rng_
    df["_dn"] = df["close"] <= df["low"] + 0.3 * rng_
    df["_body"] = (df["close"] - df["open"]).abs() / rng_
    if USE_VOLUME and "volume" in df.columns:
        df["_vr"] = df["volume"] / df["volume"].rolling(20).mean().replace(0, np.nan)
    else:
        df["_vr"] = np.nan
    df["_atr"] = atr_s
    mb, mr = marubozu_flags(df["open"].values, df["high"].values, df["low"].values, df["close"].values)
    df["_mb"], df["_mr"] = mb, mr

    levels, pats = build_levels(df, ticker, loader, tz, sess_start)
    events = []
    # أقرب مقاومة ودعم من الفريمات الأعلى (لرسمها في البطاقة)
    cl = df["close"].values
    resA = np.full(len(df), np.nan)
    supA = np.full(len(df), np.nan)
    for _lab, _secs, _lv in levels:
        for col in ("aH", "fR"):
            v = _lv[col].values
            ok = ~np.isnan(v) & (v > cl)
            resA = np.where(ok & (np.isnan(resA) | (v < resA)), v, resA)
        for col in ("aL", "fS"):
            v = _lv[col].values
            ok = ~np.isnan(v) & (v < cl)
            supA = np.where(ok & (np.isnan(supA) | (v > supA)), v, supA)
    df["_res"], df["_sup"] = resA, supA
    for label, secs, lv in levels:
        events += htf_break_events(df, lv, label)
        events += fake_events(df, lv, label, rsi_ok)
        events += role_events(df, lv, label, atr, rsi_ok)
    events += rejection_events(df, [(lab, lv) for lab, _, lv in levels], rsi_ok)
    if PATTERNS:
        events += pattern_events(df, pats)
    return df, tidy(events)


# ===================== التنبيهات =====================
def score_event(df, e):
    i, kind = e["i"], e["kind"]
    bullish = _is_bull(kind)
    pts = TF_PTS.get(e["tf"], 1)                                   # وزن الفريم
    pts += 1 if (df["_up"].values[i] if bullish else df["_dn"].values[i]) else 0   # إغلاق قوي بقرب القمة/القاع
    b = df["_body"].values[i]
    pts += 1 if (not np.isnan(b) and b >= 0.5) else 0              # جسم الشمعة كبير
    vr = df["_vr"].values[i]
    if not np.isnan(vr):
        pts += 2 if vr >= 2.5 else 1 if vr >= 1.5 else 0           # حجم تداول مرتفع
    if kind in ("اختراق قمة", "كسر قاع") or _is_pattern(kind):
        a = df["_atr"].values[i]
        if not np.isnan(a) and abs(df["close"].values[i] - e["level"]) >= 0.25 * a:
            pts += 1                                               # اختراق حاسم وليس بالكاد
    if "مكتمل" in kind or _is_pattern(kind):
        pts += 1                                                   # نموذج مكتمل
    return pts


def build_alerts(df, name, ticker, events):
    step = pd.Timedelta(seconds=SECS[CHART_INTERVAL])
    rows = {}
    for e in events:
        if not SEND_WATCH and e["kind"].startswith("ترقب"):
            continue
        rows.setdefault(e["i"], []).append(e)
    out = []
    for i, evs in sorted(rows.items()):
        evs = sorted(evs, key=lambda e: (TF_RANK.get(e["tf"], 9), e["kind"]))
        score = max(score_event(df, e) for e in evs) + min(2, len({e["tf"] for e in evs}) - 1)   # + تعدد الفريمات
        score = int(min(10, score))
        t = (df.index[i] + step).tz_convert("Asia/Riyadh")      # وقت إغلاق الشمعة بتوقيت السعودية
        out.append({"السهم": name, "الرمز": ticker,
                    "السعر": round(float(df["close"].values[i]), 2),
                    "الوقت (السعودية)": t.strftime("%H:%M"),
                    "التاريخ": t.strftime("%Y-%m-%d"),
                    "_vr": float(df["_vr"].values[i]), "_maru": int(df["_mb"].values[i]) - int(df["_mr"].values[i]),
                    "_score": score, "_t": t, "_i": i, "_dl": df.index[i].strftime("%Y-%m-%d"),
                    "_events": [(e["kind"], e["tf"], e["level"]) for e in evs],
                    "_necks": [e["neck"] for e in evs if "neck" in e]})
    return pd.DataFrame(out)


def format_alert(r):
    lines = [f'{r["السهم"]} ({r["الرمز"]})',
             f'📅 التاريخ: {r["التاريخ"]}',
             f'🕒 الوقت: {r["الوقت (السعودية)"]} (توقيت السعودية)',
             f'💰 السعر: {r["السعر"]}   |   ⏱ إغلاق شمعة {NAMES[CHART_INTERVAL]}',
             f'⭐ الجودة: {r["_score"]}/10']
    if not np.isnan(r["_vr"]) and r["_vr"] >= VOL_MULT:
        lines.append(f'📊 شمعة أحجام عالية (×{r["_vr"]:.1f} من المتوسط)')
    if r["_maru"] != 0:
        lines.append('🕯 شمعة ماربوزو ' + ('صاعدة' if r["_maru"] > 0 else 'هابطة'))
    lines.append('🔔 الحدث:')
    for kind, tf, lvl in r["_events"]:
        lines.append(f'• {kind} | الفاصل: {tf} | المستوى: {lvl:.2f}')
    return "\n".join(lines)


# ===================== الشارت =====================
import re

_AR_RUN = re.compile(r"([\u0600-\u06FF\u0750-\u077F]+)")
_MIRROR = str.maketrans("()[]{}", ")(][}{")

KIND_EN = {
    "اختراق قمة": "High Break", "كسر قاع": "Low Break",
    "ترقب كسر وهمي صاعد": "Bull Fakeout Watch", "ترقب كسر وهمي هابط": "Bear Fakeout Watch",
    "كسر وهمي صاعد مكتمل": "Bull Fakeout Confirmed", "كسر وهمي هابط مكتمل": "Bear Fakeout Confirmed",
    "تبادل أدوار صاعد (دعم)": "Role Reversal (Support)", "تبادل أدوار هابط (مقاومة)": "Role Reversal (Resistance)",
    "رفض صاعد عند دعم (قمة مخترقة)": "Bull Rejection @ Flipped Support",
    "رفض صاعد عند قاع": "Bull Rejection @ Low",
    "رفض هابط عند مقاومة (قاع مكسور)": "Bear Rejection @ Flipped Resistance",
    "رفض هابط عند قمة": "Bear Rejection @ High",
}
TF_EN = {"1س": "1H", "4س": "4H", "يومي": "Daily", "أسبوعي": "Weekly"}


_reshaper = None
_reshaper_failed = False


def _shape(x):
    """تشبيك حروف العربي. إذا المكتبة غير مثبتة يثبتها تلقائيًا."""
    global _reshaper, _reshaper_failed
    if _reshaper is None and not _reshaper_failed:
        try:
            try:
                import arabic_reshaper
            except ImportError:
                import subprocess, sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "arabic-reshaper"])
                import arabic_reshaper
            _reshaper = arabic_reshaper
        except Exception as ex:
            _reshaper_failed = True
            print("⚠️ تعذر تحميل arabic-reshaper، الحروف ستظهر متقطعة:", ex)
    return _reshaper.reshape(x) if _reshaper is not None else x


def _ar_manual(s):
    """ترتيب بصري يدوي للعربي (من اليمين لليسار) لمحركات رسم لا تدعم العربي."""
    words = []
    for w in s.split(" "):
        if _AR_RUN.search(w):
            vis = []
            for p in _AR_RUN.split(w):
                if not p:
                    continue
                vis.append(_shape(p)[::-1] if _AR_RUN.fullmatch(p) else p.translate(_MIRROR))
            words.append("".join(vis[::-1]))
        else:
            words.append(w)
    return " ".join(words[::-1])


def _native_arabic():
    """يفحص فعليًا هل matplotlib يشكّل العربي ويرتّب اتجاهه بنفسه (يختلف بين كولاب وGitHub)."""
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.font_manager import FontProperties
        fig = Figure()
        FigureCanvasAgg(fig)
        r = fig.canvas.get_renderer()
        fp = FontProperties(size=20)

        def w(t):
            return r.get_text_width_height_descent(t, fp, False)[0]

        plain, joined, iso = w("\u0633\u0633\u0633"), w("\uFEB3\uFEB4\uFEB2"), w("\uFEB1\uFEB1\uFEB1")
        return abs(plain - joined) < abs(plain - iso)
    except Exception:
        return False


_native_cache = None


def ar(s):
    global _native_cache
    mode = CHART_TEXT
    if mode == "auto":
        if _native_cache is None:
            _native_cache = _native_arabic()
            print("نمط كتابة العربي في الشارت:", "تلقائي من matplotlib" if _native_cache else "يدوي")
        mode = "ar_native" if _native_cache else "ar_manual"
    if not _AR_RUN.search(s):
        return s
    return s if mode == "ar_native" else _ar_manual(s)


def chart_label(kind, tf, lvl):
    if CHART_TEXT == "en":
        return f"{KIND_EN.get(kind, kind)} | {TF_EN.get(tf, tf)} | {lvl:.2f}"
    return ar(f"{kind} | {tf} | {lvl:.2f}")


def chart_title(name, ticker, t_alert):
    ts = t_alert.strftime("%Y-%m-%d %H:%M")
    if CHART_TEXT == "en":
        return f"{ticker} | {CHART_INTERVAL} candle | {ts} (KSA time)"
    return ar(f"{name} ({ticker}) | شمعة {NAMES[CHART_INTERVAL]} | {ts} (توقيت السعودية)")


def make_chart(df, i, events, name, ticker, t_alert):
    from matplotlib.figure import Figure
    lo = max(0, i - CHART_BARS + 1)
    w = df.iloc[lo:i + 1]
    n = len(w)
    x = np.arange(n)
    o, h, l, c = (w[k].values for k in ("open", "high", "low", "close"))
    mb, mr = marubozu_flags(o, h, l, c)
    vr = w["_vr"].values if "_vr" in w.columns else np.full(n, np.nan)
    hv = np.nan_to_num(vr, nan=0.0) >= VOL_MULT
    face, edge = [], []
    for k_ in range(n):
        if mb[k_]:
            face.append("#16a34a"); edge.append("#16a34a")        # ماربوزو صاعد: أخضر كامل
        elif mr[k_]:
            face.append("#dc2626"); edge.append("#dc2626")        # ماربوزو هابط: أحمر كامل
        elif hv[k_]:
            face.append("#00008B"); edge.append("#00008B")        # شمعة أحجام: أزرق داكن
        elif c[k_] >= o[k_]:
            face.append("#ffffff"); edge.append("#000000")        # شمعة صاعدة: أبيض
        else:
            face.append("#000000"); edge.append("#000000")        # شمعة هابطة: أسود

    fig = Figure(figsize=(10, 6.2), dpi=110)
    ax = fig.add_subplot(111)
    ax.vlines(x, l, h, colors=edge, linewidth=1.1, zorder=2)
    ax.bar(x, np.maximum(np.abs(c - o), (h.max() - l.min()) * 0.002), bottom=np.minimum(o, c),
           width=0.65, color=face, edgecolor=edge, linewidth=0.9, zorder=3)
    ax.axvspan(n - 1.5, n - 0.5, color="#ffd54f", alpha=0.35, zorder=1)

    seen, k = set(), 0
    levels_used = []
    for kind, tf, lvl in events:
        key = (round(lvl, 4), tf)
        if key in seen or k >= 5:
            continue
        seen.add(key)
        bullish = _is_bull(kind)
        color = "#0b6e3a" if bullish else "#b3261e"
        ax.axhline(lvl, color=color, linestyle="--", linewidth=1.6, zorder=4)
        side_right = (k % 2 == 0)
        ax.annotate(chart_label(kind, tf, lvl), xy=(n - 1 if side_right else 0, lvl),
                    xytext=(-4 if side_right else 4, 4), textcoords="offset points",
                    ha="right" if side_right else "left", va="bottom", fontsize=10, color=color,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, alpha=0.9), zorder=6)
        levels_used.append(lvl)
        k += 1

    ymin = min([l.min()] + levels_used)
    ymax = max([h.max()] + levels_used)
    pad = (ymax - ymin) * 0.08 or ymax * 0.01
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_xlim(-1, n + 1)

    idx_r = w.index.tz_convert("Asia/Riyadh")
    ticks = list(range(0, n, max(1, n // 7)))
    ax.set_xticks(ticks)
    ax.set_xticklabels([idx_r[j].strftime("%m/%d\n%H:%M") for j in ticks], fontsize=9)
    ax.yaxis.tick_right()
    ax.grid(True, color="#e6e6e6", linewidth=0.7, zorder=0)
    ax.set_title(chart_title(name, ticker, t_alert), fontsize=12)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    return buf.getvalue()


# ===================== بطاقة التنبيه (تصميم راصد) =====================
BRAND_EN = "RASED"
BRAND_AR = "راصد الفرص الاستثمارية"
BRAND_TAG = "تحليل أعمق .. لقرارات أذكى"
FOOT_LEFT = "مع راصد .. في قلب الفرص"
FOOT_RIGHT = "تحليل احترافي .. لرؤية أوضح للسوق"
CHART_STYLE = "card"        # "card" بطاقة راصد الكاملة | "simple" الشارت البسيط القديم
CARD_BARS = 80              # عدد الشموع في البطاقة
CARD_CANDLES = "color"      # "color" أخضر/أحمر مثل التصميم | "bw" أبيض/أسود مع الماربوزو والحجم بالأزرق الداكن
CARD_SHOW_STOP = True       # إظهار وقف الخسارة المقترح (آلي: خلف المستوى/الشمعة بمقدار STOP_ATR × ATR)
STOP_ATR = 0.5

AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
             "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def _fmt_vol(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "--"
    for d, s in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(v) >= d:
            return f"{v / d:.1f}{s}"
    return f"{v:.0f}"


def _is_bull(kind):
    return ("صاعد" in kind) or kind.startswith(("اختراق", "قاع مزدوج", "رأس وكتفين مقلوب"))


def _callout_text(kind, score):
    strong = score >= 8
    if kind.startswith("قمة مزدوجة"):
        return "نموذج قمة مزدوجة"
    if kind.startswith("قاع مزدوج"):
        return "نموذج قاع مزدوج"
    if kind.startswith("رأس وكتفين مقلوب"):
        return "رأس وكتفين مقلوب"
    if kind.startswith("رأس وكتفين"):
        return "نموذج رأس وكتفين"
    if kind.startswith("اختراق قاعدة"):
        return "اختراق قاعدة سعرية"
    if kind.startswith("كسر قاعدة"):
        return "كسر قاعدة سعرية"
    if kind == "اختراق قمة":
        return "إشارة اختراق قوية" if strong else "إشارة اختراق"
    if kind == "كسر قاع":
        return "إشارة كسر قوية" if strong else "إشارة كسر"
    if "وهمي" in kind:
        return "كسر وهمي مكتمل" if "مكتمل" in kind else "ترقب كسر وهمي"
    if kind.startswith("تبادل أدوار صاعد"):
        return "تبادل أدوار صاعد"
    if kind.startswith("تبادل أدوار هابط"):
        return "تبادل أدوار هابط"
    if kind.startswith("رفض صاعد"):
        return "شمعة رفض صاعدة"
    if kind.startswith("رفض هابط"):
        return "شمعة رفض هابطة"
    return kind


def _summary_text(kind):
    if kind.startswith("قمة مزدوجة"):
        return "كسر خط عنق القمة المزدوجة"
    if kind.startswith("قاع مزدوج"):
        return "اختراق خط عنق القاع المزدوج"
    if kind.startswith("رأس وكتفين مقلوب"):
        return "اختراق خط عنق الرأس والكتفين المقلوب"
    if kind.startswith("رأس وكتفين"):
        return "كسر خط عنق الرأس والكتفين"
    if kind.startswith("اختراق قاعدة"):
        return "اختراق قاعدة سعرية"
    if kind.startswith("كسر قاعدة"):
        return "كسر قاعدة سعرية"
    if kind == "اختراق قمة":
        return "اختراق لمستوى المقاومة"
    if kind == "كسر قاع":
        return "كسر لمستوى الدعم"
    if "وهمي" in kind:
        return "كسر وهمي مكتمل" if "مكتمل" in kind else "ترقب كسر وهمي"
    if kind.startswith("تبادل أدوار صاعد"):
        return "تبادل أدوار: دعم جديد"
    if kind.startswith("تبادل أدوار هابط"):
        return "تبادل أدوار: مقاومة جديدة"
    if kind.startswith("رفض صاعد"):
        return "رفض صاعد عند مستوى"
    if kind.startswith("رفض هابط"):
        return "رفض هابط عند مستوى"
    return kind


def _level_role(kind, c_green, c_red, c_blue):
    if kind.startswith(("قمة مزدوجة", "قاع مزدوج", "رأس وكتفين")):
        return "خط العنق", (c_green if _is_bull(kind) else c_red)
    if kind.startswith("اختراق قاعدة"):
        return "مقاومة", c_red
    if kind.startswith("كسر قاعدة"):
        return "دعم", c_blue
    if kind == "اختراق قمة":
        return "مقاومة", c_red
    if kind == "كسر قاع":
        return "دعم", c_blue
    if kind.startswith("تبادل أدوار صاعد") or "دعم (قمة مخترقة)" in kind:
        return "دعم قوي", c_green
    if kind.startswith("تبادل أدوار هابط") or "مقاومة (قاع مكسور)" in kind:
        return "مقاومة", c_red
    if "صاعد" in kind:
        return "دعم", c_blue
    return "مقاومة", c_red


def make_card(df, i, events, name, ticker, t_alert, score=7, necks=None):
    from matplotlib.figure import Figure
    from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle
    from matplotlib.ticker import FuncFormatter

    W, H = 1536, 1024
    NAVY, NAVY2, GOLD = "#0a1a3a", "#12295a", "#d4a72c"
    GREEN, RED, BLUE, ORANGE, GRAY = "#16a34a", "#e53935", "#1d6fd8", "#f5a623", "#8a94a6"

    fig = Figure(figsize=(W / 100, H / 100), dpi=100, facecolor="white")
    bg = fig.add_axes([0, 0, 1, 1])
    bg.set_xlim(0, W)
    bg.set_ylim(H, 0)
    bg.axis("off")
    bg.set_zorder(10)

    def T(x, y, s, size=22, color="white", ha="center", va="center", bold=False, z=12):
        bg.text(x, y, ar(s), fontsize=size * 0.72, color=color, ha=ha, va=va,
                fontweight="bold" if bold else "normal", zorder=z)

    def RB(x, y, w, h, r=14, fc=NAVY, ec="none", lw=0, z=3):
        bg.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                    fc=fc, ec=ec, lw=lw, zorder=z))

    # ---------------- بيانات الإشارة ----------------
    kinds = [e[0] for e in events]
    main_kind = kinds[-1] if kinds else ""
    bull = _is_bull(main_kind)
    w = df.iloc[max(0, i - CARD_BARS + 1): i + 1]
    n = len(w)
    o, h, l, c = (w[k].values for k in ("open", "high", "low", "close"))
    price = float(c[-1])
    atr = float(df["_atr"].values[i]) if "_atr" in df.columns and not np.isnan(df["_atr"].values[i]) else (h - l).mean()
    t_riy = t_alert.tz_convert("Asia/Riyadh")
    # التغير اليومي: مقارنة بإغلاق آخر يوم تداول سابق
    days = np.array(df.index.date)
    prev_idx = np.flatnonzero(days < days[i])
    prev_close = float(df["close"].values[prev_idx[-1]]) if len(prev_idx) else float(df["close"].values[max(0, i - 1)])
    chg = price - prev_close
    chg_pct = chg / prev_close * 100 if prev_close else 0.0
    chg_col = GREEN if chg >= 0 else RED
    vr = float(df["_vr"].values[i]) if "_vr" in df.columns else np.nan
    ma_full = df["close"].rolling(50).mean()
    ma = ma_full.iloc[max(0, i - CARD_BARS + 1): i + 1].values
    ma_now = float(ma_full.iloc[i]) if not np.isnan(ma_full.iloc[i]) else np.nan
    ma_prev = float(ma_full.iloc[max(0, i - 10)]) if not np.isnan(ma_full.iloc[max(0, i - 10)]) else np.nan
    if not np.isnan(ma_now) and not np.isnan(ma_prev):
        trend = 1 if (price > ma_now and ma_now > ma_prev) else -1 if (price < ma_now and ma_now < ma_prev) else 0
    else:
        trend = 0

    # ---------------- رأس البطاقة ----------------
    bg.add_patch(Rectangle((0, 0), W, 155, fc=NAVY, ec="none", zorder=1))
    bg.add_patch(Rectangle((0, 150), 640, 4, fc=GOLD, ec="none", zorder=2))
    bg.add_patch(Rectangle((900, 150), 636, 4, fc=GOLD, ec="none", zorder=2))
    _logo(bg, 34, 30, 0.82, GOLD)
    bg.text(158, 52, BRAND_EN, fontsize=58 * 0.72, color="white", ha="left", va="center", fontweight="bold", zorder=12)
    T(358, 98, BRAND_AR, 22, "white", ha="right")
    T(358, 128, BRAND_TAG, 21, GOLD, ha="right", bold=True)
    T(690, 64, name, 54 if len(name) <= 8 else 44 if len(name) <= 14 else 36, "white", bold=True)
    bg.text(690, 120, ticker, fontsize=38 * 0.72, color="white", ha="center", va="center", fontweight="bold", zorder=12)
    bg.plot([890, 890], [38, 136], color="#6b7894", lw=1.2, zorder=12)
    RB(1025, 22, 485, 113, 16, NAVY2, "#2a4080", 1.2, 3)
    bg.text(1155, 56, f"{price:.2f}", fontsize=52 * 0.72, color="white", ha="center", va="center", fontweight="bold", zorder=12)
    arrow = "▲" if chg >= 0 else "▼"
    bg.text(1155, 104, f"{chg_pct:+.2f}%  {arrow} {chg:+.2f}", fontsize=26 * 0.72, color=chg_col,
            ha="center", va="center", fontweight="bold", zorder=12)
    bg.plot([1285, 1285], [38, 120], color="#6b7894", lw=1.2, zorder=12)
    T(1440, 46, "آخر تحديث", 24, "white", ha="right", bold=True)
    bg.text(1440, 82, t_riy.strftime("%Y-%m-%d"), fontsize=24 * 0.72, color="white", ha="right", va="center", fontweight="bold", zorder=12)
    bg.text(1440, 114, t_riy.strftime("%H:%M") + " (KSA)", fontsize=22 * 0.72, color="white", ha="right", va="center", zorder=12)
    RB(1456, 34, 30, 28, 5, "none", "white", 1.6, 12)
    bg.plot([1456, 1486], [43, 43], color="white", lw=1.6, zorder=12)
    bg.add_patch(Circle((1471, 108), 13, fc="none", ec="white", lw=1.6, zorder=12))
    bg.plot([1471, 1471, 1478], [100, 108, 111], color="white", lw=1.6, zorder=12)

    # ---------------- الشارت الرئيسي ----------------
    AX0, AX1, AY0, AY1, VY1 = 30, 1440, 168, 598, 715
    ax = fig.add_axes([AX0 / W, 1 - AY1 / H, (AX1 - AX0) / W, (AY1 - AY0) / H])
    axv = fig.add_axes([AX0 / W, 1 - VY1 / H, (AX1 - AX0) / W, (VY1 - 600) / H], sharex=ax)
    ax.set_zorder(1)
    axv.set_zorder(1)
    x = np.arange(n)
    extra = int(n * 0.24) + 3
    xmin, xmax = -1, n - 1 + extra
    ax.set_xlim(xmin, xmax)

    bw = CARD_CANDLES == "bw"
    mb, mr = marubozu_flags(o, h, l, c)
    vrw = w["_vr"].values if "_vr" in w.columns else np.full(n, np.nan)
    hv = np.nan_to_num(vrw, nan=0.0) >= VOL_MULT
    face, edge = [], []
    for k_ in range(n):
        if bw:
            if mb[k_]:
                face.append("#16a34a"); edge.append("#16a34a")
            elif mr[k_]:
                face.append("#dc2626"); edge.append("#dc2626")
            elif hv[k_]:
                face.append("#00008B"); edge.append("#00008B")
            elif c[k_] >= o[k_]:
                face.append("#ffffff"); edge.append("#000000")
            else:
                face.append("#000000"); edge.append("#000000")
        else:
            col_ = "#27a45d" if c[k_] >= o[k_] else "#e8453c"
            face.append(col_); edge.append(col_)
    ax.vlines(x, l, h, colors=edge, linewidth=1.2, zorder=2)
    ax.bar(x, np.maximum(np.abs(c - o), (h.max() - l.min()) * 0.002), bottom=np.minimum(o, c),
           width=0.62, color=face, edgecolor=edge, linewidth=0.9, zorder=3)
    if not np.all(np.isnan(ma)):
        ax.plot(x, ma, color=BLUE, linewidth=1.6, zorder=4)

    # مستويات
    lines, seen = [], []
    for kind, tf, lvl in events:
        if any(abs(lvl - s) <= 0.0015 * lvl for s in seen) or len(lines) >= 3:
            continue
        seen.append(lvl)
        lab, colr = _level_role(kind, GREEN, RED, BLUE)
        lines.append((lvl, lab, colr))
    lo_v, hi_v = float(min(l.min(), np.nanmin(ma) if not np.all(np.isnan(ma)) else l.min())), float(h.max())
    span = hi_v - lo_v
    for col_name, lab, colr in (("_res", "مقاومة", RED), ("_sup", "دعم", BLUE)):
        if col_name in df.columns:
            v = df[col_name].values[i]
            if not np.isnan(v) and lo_v - 0.35 * span <= v <= hi_v + 0.35 * span and \
                    not any(abs(v - s) <= 0.0015 * v for s in seen):
                seen.append(v)
                lines.append((float(v), lab, colr))
    ymin = min([lo_v] + [x_[0] for x_ in lines])
    ymax = max([hi_v] + [x_[0] for x_ in lines])
    pad = (ymax - ymin) * 0.07 or ymax * 0.01
    ymin, ymax = ymin - pad, ymax + pad
    ax.set_ylim(ymin, ymax)

    def ypx(p):
        return AY0 + (ymax - p) / (ymax - ymin) * (AY1 - AY0)

    def xpx(xi):
        return AX0 + (xi - xmin) / (xmax - xmin) * (AX1 - AX0)

    for lvl, lab, colr in lines:
        ax.axhline(lvl, color=colr, linestyle=(0, (6, 4)), linewidth=1.6, zorder=3.5)
    # خط العنق المائل (إن وُجد) يُرسم عبر نافذة الشارت
    w_ns = w.index.as_unit("ns").asi8
    for nk in (necks or []):
        y0, y1 = _neck_at(nk, w_ns[0]), _neck_at(nk, w_ns[-1])
        if abs(y1 - y0) > 1e-9 and ymin <= min(y0, y1) and max(y0, y1) <= ymax:
            ax.plot([0, n - 1], [y0, y1], color=GOLD, linewidth=2.2, linestyle=(0, (5, 3)), zorder=4)
    # وسوم المستويات على اليمين (مع تفادي التداخل)
    order = sorted(range(len(lines)), key=lambda k_: ypx(lines[k_][0]))
    placed = []
    for k_ in order:
        yy = ypx(lines[k_][0])
        for py_ in placed:
            if abs(yy - py_) < 52:
                yy = py_ + 52
        placed.append(yy)
        lvl, lab, colr = lines[k_]
        yy = min(max(yy, AY0 + 28), AY1 - 28)
        RB(1328, yy - 27, 100, 54, 9, colr, "none", 0, 8)
        T(1378, yy - 12, lab, 17, "white", bold=True, z=13)
        bg.text(1378, yy + 11, f"{lvl:.2f}", fontsize=22 * 0.72, color="white", ha="center", va="center",
                fontweight="bold", zorder=13)

    ax.yaxis.tick_right()
    ax.tick_params(axis="y", labelsize=15, length=4)
    ax.tick_params(axis="x", labelbottom=False, length=0)
    ax.grid(True, color="#e9edf3", linewidth=0.8, zorder=0)
    for sp in ax.spines.values():
        sp.set_color("#cfd6e0")

    # تمييز شمعة الإشارة + الشرح
    cx = xpx(n - 1)
    ytop, ybot = ypx(h[-1]), ypx(l[-1])
    bg.add_patch(Rectangle((cx - 16, ytop - 12), 32, ybot - ytop + 24, fc="none", ec=ORANGE, lw=2.4, zorder=11))
    ctext = _callout_text(main_kind, score)
    bx_w = max(220, 14 * len(ctext) + 40)
    bx = max(AX0 + 10, cx - bx_w - 120)
    by = AY0 + 8 if bull else AY1 - 62
    RB(bx, by, bx_w, 48, 14, "#fdecc8", ORANGE, 2, 11)
    T(bx + bx_w / 2, by + 24, ctext, 24, "#8a5a00", bold=True, z=13)
    bg.annotate("", xy=(cx - 16, ytop - 4 if bull else ybot + 4), xytext=(bx + bx_w, by + 24),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.6, connectionstyle="arc3,rad=-0.15"), zorder=11)
    # متوسط 50
    if not np.all(np.isnan(ma)):
        k0 = int(np.nanargmin(np.abs(x - n * 0.42)))
        if not np.isnan(ma[k0]):
            mx, my = xpx(k0), ypx(float(ma[k0]))
            bxm, bym = mx - 80, min(my + 60, AY1 - 70)
            RB(bxm, bym, 190, 46, 22, "white", BLUE, 1.6, 11)
            T(bxm + 95, bym + 23, "متوسط متحرك 50", 21, "#1b2a49", z=13)
            bg.annotate("", xy=(mx, my + 2), xytext=(bxm + 20, bym),
                        arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.4, connectionstyle="arc3,rad=0.3"), zorder=11)

    # ---------------- الحجم ----------------
    vol = w["volume"].values.astype(float) if "volume" in w.columns else np.full(n, np.nan)
    if np.all(np.isnan(vol)) or np.nanmax(vol) <= 0:
        axv.set_ylim(0, 1)
        axv.text(0.5, 0.5, ar("بيانات الحجم غير متوفرة"), transform=axv.transAxes, ha="center", va="center",
                 fontsize=16, color=GRAY)
        axv.set_yticks([])
    else:
        vcol = [("#27a45d" if c[k_] >= o[k_] else "#e8453c") for k_ in range(n)]
        axv.bar(x, np.nan_to_num(vol), width=0.7, color=vcol, alpha=0.9, zorder=3)
        vmax = float(np.nanmax(vol))
        axv.set_ylim(0, vmax * 1.12)
        axv.yaxis.tick_right()
        axv.yaxis.set_major_formatter(FuncFormatter(lambda v, p: _fmt_vol(v)))
        axv.tick_params(axis="y", labelsize=14, length=3)
        axv.set_yticks([vmax * 0.5, vmax])
        vx = xpx(n - 1)
        vtop = 600 + (1 - float(vol[-1]) / (vmax * 1.12)) * (VY1 - 600)
        bg.add_patch(Rectangle((vx - 14, vtop - 6), 28, VY1 - vtop + 6, fc="none", ec=ORANGE, lw=2.2, zorder=11))
        if not np.isnan(vr) and vr >= VOL_MULT:
            RB(vx - 330, 612, 220, 44, 14, "#fdecc8", ORANGE, 2, 11)
            T(vx - 220, 634, "حجم تداول مرتفع", 22, "#8a5a00", bold=True, z=13)
            bg.annotate("", xy=(vx - 16, vtop + 6), xytext=(vx - 110, 634),
                        arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.5), zorder=11)
        RB(1336, 612, 98, 62, 10, NAVY, "none", 0, 8)
        T(1385, 630, "الحجم", 19, "white", z=13)
        bg.text(1385, 658, _fmt_vol(float(vol[-1])), fontsize=24 * 0.72, color="white", ha="center", va="center",
                fontweight="bold", zorder=13)
    axv.grid(True, color="#e9edf3", linewidth=0.8, zorder=0)
    for sp in axv.spines.values():
        sp.set_color("#cfd6e0")
    # تواريخ المحور
    idx_r = w.index.tz_convert("Asia/Riyadh")
    starts = [0] + [k_ for k_ in range(1, n) if idx_r[k_].date() != idx_r[k_ - 1].date()]
    step_ = max(1, int(np.ceil(len(starts) / 5)))
    ticks = starts[::step_]
    axv.set_xticks(ticks)
    axv.set_xticklabels([ar(f"{idx_r[k_].day} {AR_MONTHS[idx_r[k_].month - 1]}") for k_ in ticks],
                        fontsize=15, fontweight="bold")
    axv.tick_params(axis="x", length=3)
    for lab_, k_ in zip(axv.get_xticklabels(), ticks):
        if k_ == 0:
            lab_.set_ha("left")

    # ---------------- البطاقات السفلية ----------------
    PY, PH = 772, 160
    # 1) الملخص الفني
    RB(26, PY, 389, PH, 16, NAVY, "none", 0, 3)
    T(395, PY + 26, "الملخص الفني", 27, GOLD, ha="right", bold=True)
    items = [(_summary_text(main_kind), 1)]
    aligned = (trend == 1 and bull) or (trend == -1 and not bull)
    items.append(("الاتجاه يدعم الإشارة" if aligned else "الاتجاه عرضي" if trend == 0 else "الاتجاه عكس الإشارة",
                  1 if aligned else (0 if trend == 0 else -1)))
    if np.isnan(vr):
        items.append(("لا توجد بيانات حجم", 0))
    else:
        items.append(("حجم تداول قوي" if vr >= VOL_MULT else "حجم تداول عادي", 1 if vr >= VOL_MULT else 0))
    for k_, (txt, st) in enumerate(items):
        yy = PY + 64 + k_ * 36
        T(345, yy, txt, 22, "white", ha="right")
        cc = GREEN if st == 1 else RED if st == -1 else GRAY
        bg.add_patch(Circle((375, yy), 13, fc=cc, ec="none", zorder=12))
        if st == 1:
            bg.plot([368, 373, 382], [yy, yy + 5, yy - 5], color="white", lw=2.4, zorder=13)
        elif st == -1:
            bg.plot([369, 381], [yy - 6, yy + 6], color="white", lw=2.2, zorder=13)
            bg.plot([369, 381], [yy + 6, yy - 6], color="white", lw=2.2, zorder=13)
        else:
            bg.plot([369, 381], [yy, yy], color="white", lw=2.4, zorder=13)

    # 2) جودة الإشارة (مقياس)
    RB(435, PY, 252, PH, 16, NAVY, "none", 0, 3)
    T(561, PY + 26, "جودة الإشارة", 27, "white", bold=True)
    pct = int(round(score * 10))
    cxg, cyg, r_out, r_in = 561, PY + 112, 62, 44
    steps = 40
    cols = [(239, 68, 68), (249, 115, 22), (250, 204, 21), (34, 197, 94)]

    def grad(t):
        pos = t * (len(cols) - 1)
        a_ = min(int(pos), len(cols) - 2)
        f_ = pos - a_
        return tuple((cols[a_][q] * (1 - f_) + cols[a_ + 1][q] * f_) / 255 for q in range(3))
    for s_ in range(steps):
        a1 = np.pi - np.pi * s_ / steps
        a2 = np.pi - np.pi * (s_ + 1) / steps
        pts = [(cxg + r_out * np.cos(a1), cyg - r_out * np.sin(a1)), (cxg + r_out * np.cos(a2), cyg - r_out * np.sin(a2)),
               (cxg + r_in * np.cos(a2), cyg - r_in * np.sin(a2)), (cxg + r_in * np.cos(a1), cyg - r_in * np.sin(a1))]
        lit = (s_ + 0.5) / steps <= pct / 100
        bg.add_patch(Polygon(pts, closed=True, fc=grad((s_ + 0.5) / steps), ec="none", alpha=1.0 if lit else 0.22, zorder=12))
    bg.text(cxg, cyg - 16, f"{pct}%", fontsize=32 * 0.72, color="white", ha="center", va="center", fontweight="bold", zorder=13)
    qlabel = "ممتازة" if score >= 9 else "جيدة جدًا" if score >= 8 else "جيدة" if score >= 7 else "متوسطة"
    qcol = "#22c55e" if score >= 8 else "#facc15" if score >= 7 else "#f97316"
    T(cxg, cyg + 22, qlabel, 25, qcol, bold=True, z=13)

    # 3) قوة الحجم
    RB(705, PY, 253, PH, 16, NAVY, "none", 0, 3)
    T(831, PY + 26, "قوة الحجم", 27, "white", bold=True)
    if np.isnan(vr):
        lit_n, vlabel, vcolr = 0, "غير متوفر", GRAY
    else:
        lit_n = 1 if vr < 0.8 else 2 if vr < 1.2 else 3 if vr < 1.5 else 4 if vr < 2.5 else 5
        vlabel = ["", "ضعيف", "عادي", "جيد", "مرتفع", "مرتفع جدًا"][lit_n]
        vcolr = ["#22c55e", GRAY, GRAY, "#facc15", "#22c55e", "#f97316"][lit_n] if lit_n else GRAY
    for k_ in range(5):
        hh = 14 + k_ * 10
        bx0 = 770 + k_ * 26
        bg.add_patch(Rectangle((bx0, PY + 112 - hh), 20, hh, fc="#22c55e" if k_ < lit_n else "#2f4166", ec="none", zorder=12))
    T(831, PY + 136, vlabel, 24, "#f97316" if lit_n == 5 else "#22c55e" if lit_n >= 3 else GRAY, bold=True, z=13)

    # 4) الاتجاه العام
    RB(974, PY, 221, PH, 16, NAVY, "none", 0, 3)
    T(1084, PY + 26, "الاتجاه العام", 27, "white", bold=True)
    tcol = GREEN if trend == 1 else RED if trend == -1 else GRAY
    base_y = PY + 112
    if trend == 1:
        pts = [(1018, base_y + 6), (1040, base_y - 8), (1062, base_y + 2), (1088, base_y - 26), (1108, base_y - 14), (1146, base_y - 44)]
        tip = pts[-1]
        head = [(tip[0] + 6, tip[1] - 6), (tip[0] - 20, tip[1] - 2), (tip[0] - 2, tip[1] + 18)]
    elif trend == -1:
        pts = [(1018, base_y - 44), (1040, base_y - 28), (1062, base_y - 38), (1088, base_y - 6), (1108, base_y - 18), (1146, base_y + 8)]
        tip = pts[-1]
        head = [(tip[0] + 6, tip[1] + 6), (tip[0] - 20, tip[1] + 2), (tip[0] - 2, tip[1] - 18)]
    else:
        pts = [(1018, base_y - 16), (1044, base_y - 28), (1070, base_y - 8), (1096, base_y - 24), (1122, base_y - 10), (1146, base_y - 20)]
        tip = pts[-1]
        head = [(tip[0] + 8, tip[1]), (tip[0] - 12, tip[1] - 12), (tip[0] - 12, tip[1] + 12)]
    bg.plot([p[0] for p in pts], [p[1] for p in pts], color=tcol, lw=5, solid_capstyle="round", zorder=12)
    bg.add_patch(Polygon(head, closed=True, fc=tcol, ec="none", zorder=12))
    T(1084, PY + 140, "صاعد" if trend == 1 else "هابط" if trend == -1 else "عرضي", 22, tcol, bold=True, z=13)

    # 5) تفاصيل الإشارة
    RB(1221, PY, 289, PH, 16, NAVY, "none", 0, 3)
    T(1470, PY + 26, "تفاصيل الإشارة", 27, "white", ha="right", bold=True)
    lvl0 = lines[0][0] if lines else price
    if bull:
        stop = min(float(l[-1]), lvl0) - STOP_ATR * atr
    else:
        stop = max(float(h[-1]), lvl0) + STOP_ATR * atr
    rows = [("سعر الإشارة", f"{price:.2f}"), ("مستوى الاختراق" if main_kind in ("اختراق قمة", "كسر قاع") else "المستوى", f"{lvl0:.2f}")]
    if CARD_SHOW_STOP:
        rows.append(("وقف الخسارة", f"{stop:.2f}"))
    for k_, (lab, val) in enumerate(rows):
        yy = PY + 72 + k_ * 34
        T(1490, yy, lab + " :", 21, "white", ha="right")
        bg.text(1262, yy, val, fontsize=24 * 0.72, color="white", ha="left", va="center", fontweight="bold", zorder=12)

    # ---------------- التذييل ----------------
    bg.add_patch(Rectangle((0, 948), W, 76, fc=NAVY, ec="none", zorder=1))
    bg.add_patch(Rectangle((0, 946), 560, 3, fc=GOLD, ec="none", zorder=2))
    bg.add_patch(Rectangle((976, 946), 560, 3, fc=GOLD, ec="none", zorder=2))
    bg.plot([38, 84], [989, 989], color=GOLD, lw=2, zorder=12)
    T(450, 989, FOOT_LEFT, 25, GOLD, ha="right", bold=True)
    _logo(bg, 668, 962, 0.55, GOLD)
    bg.text(752, 990, BRAND_EN, fontsize=36 * 0.72, color="white", ha="left", va="center", fontweight="bold", zorder=12)
    T(1430, 989, FOOT_RIGHT, 24, "white", ha="right")
    bg.plot([1445, 1503], [989, 989], color=GOLD, lw=2, zorder=12)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    return buf.getvalue()


def _logo(bg, x, y, s, color):
    """شعار بسيط: ثلاثة أعمدة صاعدة وسهم."""
    from matplotlib.patches import Rectangle, Polygon
    for k_, hh in enumerate((38, 58, 80)):
        bg.add_patch(Rectangle((x + 4 * s + k_ * 26 * s, y + (92 - hh) * s), 18 * s, hh * s, fc=color, ec="none", zorder=12))
    bg.plot([x + 8 * s, x + 50 * s, x + 74 * s, x + 118 * s], [y + 50 * s, y + 34 * s, y + 46 * s, y + 6 * s],
            color=color, lw=5 * s + 1, solid_capstyle="round", zorder=12)
    bg.add_patch(Polygon([(x + 126 * s, y), (x + 100 * s, y + 6 * s), (x + 120 * s, y + 26 * s)], closed=True,
                         fc=color, ec="none", zorder=12))


# ===================== تيليجرام =====================
def _tg(method, data, files=None):
    import requests, time
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    for _ in range(3):
        try:
            r = requests.post(url, data=data, files=files, timeout=40)
        except Exception as ex:
            print("⚠️ خطأ اتصال بتيليجرام:", ex)
            time.sleep(3)
            continue
        if r.ok:
            return True
        if r.status_code == 429:
            time.sleep(r.json().get("parameters", {}).get("retry_after", 5) + 1)
            continue
        print("⚠️ تيليجرام رفض الطلب:", r.status_code, r.text[:200])
        return False
    return False


def send_telegram(text):
    return _tg("sendMessage", {"chat_id": CHAT_ID, "text": text[:4000]})


def send_photo(png, caption):
    return _tg("sendPhoto", {"chat_id": CHAT_ID, "caption": caption[:1000]},
               files={"photo": ("chart.png", png, "image/png")})


def send_alert(r, dfs):
    text = format_alert(r)
    if SEND_CHARTS:
        try:
            if CHART_STYLE == "card":
                try:
                    png = make_card(dfs[r["الرمز"]], r["_i"], r["_events"], r["السهم"], r["الرمز"], r["_t"], r["_score"], r.get("_necks"))
                except Exception as ex_card:
                    print("⚠️ تعذر رسم البطاقة، سيُستخدم الشارت البسيط:", ex_card)
                    png = make_chart(dfs[r["الرمز"]], r["_i"], r["_events"], r["السهم"], r["الرمز"], r["_t"])
            else:
                png = make_chart(dfs[r["الرمز"]], r["_i"], r["_events"], r["السهم"], r["الرمز"], r["_t"])
            if len(text) <= 1000:
                if send_photo(png, text):
                    return True
            elif send_photo(png, f'{r["السهم"]} ({r["الرمز"]}) | {r["التاريخ"]} {r["الوقت (السعودية)"]}'):
                return send_telegram(text)
        except Exception as ex:
            print("⚠️ تعذر رسم الشارت:", ex)
    return send_telegram(text)


# ===================== تحميل مع كاش للبيانات الأطول =====================
_cache = {}


def cached_load(ticker, interval, period):
    import time
    if interval in ("1d", "1h") and period in ("5y", "730d"):
        hit = _cache.get((ticker, interval))
        if hit and time.time() - hit[0] < 1800:
            return hit[1]
        d = load(ticker, interval, period)
        _cache[(ticker, interval)] = (time.time(), d)
        return d
    return load(ticker, interval, period)


def scan_all():
    frames, dfs = [], {}
    for tkr, nm in SYMBOLS.items():
        try:
            df, events = run_symbol(tkr, nm, loader=cached_load)
            if df is None:
                continue
            a = build_alerts(df, nm, tkr, events)
            dfs[tkr] = df
            if not a.empty:
                frames.append(a)
        except Exception as ex:
            print(f"⚠️ خطأ في {tkr}: {ex}")
    if not frames:
        return pd.DataFrame(), dfs
    return pd.concat(frames, ignore_index=True).sort_values("_t").reset_index(drop=True), dfs


def in_replay(r):
    if not REPLAY_RANGES:
        return False
    lo, hi = REPLAY_RANGES["SA" if r["الرمز"].endswith(".SR") else "US"]
    return lo <= r["_dl"] <= hi


def summary_text(sel):
    kinds = pd.Series([k for evs in sel["_events"] for k, _, _ in evs]).value_counts()
    stocks = sel["السهم"].value_counts()
    return ("📊 ملخص الإعادة\nحسب النوع:\n" + "\n".join(f"• {k}: {v}" for k, v in kinds.items())
            + "\n\nحسب السهم:\n" + "\n".join(f"• {k}: {v}" for k, v in stocks.items()))


def main():
    """الوضع القديم (حلقة طويلة). غير مستخدم عندما RUN_ONCE = True."""
    import time
    ok = send_telegram(f"✅ بدأ اختبار المؤشر على {len(SYMBOLS)} أسهم | إشارات على شمعة {NAMES[CHART_INTERVAL]} | "
                       f"قمم وقيعان: 1س/4س/يومي/أسبوعي | التأكيد بإغلاق شمعة {NAMES[CHART_INTERVAL]} | "
                       f"الحساسية {ZZ_MULT} | أقل جودة {MIN_SCORE}/10")
    if not ok:
        print("❌ فشل الإرسال لتيليجرام. تأكد من التوكن ورقم المحادثة، وأنك ضغطت Start في البوت.")
        return
    alerts, dfs = scan_all()
    sent = set()
    if alerts.empty:
        print("لا توجد تنبيهات في البيانات الحالية.")
    else:
        print("توزيع درجات الجودة (كل التنبيهات قبل الفلترة):")
        print(alerts["_score"].value_counts().sort_index().to_string())
        print(f"المقبول (الدرجة ≥ {MIN_SCORE}): {(alerts['_score'] >= MIN_SCORE).sum()} من {len(alerts)}")
        if REPLAY_RANGES:
            good = alerts[alerts["_score"] >= MIN_SCORE]
            sel = good[good.apply(in_replay, axis=1)].tail(MAX_REPLAY) if len(good) else good
            print(f"إعادة {len(sel)} تنبيه...")
            send_telegram(f"🧪 إعادة التنبيهات: السعودي {REPLAY_RANGES['SA'][0]} → {REPLAY_RANGES['SA'][1]} | "
                          f"الأمريكي {REPLAY_RANGES['US'][0]} → {REPLAY_RANGES['US'][1]} ({len(sel)} تنبيه)")
            for _, r in sel.iterrows():
                send_alert(r, dfs)
                time.sleep(1.5)
            if len(sel):
                txt = summary_text(sel)
                print(txt)
                send_telegram(txt)
        sent.update(alerts["الرمز"] + "|" + alerts["_t"].astype(str))

    if not LIVE:
        print("انتهت الإعادة.")
        return
    print(f"🔴 المتابعة الحية تعمل لمدة {LIVE_HOURS} ساعات. أوقفها بزر ■ في كولاب.")
    end = time.time() + LIVE_HOURS * 3600
    try:
        while time.time() < end:
            time.sleep(CHECK_EVERY_SEC)
            alerts, dfs = scan_all()
            if alerts.empty:
                continue
            now = pd.Timestamp.now(tz="UTC")
            for _, r in alerts.iterrows():
                k = f'{r["الرمز"]}|{r["_t"]}'
                if k in sent:
                    continue
                sent.add(k)
                if r["_score"] < MIN_SCORE:
                    continue
                if (now - r["_t"]).total_seconds() / 60 <= LIVE_MAX_AGE_MIN:
                    send_alert(r, dfs)
                    print("📨", r["السهم"], [e[:2] for e in r["_events"]], r["الوقت (السعودية)"])
                    time.sleep(1.5)
    except KeyboardInterrupt:
        print("تم الإيقاف.")


# ===================== وضع الفحص الواحد (للتشغيل المجدول كل 30 دقيقة) =====================
import json

RUN_ONCE = True                  # True = فحص واحد ثم خروج (للتشغيل المجدول). False = الحلقة الطويلة القديمة
STATE_FILE = "sent_state.json"   # يحفظ التنبيهات المرسلة عشان ما تتكرر بين التشغيلات
ONCE_MAX_AGE_MIN = 90            # لا نرسل إلا تنبيهات أحدث من هذا العمر (بالدقايق)
HEARTBEAT = True                 # رسالة "الفاحص شغّال" عند بداية جلسة كل سوق


def _in_session(ticker, now_utc):
    """هل سوق هذا السهم مفتوح الآن (مع 45 دقيقة بعد الإغلاق لالتقاط آخر شمعة)؟"""
    tz, start_min = market(ticker)
    t = now_utc.tz_convert(tz)
    sa = ticker.endswith(".SR")
    day_ok = (t.weekday() in (6, 0, 1, 2, 3)) if sa else (t.weekday() <= 4)   # السعودي: أحد-خميس | الأمريكي: اثنين-جمعة
    end_min = (15 * 60 if sa else 16 * 60) + 45
    mins = t.hour * 60 + t.minute
    return day_ok and start_min <= mins <= end_min


def _load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            st = json.load(f)
        return set(st.get("sent", [])), dict(st.get("hb", {}))
    except Exception:
        return set(), {}


def _save_state(sent, hb):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"sent": sorted(sent)[-6000:], "hb": hb}, f, ensure_ascii=False)


def run_once():
    import time
    global SYMBOLS
    now = pd.Timestamp.now(tz="UTC")
    full = SYMBOLS
    active = {k: v for k, v in full.items() if _in_session(k, now)}
    print(f"الأسهم في الجلسة الآن: {len(active)} من {len(full)}")
    if not active:
        print("لا يوجد سوق مفتوح الآن. انتهى.")
        return
    sent, hb = _load_state()

    if HEARTBEAT:
        for mk, label, tz in (("SA", "السعودي", "Asia/Riyadh"), ("US", "الأمريكي", "America/New_York")):
            n_mk = sum(1 for k in active if k.endswith(".SR") == (mk == "SA"))
            today = now.tz_convert(tz).strftime("%Y-%m-%d")
            if n_mk and hb.get(mk) != today:
                send_telegram(f"🟢 الفاحص شغّال: بدأت جلسة السوق {label} ({n_mk} سهم) | {today}")
                hb[mk] = today

    SYMBOLS = active
    try:
        alerts, dfs = scan_all()
    except Exception as ex:
        send_telegram(f"⚠️ خطأ في الفحص: {ex}")
        raise
    finally:
        SYMBOLS = full

    n_sent = 0
    if not alerts.empty:
        for _, r in alerts.iterrows():
            k = f'{r["الرمز"]}|{r["_t"]}'
            if k in sent:
                continue
            sent.add(k)
            age = (now - r["_t"]).total_seconds() / 60
            if r["_score"] >= MIN_SCORE and age <= ONCE_MAX_AGE_MIN:
                send_alert(r, dfs)
                n_sent += 1
                print("📨", r["السهم"], [e[:2] for e in r["_events"]], r["الوقت (السعودية)"])
                time.sleep(1.5)
    _save_state(sent, hb)
    print(f"تم الفحص. تنبيهات مرسلة: {n_sent}")


if RUN_ONCE:
    run_once()
else:
    main()
