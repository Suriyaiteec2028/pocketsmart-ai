import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter

class IkeaAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__(name="IKEA", icon="fa-solid fa-couch")

    CATALOG = [
        {"name": "IKEA KIVIK 3-Seat Sofa (Tibbleby Beige/Grey)", "category": "Sofa", "room": "Living Room", "price": 28990, "style": "Scandinavian", "rating": 4.6, "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&auto=format&fit=crop"},
        {"name": "IKEA LACK Coffee Table (White / Black-Brown)", "category": "Coffee Table", "room": "Living Room", "price": 1490, "style": "Minimalist", "rating": 4.5, "image": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500&auto=format&fit=crop"},
        {"name": "IKEA HEJNE Wooden Wall Shelf Unit", "category": "Storage", "room": "Living Room", "price": 3500, "style": "Industrial", "rating": 4.3, "image": "https://images.unsplash.com/photo-1594026112284-02bb6f3352fe?w=500&auto=format&fit=crop"},
        {"name": "IKEA MALM Bed Frame High with 2 Storage Boxes", "category": "Bed", "room": "Bedroom", "price": 19990, "style": "Minimalist", "rating": 4.7, "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&auto=format&fit=crop"},
        {"name": "IKEA SONGESAND 3-Door Wardrobe", "category": "Wardrobe", "room": "Bedroom", "price": 16990, "style": "Traditional", "rating": 4.4, "image": "https://images.unsplash.com/photo-1558997519-83ea9252def8?w=500&auto=format&fit=crop"},
        {"name": "IKEA TERTIAL Work Lamp (Dark Grey)", "category": "Lighting", "room": "Study Room", "price": 1290, "style": "Industrial", "rating": 4.8, "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop"},
        {"name": "IKEA TIPHEDE Flatwoven Rug (Natural/Black)", "category": "Rug", "room": "Living Room", "price": 1190, "style": "Scandinavian", "rating": 4.4, "image": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=500&auto=format&fit=crop"},
        {"name": "IKEA JOKKMOKK Table and 4 Chairs (Antique Stain)", "category": "Dining items", "room": "Dining Room", "price": 12990, "style": "Scandinavian", "rating": 4.5, "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=500&auto=format&fit=crop"},
        {"name": "IKEA KALLAX Shelving Unit 4x4", "category": "Storage", "room": "Study Room", "price": 9990, "style": "Modern", "rating": 4.6, "image": "https://images.unsplash.com/photo-1594026112284-02bb6f3352fe?w=500&auto=format&fit=crop"}
    ]

    def search_products(self, category: str, budget: float, preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        category_lower = category.lower() if category else ""
        results = []
        for item in self.CATALOG:
            item_cat = item["category"].lower()
            if (category_lower in item_cat or item_cat in category_lower) and item["price"] <= budget * 1.15:
                res = dict(item)
                query = urllib.parse.quote_plus(item["name"])
                res["platform"] = self.name
                res["product_url"] = f"https://www.ikea.com/in/en/search/?q={query}"
                results.append(res)
        return results

    def search_services(self, category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []
