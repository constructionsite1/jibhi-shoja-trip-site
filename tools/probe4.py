import requests, re, json
from collections import OrderedDict
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
s = requests.Session(); s.headers.update(UA)

print("===== 1. airbnb public api =====")
try:
    r = s.get("https://api.airbnb.com/v2/listings/13870520",
              params={"_format": "for_p3", "key": "d306zoyjsyarp7ifhu67rjxn52tv0t20"}, timeout=30)
    print("status", r.status_code, len(r.content))
    if r.status_code == 200:
        d = r.json()
        ph = d.get("listing", {}).get("photos") or []
        print("photos:", len(ph))
        for p in ph[:4]:
            print("   ", str(p.get("large_url") or p.get("x_large_url"))[:130])
    else:
        print(r.text[:200])
except Exception as e:
    print("FAIL", str(e)[:120])

print("===== 2. booking 202 body =====")
try:
    r = s.get("https://www.booking.com/hotel/in/moustache-shoja.html", timeout=30)
    print("status", r.status_code, len(r.text))
    print(r.text[:400])
except Exception as e:
    print("FAIL", str(e)[:120])

print("===== 3. google hotels riverview =====")
try:
    r = s.get("https://www.google.com/travel/hotels/entity/ChoIzdz_5I62_pTLARoNL2cvMTFkenRzMWszehAB",
              headers={**UA, "Accept-Language": "en-US,en;q=0.9"}, timeout=30)
    print("status", r.status_code, len(r.text))
    g = list(OrderedDict.fromkeys(re.findall(r"https://lh3\.googleusercontent\.com/[^\"' )]+", r.text)))
    print("gphotos:", len(g))
    for x in g[:8]:
        print("   ", x[:150])
except Exception as e:
    print("FAIL", str(e)[:120])

print("===== 4. hygge latoda =====")
try:
    r = s.get("https://www.hyggecottages.com/cottages/latoda-the-tree-cottage-jibhi/", timeout=30)
    print("status", r.status_code, len(r.text))
    pat = r"https?://[A-Za-z0-9/._%~:?&=+#-]+\.(?:jpe?g|png|webp)"
    imgs = [u for u in OrderedDict.fromkeys(re.findall(pat, r.text)) if "hygge" in u.lower() or "upload" in u.lower() or "wp-content" in u.lower()]
    print("imgs:", len(imgs))
    for x in imgs[:8]:
        print("   ", x[:150])
except Exception as e:
    print("FAIL", str(e)[:120])
