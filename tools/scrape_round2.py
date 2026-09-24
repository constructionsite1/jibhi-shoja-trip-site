"""Round 2: remaining Airbnb IDs + official/direct sites. Saves candidates to
site/tools/staging/<slug>/raw-NN.jpg (up to 8). Human selects final 4 after."""
import re, time, sys, hashlib
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urljoin
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "tools" / "staging"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

AIRBNB_NEW = {
 "stay-03-latoda-treehouse": "870845191119280619",
 "stay-04-wayward-inn": "13870520",
 "stay-05-tandi-cottage": "915183568372443289",
 "stay-08-om-homestay": "786455009119525173",
 "stay-09-serenity-wooden": "51914594",
 "stay-15-riverside-serenity": "1279706273527651930",
 "stay-16-cedar-nest-sainj": "853189955208971108",
}
# slug -> (page url, url-substring filter to keep only property images)
DIRECT = {
 "stay-11-silence-pines": ("https://www.homestaysofindia.com/himachal-banjar-jibhi-silence-of-pines", None),
 "stay-12-moustache-shoja": ("https://www.expedia.com/Banjar-Hotels-Moustache-Shoja.h106070996.Hotel-Information", "trvl-media"),
 "stay-13-zostel-shoja": ("https://www.zostel.com/zostel/shoja/", "gallery"),
 "stay-14-tirthan-crest": ("https://www.booking.com/hotel/in/tirthan-bnb-jibhi-at-banjar-near-bus-stand.html", "bstatic"),
 "stay-17-mountain-nest": ("https://mountainneststay.com/", None),
 "stay-18-tirthan-riverview": ("https://tirthanriverviewhomestay.bookmystay.io/", None),
 "stay-19-jaabal-riverside": ("https://tirthanjaabalhomestay.com/", None),
 "stay-20-mizuki-retreat": ("https://mizukiretreat.com/", None),
}
SKIP = ("favicon", "logo", "sprite", "emoji", "icon", "placeholder", "avatar", "payment", "badge")

def airbnb_urls(s, lid):
    r = s.get(f"https://www.airbnb.co.in/rooms/{lid}", timeout=30)
    r.raise_for_status()
    allimgs = list(OrderedDict.fromkeys(
        re.findall(r"https://a0\.muscache\.com/im/pictures/[A-Za-z0-9/._%~-]+?\.(?:jpe?g|png|webp)", r.text)))
    own = [u for u in allimgs if lid in u]
    seen, out = set(), []
    for u in own:
        key = u.split("/")[-1].split("?")[0].lower()
        if key not in seen:
            seen.add(key); out.append(u)
    return out

def page_images(s, url, keep=None):
    r = s.get(url, timeout=30)
    r.raise_for_status()
    html = r.text
    found = []
    m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
    if m:
        found.append(m.group(1))
    for m in re.finditer(r"<img[^>]+src=\"([^\"]+)\"", html):
        found.append(m.group(1))
    urls = []
    for u in found:
        u = urljoin(url, u.split(" ")[0])
        if not u.startswith("http"):
            continue
        low = u.lower()
        if any(k in low for k in SKIP):
            continue
        if keep and keep not in low:
            continue
        urls.append(u)
    return list(OrderedDict.fromkeys(urls))

def grab(s, slug, urls, cap=8):
    dest = OUT / slug; dest.mkdir(parents=True, exist_ok=True)
    seen_hash, n = set(), 0
    for u in urls:
        if n >= cap:
            break
        try:
            dl = u + ("&im_w=1440" if "muscache" in u and "im_w" not in u else "")
            r = s.get(dl or u, timeout=40)
            if r.status_code != 200 or len(r.content) < 15000:
                continue
            h = hashlib.md5(r.content).hexdigest()
            if h in seen_hash:
                continue
            seen_hash.add(h)
            (dest / f"raw-{n:02d}.jpg").write_bytes(r.content)
            n += 1
        except Exception as e:
            print(f"  {slug}: IMG FAIL {str(e)[:80]}")
    print(f"{slug}: saved {n}")
    return n

def main():
    s = requests.Session(); s.headers.update(UA)
    for slug, lid in AIRBNB_NEW.items():
        try:
            grab(s, slug, airbnb_urls(s, lid), cap=6)
        except Exception as e:
            print(f"{slug}: PAGE FAIL {str(e)[:100]}")
        time.sleep(5)
    for slug, (url, keep) in DIRECT.items():
        try:
            grab(s, slug, page_images(s, url, keep), cap=8)
        except Exception as e:
            print(f"{slug}: PAGE FAIL {str(e)[:100]}")
        time.sleep(4)

if __name__ == "__main__":
    sys.exit(main())
