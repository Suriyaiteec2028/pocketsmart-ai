import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter

class SwiggyAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__(name="Swiggy", icon="fa-solid fa-burger")

    SERVICES = [
        {"name": "Swiggy Gourmet Party Catering (North & South Indian Buffet)", "category": "Catering", "per_person": 380, "preference": "Vegetarian", "rating": 4.6, "image": "https://images.unsplash.com/photo-1555244162-803834f70033?w=500&auto=format&fit=crop"},
        {"name": "Swiggy Deluxe Non-Veg Feast Catering Package", "category": "Catering", "per_person": 520, "preference": "Non-Vegetarian", "rating": 4.7, "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&auto=format&fit=crop"},
        {"name": "Swiggy High-Tea Celebration Snack Box (Pastries, Sandwiches & Chai)", "category": "Catering", "per_person": 220, "preference": "Snacks Only", "rating": 4.5, "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop"},
        {"name": "Swiggy Grand Multi-Cuisine Feast (Veg & Non-Veg)", "category": "Catering", "per_person": 600, "preference": "Both", "rating": 4.8, "image": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop"},
        {"name": "Warm Welcome Mocktail & Beverage Bar Service", "category": "Catering", "per_person": 120, "preference": "Snacks Only", "rating": 4.3, "image": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop"}
    ]

    def search_products(self, category: str, budget: float, preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    def search_services(self, category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        guest_count = 1
        pref = "Vegetarian"
        if requirements:
            guest_count = int(requirements.get("guest_count", 1))
            pref = requirements.get("catering_preference", "Vegetarian")

        for item in self.SERVICES:
            total_est = item["per_person"] * guest_count
            if total_est <= budget * 1.25 or len(results) == 0:
                res = dict(item)
                res["guest_count"] = guest_count
                res["total_price"] = total_est
                res["platform"] = self.name
                res["service_url"] = "https://www.swiggy.com"
                results.append(res)
        return results
