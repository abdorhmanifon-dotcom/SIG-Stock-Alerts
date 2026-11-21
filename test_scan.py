import os
import time

TEST_N = int(os.environ.get("TEST_N") or "20")                 # عدد الأسهم المفحوصة (نصفها سعودي ونصفها أمريكي)
SEND_LAST = int(os.environ.get("SEND_LAST") or "3")            # عدد آخر التنبيهات العامة المرسلة كعينة
SEND_PATTERNS = int(os.environ.get("SEND_PATTERNS") or "2")    # عدد آخر التنبيهات اللي فيها نموذج

# نحمّل scanner.py بدون تشغيل الفحص التلقائي في آخره
src = open("scanner.py", encoding="utf-8").read().rsplit("\nif RUN_ONCE:", 1)[0]
g = {"__name__": "scanner_test"}
exec(compile(src, "scanner.py", "exec"), g)

sa = [(k, v) for k, v in g["SYMBOLS"].items() if k.endswith(".SR")][: TEST_N // 2]
us = [(k, v) for k, v in g["SYMBOLS"].items() if not k.endswith(".SR")][: TEST_N - len(sa)]
g["SYMBOLS"] = dict(sa + us)

g["send_telegram"](f"🧪 اختبار بدون انتظار السوق: فحص {len(g['SYMBOLS'])} سهم وإرسال عينة من آخر التنبيهات")
t0 = time.time()
alerts, dfs = g["scan_all"]()
print(f"انتهى الفحص خلال {time.time() - t0:.0f} ثانية | أسهم لها بيانات: {len(dfs)} من {len(g['SYMBOLS'])}")

if alerts.empty:
    g["send_telegram"]("🧪 الفحص اشتغل لكن ما لقيت أي تنبيه في بيانات هذي الأسهم.")
    raise SystemExit

is_pat = alerts["_events"].apply(lambda evs: any(g["_is_pattern"](k) for k, _, _ in evs))
good = alerts[alerts["_score"] >= g["MIN_SCORE"]]
pick = list(good.tail(SEND_LAST).index) + list(alerts[is_pat].tail(SEND_PATTERNS).index)
if not pick:
    pick = list(alerts.tail(SEND_LAST).index)
pick = list(dict.fromkeys(pick))

print(f"إجمالي التنبيهات: {len(alerts)} | مقبولة (≥{g['MIN_SCORE']}): {len(good)} | فيها نماذج: {int(is_pat.sum())}")
g["send_telegram"](f"🧪 عينة من آخر التنبيهات ({len(pick)}) | إجمالي ما لقيته: {len(alerts)} | "
                   f"فوق حد الجودة: {len(good)} | فيها نماذج: {int(is_pat.sum())}")
for k in pick:
    g["send_alert"](alerts.loc[k], dfs)
    time.sleep(1.5)
print("تم إرسال العينة.")
