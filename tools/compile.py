"""Compile research data.md files -> site JSON. Run from project root:
  python site/tools/compile.py
Provenance: stays/*/data.md, places/place-*.md, stays/shortlist.md (areas)."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"

# slug -> (area_group, hub_label, hub_url, stay_kind)
META = {
 "stay-01-moonlight-view":   ("Jibhi", "Airbnb", "https://www.airbnb.com/rooms/52829977", "Airbnb"),
 "stay-02-whispering-pines": ("Tandi", "Airbnb", "https://www.airbnb.com/rooms/26117817", "Airbnb"),
 "stay-03-latoda-treehouse": ("Ghiyagi", "Airbnb hub", "https://www.airbnb.co.in/shoja-india/stays", "Airbnb"),
 "stay-04-wayward-inn":      ("Ghiyagi", "Airbnb hub", "https://www.airbnb.co.in/jibhi-india/stays", "Airbnb"),
 "stay-05-tandi-cottage":    ("Tandi", "Airbnb hub", "https://www.airbnb.co.in/jibhi-india/stays", "Airbnb"),
 "stay-06-mudhouse-peaks":   ("Jibhi", "Airbnb", "https://www.airbnb.co.in/rooms/1412122997309117906", "Airbnb"),
 "stay-07-lost-escape":      ("Jibhi", "Airbnb", "https://www.airbnb.co.in/rooms/758357609524923692", "Airbnb"),
 "stay-08-om-homestay":      ("Jibhi", "Airbnb hub", "https://www.airbnb.co.in/jibhi-india/stays", "Airbnb"),
 "stay-09-serenity-wooden":  ("Jibhi", "Airbnb hub", "https://www.airbnb.co.in/jibhi-india/stays", "Airbnb"),
 "stay-10-hillhouse-aframe": ("Jibhi", "Airbnb", "https://www.airbnb.co.in/rooms/1583118387367694595", "Airbnb"),
 "stay-11-silence-pines":    ("Jibhi", "Homestays of India", "https://www.homestaysofindia.com/himachal-banjar-jibhi-silence-of-pines", "Homestay"),
 "stay-12-moustache-shoja":  ("Shoja", "Booking hub", "https://www.booking.com/hostels/city/in/jibhi.html", "Hostel-private"),
 "stay-13-zostel-shoja":     ("Shoja", "Booking hub", "https://www.booking.com/hostels/city/in/jibhi.html", "Hostel-private"),
 "stay-14-tirthan-crest":    ("Tirthan", "Homestays hub", "https://www.homestays.co.in/gushaini-india", "Homestay"),
 "stay-15-riverside-serenity":("Tirthan", "Airbnb", "https://www.airbnb.co.in/rooms/1279706273527651930", "Airbnb"),
 "stay-16-cedar-nest-sainj": ("Sainj", "Booking hub", "https://www.booking.com/cottages/city/in/sainj.html", "Homestay"),
 "stay-17-mountain-nest":    ("Jibhi", "Direct", "https://mountainneststay.com/", "Homestay"),
 "stay-18-tirthan-riverview":("Tirthan", "Direct", "https://tirthanriverviewhomestay.bookmystay.io/", "Homestay"),
 "stay-19-jaabal-riverside": ("Tirthan", "Direct", "https://tirthanjaabalhomestay.com/", "Homestay"),
 "stay-20-mizuki-retreat":   ("Tirthan", "Direct", "https://mizukiretreat.com/", "Homestay"),
 "stay-21-forest-lens":      ("Jibhi", "Airbnb", "https://www.airbnb.com.au/rooms/1438153001249315575", "Airbnb"),
 "stay-22-rocky-retreat":    ("Jibhi", "Airbnb", "https://www.airbnb.com.au/rooms/1146687534659285703", "Airbnb"),
}

def parse_kv(md: str) -> dict:
    out = {}
    for m in re.finditer(r"^-\s+([^:]+):\s*(.*)$", md, re.M):
        out[m.group(1).strip()] = m.group(2).strip()
    return out

def inr_first(s: str):
    m = re.search(r"₹([\d,]+)", s or "")
    return int(m.group(1).replace(",", "")) if m else None

def parse_stays():
    recs = []
    for d in sorted((ROOT / "stays").glob("stay-*")):
        if not d.is_dir():
            continue
        slug = d.name
        md = (d / "data.md").read_text(encoding="utf-8")
        kv = parse_kv(md)
        name = md.splitlines()[0].lstrip("# ").strip()
        photos = [p.strip().replace("images/", f"assets/img/stays/{slug}/")
                  for p in kv.get("Photos", "").split(",") if p.strip()]
        allin = inr_first(kv.get("Price/night", "").split("|")[-1])
        area, hub_label, hub_url, kind = META[slug]
        recs.append({
            "slug": slug, "name": name, "area": area, "kind": kind,
            "type": kv.get("Type", ""), "location": kv.get("Location", ""),
            "price_base": inr_first(kv.get("Price/night", "")),
            "price_allin": allin,
            "total4": inr_first(kv.get("Total for 4 nights (Oct 4–8)", "")),
            "total5": inr_first(kv.get("Total for 5 nights (Oct 4–9, if extending)", "")),
            "rating": kv.get("Rating", ""), "cleanliness": kv.get("Cleanliness", ""),
            "view": kv.get("View/balcony", ""), "amenities": kv.get("Amenities", ""),
            "booking_primary": kv.get("Booking link", ""),
            "booking_hub": {"label": hub_label, "url": hub_url},
            "photos": photos, "why": kv.get("Why suggested", ""),
            "flag_over_cap": (allin or 0) > 2500,
        })
    return recs

def parse_places():
    recs = []
    for f in sorted((ROOT / "places").glob("place-*.md")):
        md = f.read_text(encoding="utf-8")
        kv = parse_kv(md)
        photos = [p.strip().replace("images/", "assets/img/places/")
                  for p in kv.get("Photos", "").split(",") if p.strip()]
        recs.append({"slug": f.stem, "name": md.splitlines()[0].lstrip("# ").strip(),
                     "type": kv.get("Type", ""), "location": kv.get("Location", ""),
                     "distance": kv.get("Distance", ""), "why": kv.get("Why it fits", kv.get("Why they fit", "")),
                     "notes": kv.get("Notes", ""), "photos": photos})
    return recs

def main():
    stays = parse_stays()
    places = parse_places()
    assert len(stays) == 22, f"expected 22 stays, got {len(stays)}"
    assert all(len(s["photos"]) == 4 for s in stays), "each stay needs 4 photos"
    missing = [p for s in stays for p in s["photos"]
               if not (ROOT / p.replace("assets/", "stays/" if "/stays/" in p else "places/")).exists()
               and not (SITE / p).exists() and not (ROOT / "stays" / s["slug"] / "images" / Path(p).name).exists()]
    # check against research originals
    for s in stays:
        for p in s["photos"]:
            orig = ROOT / "stays" / s["slug"] / "images" / Path(p).name
            assert orig.exists(), f"missing source image {orig}"
    for p in places:
        for ph in p["photos"]:
            orig = ROOT / "places" / "images" / Path(ph).name
            assert orig.exists(), f"missing source image {orig}"
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "data" / "stays.json").write_text(json.dumps(stays, ensure_ascii=False, indent=2), encoding="utf-8")
    (SITE / "data" / "places.json").write_text(json.dumps(places, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(stays)} stays, {len(places)} places")

if __name__ == "__main__":
    sys.exit(main())
