"""
ZETA Bot Integration System
Base architecture for extensible third-party integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Integration(ABC):
    """
    Abstract base class for all integrations.
    
    Each integration must implement:
    - initialize(): Setup and connection test
    - sync_products(): Pull product data from external system
    - create_order(): Push order to external system
    - check_availability(): Real-time stock check
    """
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the integration and test connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def sync_products(self) -> Dict[str, Any]:
        """
        Synchronize products from external system.
        
        Returns:
            Dict with sync results: {
                "success": bool,
                "products_synced": int,
                "errors": list
            }
        """
        pass
    
    @abstractmethod
    async def create_order(self, order_data: dict) -> Dict[str, Any]:
        """
        Create order in external system.
        
        Args:
            order_data: Order information including:
                - customer details
                - products
                - delivery info
        
        Returns:
            Dict with order result: {
                "success": bool,
                "order_id": str,
                "error": str (optional)
            }
        """
        pass
    
    @abstractmethod
    async def check_availability(self, sku: str) -> Dict[str, Any]:
        """
        Check product availability in external system.
        
        Args:
            sku: Product SKU/article number
        
        Returns:
            Dict with availability info: {
                "available": bool,
                "quantity": int,
                "price": float,
                "error": str (optional)
            }
        """
        pass


__all__ = ["Integration"]
