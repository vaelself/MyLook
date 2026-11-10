"""Хранение данных пользователей в JSON-файле.

Все данные лежат в памяти (self.data) и после каждого изменения
сразу записываются на диск.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        # Один общий замок, чтобы два пользователя не записывали файл одновременно
        self.lock = asyncio.Lock()
        self.data = self._load()

    # ---------- работа с файлом ----------

    def _load(self) -> dict:
        """Читает файл. Если его нет — создаёт пустую структуру."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            data = {"users": {}}
            self._write(data)
            return data

        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not isinstance(data.get("users"), dict):
                raise ValueError("неправильная структура файла")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            # Файл испорчен: сохраняем его копию и начинаем с нуля
            broken = self.path.with_name(f"{self.path.name}.broken-{int(time.time())}")
            logger.error("Файл %s повреждён (%s), переименован в %s", self.path, e, broken)
            os.replace(self.path, broken)
            data = {"users": {}}
            self._write(data)
            return data

    def _write(self, data: dict) -> None:
        """Атомарная запись: сначала во временный файл, потом замена."""
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.path)

    def _save(self) -> None:
        self._write(self.data)

    # ---------- пользователь ----------

    def get_user(self, user_id: int) -> dict:
        """Возвращает данные пользователя, при необходимости создаёт пустые."""
        key = str(user_id)
        if key not in self.data["users"]:
            self.data["users"][key] = {"city": None, "next_id": 1, "places": [], "items": []}
        return self.data["users"][key]

    def _new_id(self, user: dict) -> int:
        new_id = user["next_id"]
        user["next_id"] += 1
        return new_id

    async def set_city(self, user_id: int, city: str) -> None:
        async with self.lock:
            self.get_user(user_id)["city"] = city
            self._save()

    # ---------- вещи ----------

    def get_items(self, user_id: int) -> list[dict]:
        return self.get_user(user_id)["items"]

    def get_item(self, user_id: int, item_id: int) -> dict | None:
        for item in self.get_items(user_id):
            if item["id"] == item_id:
                return item
        return None

    async def add_item(self, user_id: int, name: str, item_type: str, category: str,
                       photo_file_id: str, places: list[int]) -> dict:
        async with self.lock:
            user = self.get_user(user_id)
            item = {
                "id": self._new_id(user),
                "name": name,
                "type": item_type,
                "category": category,
                "photo_file_id": photo_file_id,
                "places": list(places),
            }
            user["items"].append(item)
            self._save()
            return item

    async def update_item(self, user_id: int, item_id: int, field: str, value) -> bool:
        """Меняет одно поле вещи. Возвращает False, если вещи нет."""
        async with self.lock:
            item = self.get_item(user_id, item_id)
            if item is None:
                return False
            item[field] = value
            self._save()
            return True

    async def set_item_places(self, user_id: int, item_id: int, place_ids: list[int]) -> bool:
        return await self.update_item(user_id, item_id, "places", list(place_ids))

    async def delete_item(self, user_id: int, item_id: int) -> bool:
        async with self.lock:
            user = self.get_user(user_id)
            item = self.get_item(user_id, item_id)
            if item is None:
                return False
            user["items"].remove(item)
            self._save()
            return True

    # ---------- места ----------

    def get_places(self, user_id: int) -> list[dict]:
        return self.get_user(user_id)["places"]

    def get_place(self, user_id: int, place_id: int) -> dict | None:
        for place in self.get_places(user_id):
            if place["id"] == place_id:
                return place
        return None

    def place_name_exists(self, user_id: int, name: str, exclude_id: int | None = None) -> bool:
        """Есть ли уже место с таким названием (без учёта регистра и пробелов)."""
        name = name.strip().lower()
        for place in self.get_places(user_id):
            if place["id"] != exclude_id and place["name"].strip().lower() == name:
                return True
        return False

    async def add_place(self, user_id: int, name: str) -> dict:
        async with self.lock:
            user = self.get_user(user_id)
            place = {"id": self._new_id(user), "name": name}
            user["places"].append(place)
            self._save()
            return place

    async def rename_place(self, user_id: int, place_id: int, name: str) -> bool:
        async with self.lock:
            place = self.get_place(user_id, place_id)
            if place is None:
                return False
            place["name"] = name
            self._save()
            return True

    async def delete_place(self, user_id: int, place_id: int) -> bool:
        """Удаляет место и убирает его из всех вещей (сами вещи остаются)."""
        async with self.lock:
            user = self.get_user(user_id)
            place = self.get_place(user_id, place_id)
            if place is None:
                return False
            user["places"].remove(place)
            for item in user["items"]:
                if place_id in item["places"]:
                    item["places"].remove(place_id)
            self._save()
            return True

    async def set_place_items(self, user_id: int, place_id: int, item_ids: list[int]) -> bool:
        """Отмечает, какие вещи подходят для места."""
        async with self.lock:
            if self.get_place(user_id, place_id) is None:
                return False
            for item in self.get_items(user_id):
                if item["id"] in item_ids and place_id not in item["places"]:
                    item["places"].append(place_id)
                elif item["id"] not in item_ids and place_id in item["places"]:
                    item["places"].remove(place_id)
            self._save()
            return True
