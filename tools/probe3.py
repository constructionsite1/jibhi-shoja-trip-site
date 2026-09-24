import requests, re
from collections import OrderedDict
h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
s = requests.Session(); s.headers.update(h)

r = s.get("https://www.airbnb.co.in/rooms/13870520", timeout=30)
pat = r"https://a0\.muscache\.com/im/pictures/[A-Za-z0-9/._%~-]+?\.(?:jpe?g|png|webp)"
imgs = list(OrderedDict.fromkeys(re.findall(pat, r.text)))
print("wayward muscache total:", len(imgs))
for x in imgs[:12]:
    print("   ", x[:150])

print("===== bookmystay =====")
r = s.get("https://tirthanriverviewhomestay.bookmystay.io/", timeout=30)
print("status", r.status_code, len(r.text))
pat2 = r"https?://[A-Za-z0-9/._%~:?&=+#-]+\.(?:jpe?g|png|webp)"
imgs = list(OrderedDict.fromkeys(re.findall(pat2, r.text)))[:15]
for x in imgs:
    print("   ", x[:150])

print("===== moustache stay index =====")
r = s.get("https://moustachescapes.com/stay/", timeout=30)
print("status", r.status_code, len(r.text))
for m in OrderedDict.fromkeys(re.findall(r"href=\"([^\"]*[Ss]hoja[^\"]*)\"", r.text)):
    print("   ", m[:150])

print("===== homestays tirthan crest href =====")
r = s.get("https://www.homestays.co.in/tirthan-india", timeout=30)
for m in OrderedDict.fromkeys(re.findall(r"href=\"([^\"]*[Cc]rest[^\"]*)\"", r.text)):
    print("   ", m[:200])
