"""Round 4: Wayback Machine snapshots of Airbnb room pages (bypass 429s)."""
import re, time, sys, hashlib
from collections import OrderedDict
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "tools" / "staging"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
SKIP = ("PlatformAssets", "platform-assets", "Favicons", "favicon", "search-bar-icons")
IDS = {
 "stay-03-latoda-treehouse": "870845191119280619",
 "stay-04-wayward-inn": "13870520",
 "stay-05-tandi-cottage": "915183568372443289",
 "stay-08-om-homestay": "786455009119525173",
 "stay-09-serenity-wooden": "51914594",
 "stay-15-riverside-serenity": "1279706273527651930",
 "stay-16-cedar-nest-sainj": "853189955208971108",
}

def snapshot(s, lid):
    for domain in ("airbnb.co.in", "airbnb.com"):
        try:
            r = s.get("https://archive.org/wayback/available",
                      params={"url": f"{domain}/rooms/{lid}"}, timeout=30).json()
            snap = (r.get("archived_snapshots") or {}).get("closest") or {}
            if snap.get("available") and int(snap.get("status", "0")) == 200:
                return snap["url"]
        except Exception:
            pass
    return None

def grab(s, slug, urls, cap=8):
    dest = OUT / slug; dest.mkdir(parents=True, exist_ok=True)
    have = len(list(dest.glob("raw-*.jpg")))
    seen, n = set(), 0
    for u in urls:
        if n >= cap:
            break
        for src in (u, u.replace("https://a0.muscache.com", "https://web.archive.org", 1) if False else u):
            try:
                dl = src + ("&im_w=1440" if "muscache" in src and "im_w" not in src else "")
                r = s.get(dl, timeout=40)
                if r.status_code != 200 or len(r.content) < 15000:
                    continue
                h = hashlib.md5(r.content).hexdigest()
                if h in seen:
                    continue
                seen.add(h)
                (dest / f"raw-{have+n:02d}.jpg").write_bytes(r.content)
                n += 1
                break
            except Exception:
                continue
    print(f"{slug}: +{n} (total now {have+n})", flush=True)

def main():
    s = requests.Session(); s.headers.update(UA)
    for slug, lid in IDS.items():
        have = len(list((OUT / slug).glob("raw-*.jpg"))) if (OUT / slug).exists() else 0
        if have >= 4:
            print(f"{slug}: already has {have}, skip"); continue
        try:
            snap = snapshot(s, lid)
            print(f"{slug}: snapshot -> {snap}")
            if not snap:
                continue
            html = s.get(snap, timeout=60).text
            allimgs = list(OrderedDict.fromkeys(
                re.findall(r"https?://a0\.muscache\.com/im/pictures/[A-Za-z0-9/._%~-]+?\.(?:jpe?g|png|webp)", html)))
            if not allimgs:  # archived rewrites -> web.archive.org URLs
                allimgs = list(OrderedDict.fromkeys(
                    re.findall(r"https?://web\.archive\.org[^\"' ]*muscache[^\"' ]*?\.(?:jpe?g|png|webp)", html)))
            urls = [u for u in allimgs if not any(k in u for k in SKIP)]
            print(f"{slug}: {len(urls)} candidate imgs")
            grab(s, slug, urls, cap=8)
        except Exception as e:
            print(f"{slug}: FAIL {str(e)[:120]}")
        time.sleep(6)

if __name__ == "__main__":
    sys.exit(main())
