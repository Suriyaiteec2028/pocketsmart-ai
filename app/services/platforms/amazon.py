import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter

class AmazonAdapter(BasePlatformAdapter):
    def __init__(self):
        super().__init__(name="Amazon", icon="fa-brands fa-amazon")

    # Realistic mock catalog for quick matching & candidate supply
    CATALOG = [
        # Home
        {"name": "Solimo Fabric 3-Seater Sofa (Grey)", "category": "Sofa", "room": "Living Room", "price": 14999, "style": "Modern", "rating": 4.3, "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&auto=format&fit=crop"},
        {"name": "Home Centre Verona 2-Seater Fabric Sofa", "category": "Sofa", "room": "Living Room", "price": 11500, "style": "Minimalist", "rating": 4.1, "image": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=500&auto=format&fit=crop"},
        {"name": "DeckUp Plank Engineered Wood Coffee Table", "category": "Coffee Table", "room": "Living Room", "price": 2899, "style": "Modern", "rating": 4.2, "image": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500&auto=format&fit=crop"},
        {"name": "Wipro Smart LED Warm White Floor Lamp", "category": "Lighting", "room": "Living Room", "price": 1999, "style": "Modern", "rating": 4.4, "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop"},
        {"name": "Urban Ladder Engineered Wood TV Entertainment Unit", "category": "TV Unit", "room": "Living Room", "price": 5499, "style": "Scandinavian", "rating": 4.2, "image": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=500&auto=format&fit=crop"},
        {"name": "Wakefit Queen Size Engineered Wood Bed with Storage", "category": "Bed", "room": "Bedroom", "price": 12499, "style": "Modern", "rating": 4.5, "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&auto=format&fit=crop"},
        {"name": "Sleepyhead Original Orthopedic Memory Foam Mattress", "category": "Mattress", "room": "Bedroom", "price": 8999, "style": "Comfort", "rating": 4.6, "image": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=500&auto=format&fit=crop"},
        {"name": "Amazon Basics 2-Door Wardrobe with Hanging Rod", "category": "Wardrobe", "room": "Bedroom", "price": 8499, "style": "Minimalist", "rating": 4.0, "image": "https://images.unsplash.com/photo-1558997519-83ea9252def8?w=500&auto=format&fit=crop"},
        {"name": "Story@Home 100% Blackout Room Darkening Curtains (Pack of 2)", "category": "Curtains", "room": "Living Room", "price": 1299, "style": "Modern", "rating": 4.3, "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500&auto=format&fit=crop"},
        {"name": "Status Flat Weave Textured Jute Center Rug (5x7 ft)", "category": "Rug", "room": "Living Room", "price": 2199, "style": "Boho/Modern", "rating": 4.1, "image": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=500&auto=format&fit=crop"},
        {"name": "Safal Wall Art Canvas Framed Painting Set of 3", "category": "Wall Decor", "room": "Living Room", "price": 999, "style": "Minimalist", "rating": 4.2, "image": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&auto=format&fit=crop"},

        # Jewelry
        {"name": "Zaveri Pearls Kundan & Pearl Choker Necklace Set with Earrings", "category": "Set", "price": 949, "style": "Traditional", "material": "Gold Plated", "color": "Gold", "occasion": "Wedding", "rating": 4.3, "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&auto=format&fit=crop"},
        {"name": "GIVA 925 Sterling Silver Classic Solitaire Zircon Stud Earrings", "category": "Earrings", "price": 1499, "style": "Minimal", "material": "Silver", "color": "Silver", "occasion": "Casual", "rating": 4.7, "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&auto=format&fit=crop"},
        {"name": "Yellow Chimes Austrian Crystal Elegant Drop Earrings", "category": "Earrings", "price": 699, "style": "Elegant", "material": "Silver", "color": "Silver", "occasion": "Party", "rating": 4.4, "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&auto=format&fit=crop"},
        {"name": "Shining Diva Fashion Oxidised Silver Tribal Choker Necklace", "category": "Necklace", "price": 499, "style": "Traditional", "material": "Silver", "color": "Silver", "occasion": "Festival", "rating": 4.2, "image": "https://images.unsplash.com/photo-1611591475806-231a4a49c4be?w=500&auto=format&fit=crop"},
        {"name": "GIVA 925 Sterling Silver Rose Gold Heart Adjustable Bracelet", "category": "Bracelet", "price": 1999, "style": "Modern", "material": "Rose Gold Plated", "color": "Rose Gold", "occasion": "Gift", "rating": 4.6, "image": "https://images.unsplash.com/photo-1611591475152-47eac9c5bfee?w=500&auto=format&fit=crop"},
        {"name": "Clara 925 Sterling Silver Solitaire Adjustable Finger Ring", "category": "Ring", "price": 1299, "style": "Modern", "material": "Silver", "color": "Silver", "occasion": "Engagement", "rating": 4.5, "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&auto=format&fit=crop"}
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
                res["product_url"] = f"https://www.amazon.in/s?k={query}"
                results.append(res)
        return results

    def search_services(self, category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []
