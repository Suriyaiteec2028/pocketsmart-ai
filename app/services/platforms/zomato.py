from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter

class ZomatoAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__(name="Zomato", icon="fa-solid fa-utensils")

    SERVICES = [
        {"name": "Zomato Live Counter Buffet with Chaat & Dessert Stations", "category": "Catering", "per_person": 450, "preference": "Both", "rating": 4.7, "image": "https://images.unsplash.com/photo-1555244162-803834f70033?w=500&auto=format&fit=crop"},
        {"name": "Royal Banquet Hall Dining Hall Package", "category": "Venue", "fixed_price": 18000, "capacity": 100, "rating": 4.5, "image": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=500&auto=format&fit=crop"},
        {"name": "Skyline Rooftop Lounge Private Party Space", "category": "Venue", "fixed_price": 25000, "capacity": 75, "rating": 4.6, "image": "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=500&auto=format&fit=crop"},
        {"name": "Celebration Artisan Cake & Dessert Table Setup", "category": "Decoration", "fixed_price": 4500, "rating": 4.8, "image": "https://images.unsplash.com/photo-1535141192574-5d4897c13136?w=500&auto=format&fit=crop"}
    ]

    def search_products(self, category: str, budget: float, preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    def search_services(self, category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        category_lower = category.lower() if category else ""
        for item in self.SERVICES:
            item_cat = item["category"].lower()
            if category_lower in item_cat or item_cat in category_lower:
                res = dict(item)
                res["platform"] = self.name
                res["service_url"] = "https://www.zomato.com"
                results.append(res)
        return results
