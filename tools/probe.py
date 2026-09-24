import requests, re, sys
from collections import OrderedDict
h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
urls = {
 "moustache_hw": "https://www.hostelworld.com/hostels/p/327261/moustache-shoja-jibhi/",
 "zostel": "https://www.zostel.com/zostel/shoja/",
 "cedar_linktr": "https://linktr.ee/himalayancedarnest",
}
s = requests.Session(); s.headers.update(h)
for k, u in urls.items():
    try:
        r = s.get(u, timeout=30)
        pat = r"https?://[A-Za-z0-9/._%~:?&=+#-]+\.(?:jpe?g|png|webp)"
        imgs = list(OrderedDict.fromkeys(re.findall(pat, r.text)))
        print("=====", k, r.status_code, len(r.text), "imgs:", len(imgs))
        for x in imgs[:8]:
            print("   ", x[:130])
        ab = list(OrderedDict.fromkeys(re.findall(r"airbnb\S{0,80}", r.text)))[:4]
        print("    airbnb refs:", ab)
    except Exception as e:
        print("=====", k, "FAIL", e)
