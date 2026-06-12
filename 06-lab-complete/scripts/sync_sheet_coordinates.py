from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "facilities.json"

POI_MAPPING: dict[str, dict[str, Any]] = {
    "fac_rest_001": {
        "lat": 15.788222656362159,
        "lng": 108.41128974411366,
        "zone_id": "adventure_land",
        "source_label": "Nhà hàng Riverrine",
        "match_type": "exact",
    },
    "fac_rest_002": {
        "lat": 15.787982167160775,
        "lng": 108.41073208465507,
        "source_label": "Trò Chơi Trong Nhà anchor",
        "match_type": "anchor",
    },
    "fac_rest_003": {
        "lat": 15.787197870275882,
        "lng": 108.4087401515442,
        "source_label": "Nhà hàng Deli Land",
        "match_type": "exact",
    },
    "fac_rest_004": {
        "lat": 15.789344020658428,
        "lng": 108.4140574588308,
        "source_label": "Chợ quê: Ẩm thực Ba Miền",
        "match_type": "exact_anchor_name_variant",
    },
    "fac_rest_005": {
        "lat": 15.787982167160775,
        "lng": 108.41073208465507,
        "source_label": "Nhà hàng Chingu: Chuyên lẩu nướng",
        "match_type": "exact",
    },
    "fac_rest_006": {
        "lat": 15.786111093996086,
        "lng": 108.40879196937651,
        "source_label": "Nhà hàng Harbor Corner",
        "match_type": "anchor",
    },
    "fac_rest_007": {
        "lat": 15.787982167160775,
        "lng": 108.41073208465507,
        "source_label": "Trò Chơi Trong Nhà anchor",
        "match_type": "anchor",
    },
    "fac_rest_008": {
        "lat": 15.788204,
        "lng": 108.407826,
        "zone_id": "water_world",
        "source_label": "Nhà hàng Yummy Land",
        "match_type": "exact",
    },
    "fac_rest_009": {
        "lat": 15.785879693610086,
        "lng": 108.40922442027532,
        "source_label": "Sân khấu nhạc nước anchor",
        "match_type": "anchor",
    },
    "fac_rest_010": {
        "lat": 15.78659410635966,
        "lng": 108.40952788558832,
        "source_label": "Phố Tây - Phố mua sắm & ẩm thực",
        "match_type": "anchor",
    },
    "fac_toilet_001": {"lat": 15.789138245480403, "lng": 108.40828064942237, "source_label": "Nhà vệ sinh - Thế Giới Nước", "match_type": "exact"},
    "fac_toilet_002": {"lat": 15.78707580947385, "lng": 108.41008062289654, "source_label": "Nhà vệ sinh - Trò Chơi Trong Nhà", "match_type": "exact"},
    "fac_toilet_003": {"lat": 15.79068173688096, "lng": 108.41117003126487, "source_label": "Nhà vệ sinh - River Safari", "match_type": "exact"},
    "fac_first_aid_001": {"lat": 15.787739, "lng": 108.409514, "source_label": "Trạm y tế", "match_type": "exact"},
    "fac_first_aid_002": {"lat": 15.78707, "lng": 108.410455, "source_label": "Trạm y tế", "match_type": "exact"},
    "fac_rest_area_001": {"lat": 15.790293422521918, "lng": 108.41219083860923, "source_label": "Bến thuyền", "match_type": "anchor"},
    "fac_rest_area_002": {"lat": 15.786326953438365, "lng": 108.40825857031776, "source_label": "Quảng trường trung tâm", "match_type": "anchor"},
    "fac_locker_001": {"lat": 15.787936689152907, "lng": 108.40769217916463, "source_label": "Nhà vệ sinh - Thế Giới Nước (cổng vào gần khu gửi đồ)", "match_type": "anchor"},
    "fac_locker_002": {"lat": 15.785884, "lng": 108.407893, "source_label": "Quầy thông tin", "match_type": "anchor"},
    "fac_water_001": {"lat": 15.787982167160775, "lng": 108.41073208465507, "source_label": "Trò Chơi Trong Nhà anchor", "match_type": "anchor"},
    "fac_water_002": {"lat": 15.787278000337174, "lng": 108.41168705727584, "source_label": "Nhà vệ sinh - Vùng Đất Phiêu Lưu", "match_type": "anchor"},
    "fac_souvenir_001": {"lat": 15.787195623223077, "lng": 108.40921598988636, "source_label": "Phố Đông - Phố mua sắm & ẩm thực", "match_type": "anchor"},
    "fac_lostfound_001": {"lat": 15.785884, "lng": 108.407893, "source_label": "Quầy thông tin", "match_type": "anchor"},
    "fac_ticket_001": {"lat": 15.786262, "lng": 108.407787, "source_label": "Quầy vé", "match_type": "exact"},
}


def main() -> None:
    facilities = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    missing: list[str] = []

    for facility in facilities:
        mapping = POI_MAPPING.get(facility["id"])
        if mapping is None:
            missing.append(facility["id"])
            continue

        facility["lat"] = mapping["lat"]
        facility["lng"] = mapping["lng"]
        if mapping.get("zone_id"):
            facility["zone_id"] = mapping["zone_id"]

    if missing:
        raise RuntimeError(f"Missing coordinates for: {', '.join(missing)}")

    DATA_PATH.write_text(
        json.dumps(facilities, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
