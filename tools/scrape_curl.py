"""Round 5: fetch Airbnb room pages via curl.exe (real TLS fingerprint)."""
import re, subprocess, sys, hashlib, time
from collections import OrderedDict
from pathlib import Path
import requests as rq

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "tools" / "staging"
TMP = Path(r"C:\Users\Asus\AppData\Local\Temp")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
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

def curl(url, out):
    r = subprocess.run(["curl.exe", "-s", "-m", "60", "-A", UA,
                        "--compressed", url, "-o", str(out)],
                       capture_output=True, text=True, timeout=90)
    return out.exists() and out.stat().st_size > 10000

def main():
    dl = rq.Session()
    dl.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                       "Referer": "https://www.airbnb.co.in/"})
    for slug, lid in IDS.items():
        dest = OUT / slug; dest.mkdir(parents=True, exist_ok=True)
        have = len(list(dest.glob("raw-*.jpg")))
        if have >= 4:
            print(f"{slug}: already has {have}, skip"); continue
        html = TMP / f"{slug}.html"
        if not curl(f"https://www.airbnb.co.in/rooms/{lid}", html):
            print(f"{slug}: PAGE FAIL"); time.sleep(8); continue
        t = html.read_text(encoding="utf-8", errors="replace")
        allimgs = list(OrderedDict.fromkeys(
            re.findall(r"https://a0\.muscache\.com/im/pictures/[A-Za-z0-9/._%~-]+?\.(?:jpe?g|png|webp)", t)))
        urls = [u for u in allimgs if not any(k in u for k in SKIP)]
        print(f"{slug}: page {len(t)} bytes, {len(urls)} imgs", flush=True)
        seen, n = set(), 0
        for u in urls:
            if n >= 6:
                break
            try:
                link = u + ("&im_w=1440" if "im_w" not in u else "")
                r = dl.get(link, timeout=40)
                if r.status_code != 200 or len(r.content) < 15000:
                    continue
                h = hashlib.md5(r.content).hexdigest()
                if h in seen:
                    continue
                seen.add(h)
                (dest / f"raw-{have+n:02d}.jpg").write_bytes(r.content)
                n += 1
            except Exception:
                continue
        print(f"{slug}: +{n} (total now {have+n})", flush=True)
        time.sleep(8)

if __name__ == "__main__":
    sys.exit(main())
