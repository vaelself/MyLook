"""Подбор образа. Здесь нет ничего от aiogram, только логика."""

import random
from dataclasses import dataclass, field

# Порядок вещей в готовом образе
OUTPUT_ORDER = {"outerwear": 0, "top": 1, "one_piece": 1, "bottom": 2, "shoes": 3, "accessory": 4}


@dataclass
class OutfitResult:
    outfits: list[list[dict]] = field(default_factory=list)  # найденные образы (0–2)
    missing: list[str] = field(default_factory=list)  # коды типов, которых не хватает
    no_items: bool = False  # для места не отмечено ни одной вещи


def build_outfits(items: list[dict], place_id: int, rng: random.Random, count: int = 2) -> OutfitResult:
    """Собирает до count разных образов из вещей, подходящих месту place_id."""
    # 1. Берём только вещи, отмеченные для этого места
    suitable = [item for item in items if place_id in item["places"]]
    if not suitable:
        return OutfitResult(no_items=True)

    # Раскладываем по типам
    by_type = {}
    for item in suitable:
        by_type.setdefault(item["type"], []).append(item)
    tops = by_type.get("top", [])
    bottoms = by_type.get("bottom", [])
    one_pieces = by_type.get("one_piece", [])
    shoes = by_type.get("shoes", [])

    # 2. Все возможные базовые комплекты
    base_sets = []
    for top in tops:
        for bottom in bottoms:
            for shoe in shoes:
                base_sets.append([top, bottom, shoe])
    for one_piece in one_pieces:
        for shoe in shoes:
            base_sets.append([one_piece, shoe])

    # 3. Если ничего не собирается — выясняем, чего не хватает
    if not base_sets:
        missing = []
        if not one_pieces:
            if not tops:
                missing.append("top")
            if not bottoms:
                missing.append("bottom")
        if not shoes:
            missing.append("shoes")
        return OutfitResult(missing=missing)

    # 4. Выбираем разные комплекты случайно и добавляем дополнения
    chosen = rng.sample(base_sets, min(count, len(base_sets)))
    outfits = []
    for base in chosen:
        outfit = list(base)
        if by_type.get("outerwear"):
            outfit.append(rng.choice(by_type["outerwear"]))
        if by_type.get("accessory"):
            outfit.append(rng.choice(by_type["accessory"]))
        outfit.sort(key=lambda item: OUTPUT_ORDER[item["type"]])
        outfits.append(outfit)

    return OutfitResult(outfits=outfits)
