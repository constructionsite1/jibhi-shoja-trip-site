import requests, re
from collections import OrderedDict
u = "https://r.jina.ai/https://www.airbnb.co.in/rooms/13870520"
r = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=90)
print("status:", r.status_code, "bytes:", len(r.text))
pat = r"https://a0\.muscache\.com/im/pictures/[A-Za-z0-9/._%~-]+"
imgs = list(OrderedDict.fromkeys(re.findall(pat, r.text)))
print("muscache:", len(imgs))
for x in imgs[:12]:
    print("   ", x[:150])
