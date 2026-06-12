import json
from functools import lru_cache
from pathlib import Path

from app.schemas.facility import Facility, PathMap, Zone


class MockDataLoader:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parents[1] / "data"

    def _read_json(self, filename: str) -> list[dict]:
        path = self.base_dir / filename
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @lru_cache
    def load_facilities(self) -> list[Facility]:
        return [Facility.model_validate(item) for item in self._read_json("facilities.json")]

    @lru_cache
    def load_zones(self) -> list[Zone]:
        return [Zone.model_validate(item) for item in self._read_json("zones.json")]

    @lru_cache
    def load_paths(self) -> list[PathMap]:
        return [PathMap.model_validate(item) for item in self._read_json("paths.json")]
