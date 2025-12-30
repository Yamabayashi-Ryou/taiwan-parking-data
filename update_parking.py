import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("data")
OUT.mkdir(exist_ok=True)

UTC = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def save(city, rows):
    path = OUT / f"{city}.json"
    backup = OUT / f"{city}.fallback.json"

    payload = {
        "city": city,
        "updated_at": UTC(),
        "records": rows
    }

    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        backup.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except:
        pass


def load_fallback(city):
    try:
        text = (OUT / f"{city}.fallback.json").read_text(encoding="utf-8")
        data = json.loads(text)
        for r in data["records"]:
            r["source_status"] = "fallback"
        return data["records"]
    except:
        return []


def fetch_json(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()


def normalize(city, type_, name, lat, lng, total=None, available=None, address=""):
    return {
        "city": city,
        "type": type_,
        "name": name,
        "lat": lat,
        "lng": lng,
        "total_spaces": total,
        "available_spaces": available,
        "address": address,
        "last_update_utc": UTC(),
        "source_status": "live"
    }


################################################
# 台北市 路邊 on-street
################################################
def taipei_onstreet():
    url = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json"
    try:
        js = fetch_json(url)
        rows = []
        for r in js["data"]["car"]:
            rows.append(
                normalize(
                    "Taipei",
                    "onstreet",
                    r["areaName"],
                    float(r["latitude"]),
                    float(r["longitude"]),
                    None,
                    int(r["availableCar"])
                )
            )
        save("taipei_onstreet", rows)
    except Exception:
        save("taipei_onstreet", load_fallback("taipei_onstreet"))


################################################
# 台北市 停車場 off-street
################################################
def taipei_offstreet():
    url = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldata.json"
    try:
        js = fetch_json(url)
        rows = []
        for r in js["data"]["park"]:
            rows.append(
                normalize(
                    "Taipei",
                    "offstreet",
                    r["parkName"],
                    float(r["纬度"]),
                    float(r["经度"]),
                    int(r["totalCar"]),
                    int(r["availableCar"])
                )
            )
        save("taipei_offstreet", rows)
    except:
        save("taipei_offstreet", load_fallback("taipei_offstreet"))


def main():
    taipei_onstreet()
    taipei_offstreet()
    print("完成更新")


if __name__ == "__main__":
    main()
