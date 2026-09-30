from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BasePlatformAdapter(ABC):
    """Abstract base class for all shopping and service platform adapters."""
    
    def __init__(self, name: str, icon: str = "shopping_bag"):
        self.name = name
        self.icon = icon

    @abstractmethod
    def search_products(
        self, 
        category: str, 
        budget: float, 
        preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search products within category and budget constraint."""
        pass

    @abstractmethod
    def search_services(
        self, 
        category: str, 
        location: str, 
        budget: float, 
        requirements: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search services/venues/catering within category and budget constraint."""
        pass
