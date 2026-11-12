import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("tarot_rws")
OUT.mkdir(exist_ok=True)
WIDTH = 600  # 圖片寬度（像素），想要原圖就設為 None
HEADERS = {"User-Agent": "TarotDownloader/1.0 (personal teaching use)"}
API = "https://commons.wikimedia.org/w/api.php"

# 大阿爾克那 0–21
major = ["Fool", "Magician", "High Priestess", "Empress", "Emperor",
         "Hierophant", "Lovers", "Chariot", "Strength", "Hermit",
         "Wheel of Fortune", "Justice", "Hanged Man", "Death",
         "Temperance", "Devil", "Tower", "Star", "Moon", "Sun",
         "Judgement", "World"]

# (本地檔名, 維基檔名, 搜尋前綴)
cards = []
for i, name in enumerate(major):
    cards.append((f"major_{i:02d}_{name.replace(' ', '_')}",
                  f"RWS Tarot {i:02d} {name}.jpg",
                  f"RWS Tarot {i:02d}"))

# 小阿爾克那：權杖 Wands、聖杯 Cups、寶劍 Swords、錢幣 Pents
for suit, prefix in [("wands", "Wands"), ("cups", "Cups"),
                     ("swords", "Swords"), ("pentacles", "Pents")]:
    for n in range(1, 15):
        cards.append((f"{suit}_{n:02d}", f"{prefix}{n:02d}.jpg", f"{prefix}{n:02d}"))


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def file_url(wiki_name):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + \
          urllib.parse.quote(wiki_name.replace(" ", "_"))
    if WIDTH:
        url += f"?width={WIDTH}"
    return url


def search_name(prefix):
    """備援：用前綴在 Commons 搜尋實際檔名"""
    q = urllib.parse.urlencode({
        "action": "query", "list": "allimages", "aiprefix": prefix,
        "ailimit": 5, "format": "json"})
    data = json.loads(fetch(f"{API}?{q}"))
    items = data.get("query", {}).get("allimages", [])
    for it in items:
        if it["name"].lower().endswith((".jpg", ".jpeg", ".png")):
            return it["name"]
    return None


failed = []
for local, wiki, prefix in cards:
    dest = OUT / f"{local}.jpg"
    if dest.exists():
        continue
    try:
        try:
            data = fetch(file_url(wiki))
        except Exception:
            alt = search_name(prefix)
            if not alt:
                raise
            data = fetch(file_url(alt))
        dest.write_bytes(data)
        print("OK  ", dest.name)
    except Exception as e:
        print("FAIL", local, e)
        failed.append(local)
    time.sleep(1)  # 對維基伺服器客氣一點

print(f"\n完成，成功 {len(cards) - len(failed)} / {len(cards)} 張")
if failed:
    print("失敗：", failed)