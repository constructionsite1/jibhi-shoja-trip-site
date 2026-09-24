"""Round 3: retry Airbnb with asset-tolerant filter + Booking/TripAdvisor attempts."""
import re, time, sys, hashlib
from collections import OrderedDict
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "tools" / "staging"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
SKIP = ("PlatformAssets", "platform-assets", "Favicons", "favicon", "search-bar-icons")

AIRBNB = {
 "stay-03-latoda-treehouse": "870845191119280619",
 "stay-04-wayward-inn": "13870520",
 "stay-05-tandi-cottage": "915183568372443289",
 "stay-08-om-homestay": "786455009119525173",
 "stay-09-serenity-wooden": "51914594",
 "stay-15-riverside-serenity": "1279706273527651930",
 "stay-16-cedar-nest-sainj": "853189955208971108",
}
EXTRA = {
 "stay-12-moustache-shoja": [
    "https://www.booking.com/hotel/in/moustache-shoja.html",
    "https://www.tripadvisor.in/Hotel_Review-g3389564-d28002610-Reviews-Moustache_Shoja-Banjar_Kullu_District_Himachal_Pradesh.html",
 ],
 "stay-14-tirthan-crest": [
    "https://www.booking.com/hotel/in/tirthan-bnb-jibhi-at-banjar-near-bus-stand.html",
 ],
}

def muscache_listing(html, lid):
    allimgs = list(OrderedDict.fromkeys(
        re.findall(r"https://a0\.muscache\.com/im/pictures/[A-Za-z0-9/._%~-]+?\.(?:jpe?g|png|webp)", html)))
    out = []
    for u in allimgs:
        if any(k in u for k in SKIP):
            continue
        if lid in u or "/im/pictures/miso/" in u or re.search(r"/im/pictures/[0-9a-f-]{36}\.(?:jpe?g)", u):
            out.append(u)
    return out

def generic_imgs(html):
    pat = r"https?://[A-Za-z0-9/._%~:?&=+#-]+\.(?:jpe?g|png|webp)"
    return [u for u in OrderedDict.fromkeys(re.findall(pat, html))
            if "bstatic" in u or "tripadvisor" in u or "media-cdn" in u]

def grab(s, slug, urls, cap=8):
    dest = OUT / slug; dest.mkdir(parents=True, exist_ok=True)
    have = len(list(dest.glob("raw-*.jpg")))
    seen, n = set(), 0
    for u in urls:
        if n >= cap:
            break
        try:
            dl = u + ("&im_w=1440" if "muscache" in u and "im_w" not in u else "")
            r = s.get(dl or u, timeout=40)
            if r.status_code != 200 or len(r.content) < 15000:
                continue
            h = hashlib.md5(r.content).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            (dest / f"raw-{have+n:02d}.jpg").write_bytes(r.content)
            n += 1
        except Exception as e:
            print(f"  {slug}: IMG FAIL {str(e)[:70]}")
    print(f"{slug}: +{n} (total now {have+n})")
    return n

def main():
    s = requests.Session(); s.headers.update(UA)
    for slug, lid in AIRBNB.items():
        try:
            r = s.get(f"https://www.airbnb.co.in/rooms/{lid}", timeout=30)
            if r.status_code == 429:
                print(f"{slug}: 429, cooling 150s"); time.sleep(150)
                r = s.get(f"https://www.airbnb.co.in/rooms/{lid}", timeout=30)
            r.raise_for_status()
            grab(s, slug, muscache_listing(r.text, lid), cap=6)
        except Exception as e:
            print(f"{slug}: PAGE FAIL {str(e)[:100]}")
        time.sleep(9)
    for slug, urls in EXTRA.items():
        for u in urls:
            try:
                r = s.get(u, timeout=30)
                print(slug, u[:60], r.status_code, len(r.text))
                if r.status_code == 200:
                    grab(s, slug, generic_imgs(r.text), cap=8)
            except Exception as e:
                print(f"{slug}: PAGE FAIL {str(e)[:100]}")
            time.sleep(6)

if __name__ == "__main__":
    sys.exit(main())
