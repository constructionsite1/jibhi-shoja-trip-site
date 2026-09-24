import requests, re
from collections import OrderedDict
h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
s = requests.Session(); s.headers.update(h)

# 1. why did stay-04 save 0?
r = s.get("https://www.airbnb.co.in/rooms/13870520", timeout=30)
print("wayward:", r.status_code, len(r.text), "has-id:", "13870520" in r.text)

# 2. alternates
tests = {
 "riverview_main": "https://www.tirthanriverviewhomestay.com/",
 "homestays_tirthan": "https://www.homestays.co.in/tirthan-india",
 "moustache_official": "https://moustachescapes.com/stay/moustache-hostel-shoja",
}
for k, u in tests.items():
    try:
        r = s.get(u, timeout=30)
        pat = r"https?://[A-Za-z0-9/._%~:?&=+#-]+\.(?:jpe?g|png|webp)"
        imgs = list(OrderedDict.fromkeys(re.findall(pat, r.text)))
        print("=====", k, r.status_code, len(r.text), "imgs:", len(imgs))
        for x in imgs[:6]:
            print("   ", x[:130])
    except Exception as e:
        print("=====", k, "FAIL", str(e)[:100])
