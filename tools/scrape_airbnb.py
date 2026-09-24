"""Scrape real listing photos from Airbnb room pages.
Usage: python site/tools/scrape_airbnb.py
Output: site/tools/staging/<slug>/raw-NN.jpg (up to 6 unique per listing)."""
import re, time, sys
from collections import OrderedDict
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "tools" / "staging"

AIRBNB = {
 "stay-01-moonlight-view": "52829977",
 "stay-02-whispering-pines": "26117817",
 "stay-06-mudhouse-peaks": "1412122997309117906",
 "stay-07-lost-escape": "758357609524923692",
 "stay-10-hillhouse-aframe": "1583118387367694595",
 "stay-15-riverside-serenity": "1279706273527651930",
 "stay-21-forest-lens": "1438153001249315575",
 "stay-22-rocky-retreat": "1146687534659285703",
}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

def listing_photos(s, lid):
    r = s.get(f"https://www.airbnb.co.in/rooms/{lid}", timeout=30)
    r.raise_for_status()
    allimgs = list(OrderedDict.fromkeys(
        re.findall(r"https://a0\.muscache\.com/im/pictures/[A-Za-z0-9/\.\-_%]+?\.(?:jpe?g|png|webp)", r.text)))
    # only this listing's own photos
    own = [u for u in allimgs if f"Hosting-{lid}" in u or f"Hosting%3A{lid}" in u or f"hosting/Hosting-" in u]
    if not own:  # fallback: miso/Hosting-<id> pattern variants
        own = [u for u in allimgs if lid in u]
    # dedupe by photo uuid (last path segment), drop tiny UI assets by preferring miso/original
    seen, out = set(), []
    for u in own:
        key = u.split("/")[-1].split("?")[0].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(u)
    return out

def main():
    s = requests.Session(); s.headers.update(UA)
    total = 0
    for slug, lid in AIRBNB.items():
        dest = OUT / slug; dest.mkdir(parents=True, exist_ok=True)
        try:
            urls = listing_photos(s, lid)[:6]
        except Exception as e:
            print(f"{slug}: PAGE FAIL {e}"); continue
        n = 0
        for u in urls:
            try:
                dl = u + ("&" if "?" in u else "?") + "im_w=1440"
                r = s.get(dl, timeout=40)
                if r.status_code != 200 or len(r.content) < 15000:
                    continue
                (dest / f"raw-{n:02d}.jpg").write_bytes(r.content)
                n += 1; total += 1
                if n == 6:
                    break
            except Exception as e:
                print(f"{slug}: IMG FAIL {e}")
        print(f"{slug}: saved {n}")
        time.sleep(2)
    print(f"TOTAL {total}")

if __name__ == "__main__":
    sys.exit(main())
