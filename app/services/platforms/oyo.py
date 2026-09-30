from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter

class OyoAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__(name="OYO / Townhouse", icon="fa-solid fa-hotel")

    SERVICES = [
        {"name": "OYO Townhouse Banquet & Celebration Hall", "category": "Venue", "fixed_price": 12000, "capacity": 60, "rating": 4.2, "image": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=500&auto=format&fit=crop"},
        {"name": "Townhouse Deluxe AC Guest Room (Per Night)", "category": "Accommodation", "per_room": 1650, "rating": 4.3, "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&auto=format&fit=crop"},
        {"name": "OYO Premium Suite for Bridal/Guest Stays", "category": "Accommodation", "per_room": 2800, "rating": 4.5, "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500&auto=format&fit=crop"},
        {"name": "OYO Open Lawn & Courtyard Party Space", "category": "Venue", "fixed_price": 22000, "capacity": 150, "rating": 4.4, "image": "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=500&auto=format&fit=crop"}
    ]

    def search_products(self, category: str, budget: float, preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    def search_services(self, category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        category_lower = category.lower() if category else ""
        room_count = 1
        if requirements:
            room_count = max(1, int(requirements.get("room_count", 1)))

        for item in self.SERVICES:
            item_cat = item["category"].lower()
            if category_lower in item_cat or item_cat in category_lower:
                res = dict(item)
                res["platform"] = self.name
                res["service_url"] = "https://www.oyorooms.com"
                if "per_room" in item:
                    res["room_count"] = room_count
                    res["total_price"] = item["per_room"] * room_count
                else:
                    res["total_price"] = item["fixed_price"]
                results.append(res)
        return results
