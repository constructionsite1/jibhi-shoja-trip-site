import requests, re, sys
from collections import OrderedDict
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
s = requests.Session(); s.headers.update(UA)
for name, eid in [("moustache", "ChoI9ff7z_SOqOn8ARoNL2cvMTF2eTlsMHJwdxAB"),
                  ("riverview", "ChoIzdz_5I62_pTLARoNL2cvMTFkenRzMWszehAB")]:
    try:
        r = s.get(f"https://www.google.com/travel/hotels/entity/{eid}", timeout=40)
        print(name, r.status_code, len(r.text))
        g = list(OrderedDict.fromkeys(re.findall(r"https://lh3\.googleusercontent\.com/[A-Za-z0-9/_\-=]+", r.text)))
        # drop icons/avatars
        g = [u for u in g if "default-user" not in u and "favicon" not in u]
        print("  gphotos:", len(g))
        out = Path_out = None
    except Exception as e:
        print(name, "FAIL", str(e)[:120])
