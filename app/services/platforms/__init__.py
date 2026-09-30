from typing import List, Dict, Any, Optional
from app.services.platforms.base import BasePlatformAdapter
from app.services.platforms.amazon import AmazonAdapter
from app.services.platforms.flipkart import FlipkartAdapter
from app.services.platforms.ikea import IkeaAdapter
from app.services.platforms.swiggy import SwiggyAdapter
from app.services.platforms.zomato import ZomatoAdapter
from app.services.platforms.oyo import OyoAdapter

# Singleton instances of adapters
amazon_adapter = AmazonAdapter()
flipkart_adapter = FlipkartAdapter()
ikea_adapter = IkeaAdapter()
swiggy_adapter = SwiggyAdapter()
zomato_adapter = ZomatoAdapter()
oyo_adapter = OyoAdapter()

PLATFORMS: Dict[str, BasePlatformAdapter] = {
    "amazon": amazon_adapter,
    "flipkart": flipkart_adapter,
    "ikea": ikea_adapter,
    "swiggy": swiggy_adapter,
    "zomato": zomato_adapter,
    "oyo": oyo_adapter
}

def search_all_products(category: str, budget: float, preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Aggregate product search results across retail platforms."""
    results = []
    for platform in [amazon_adapter, flipkart_adapter, ikea_adapter]:
        items = platform.search_products(category=category, budget=budget, preferences=preferences)
        results.extend(items)
    return results

def search_all_services(category: str, location: str, budget: float, requirements: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Aggregate services across service and hospitality platforms."""
    results = []
    for platform in [swiggy_adapter, zomato_adapter, oyo_adapter]:
        items = platform.search_services(category=category, location=location, budget=budget, requirements=requirements)
        results.extend(items)
    return results

__all__ = [
    "BasePlatformAdapter",
    "AmazonAdapter",
    "FlipkartAdapter",
    "IkeaAdapter",
    "SwiggyAdapter",
    "ZomatoAdapter",
    "OyoAdapter",
    "PLATFORMS",
    "search_all_products",
    "search_all_services"
]
