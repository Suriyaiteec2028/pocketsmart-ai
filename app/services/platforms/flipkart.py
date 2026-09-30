import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter

class FlipkartAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__(name="Flipkart", icon="fa-solid fa-cart-shopping")

    CATALOG = [
        # Home
        {"name": "Bharat Lifestyle Tulip Leatherette 3+1+1 Sofa Set", "category": "Sofa", "room": "Living Room", "price": 18499, "style": "Modern", "rating": 4.1, "image": "https://images.unsplash.com/photo-1540574163026-643ea20ade25?w=500&auto=format&fit=crop"},
        {"name": "HomeTown Bolton Engineered Wood Center Table", "category": "Coffee Table", "room": "Living Room", "price": 3199, "style": "Modern", "rating": 4.0, "image": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500&auto=format&fit=crop"},
        {"name": "Spacewood Winner King Size Engineered Wood Bed", "category": "Bed", "room": "Bedroom", "price": 14999, "style": "Modern", "rating": 4.3, "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&auto=format&fit=crop"},
        {"name": "Nilkamal Freedom Mini Medium Engineered Plastic Wardrobe", "category": "Wardrobe", "room": "Bedroom", "price": 4999, "style": "Budget Friendly", "rating": 4.1, "image": "https://images.unsplash.com/photo-1558997519-83ea9252def8?w=500&auto=format&fit=crop"},
        {"name": "Philips Astra Deco Smart Wi-Fi 20W LED Ceiling Batten", "category": "Lighting", "room": "Living Room", "price": 1299, "style": "Modern", "rating": 4.4, "image": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=500&auto=format&fit=crop"},
        {"name": "Kuber Industries Kitchen Dish Drainer Rack Organizer", "category": "Organizers", "room": "Kitchen", "price": 899, "style": "Modern", "rating": 4.2, "image": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&auto=format&fit=crop"},
        {"name": "Pigeon by Stovekraft 4-Burner Glass Top Gas Stove", "category": "Appliances", "room": "Kitchen", "price": 3299, "style": "Modern", "rating": 4.3, "image": "https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=500&auto=format&fit=crop"},

        # Jewelry
        {"name": "Sukkhi Regal Gold Plated Wedding Choker Necklace Set", "category": "Set", "price": 799, "style": "Traditional", "material": "Gold Plated", "color": "Gold", "occasion": "Wedding", "rating": 4.2, "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&auto=format&fit=crop"},
        {"name": "Voylla Brass Gold Plated Jhumki Earrings", "category": "Earrings", "price": 649, "style": "Traditional", "material": "Brass", "color": "Gold", "occasion": "Festival", "rating": 4.1, "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&auto=format&fit=crop"},
        {"name": "Zaveri Pearls Cubic Zirconia Platinum Plated Ring", "category": "Ring", "price": 549, "style": "Diamond Look", "material": "Silver Plated", "color": "Silver", "occasion": "Party", "rating": 4.4, "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&auto=format&fit=crop"},
        {"name": "Karatcart Traditional Royal Peacock Kada Bangles (Set of 2)", "category": "Bangles", "price": 899, "style": "Traditional", "material": "Gold Plated", "color": "Gold", "occasion": "Wedding", "rating": 4.3, "image": "https://images.unsplash.com/photo-1611591475152-47eac9c5bfee?w=500&auto=format&fit=crop"}
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
                res["product_url"] = f"https://www.flipkart.com/search?q={query}"
                results.append(res)
        return results

    def search_services(self, category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []
