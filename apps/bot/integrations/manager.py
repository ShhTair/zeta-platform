"""
Integration Manager
Centralized manager for all third-party integrations
"""

from typing import Dict, Optional, List
import logging
import asyncio
from datetime import datetime

from . import Integration

logger = logging.getLogger(__name__)


class IntegrationManager:
    """
    Manages all registered integrations and provides unified interface.
    
    Usage:
        manager = IntegrationManager()
        manager.register("1c", OneCIntegration(...))
        manager.register("bitrix24", Bitrix24Integration(...))
        
        await manager.initialize_all()
        await manager.sync_all()
    """
    
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self.enabled: Dict[str, bool] = {}
        self.last_sync: Dict[str, Optional[datetime]] = {}
    
    def register(self, name: str, integration: Integration, enabled: bool = True):
        """
        Register a new integration.
        
        Args:
            name: Integration name (e.g., "1c", "bitrix24")
            integration: Integration instance
            enabled: Whether integration is enabled
        """
        self.integrations[name] = integration
        self.enabled[name] = enabled
        self.last_sync[name] = None
        logger.info(f"Registered integration: {name} (enabled={enabled})")
    
    async def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all enabled integrations.
        
        Returns:
            Dict mapping integration name to success status
        """
        results = {}
        
        for name, integration in self.integrations.items():
            if not self.enabled.get(name):
                logger.info(f"Skipping disabled integration: {name}")
                results[name] = False
                continue
            
            try:
                logger.info(f"Initializing integration: {name}")
                success = await integration.initialize()
                results[name] = success
                
                if success:
                    logger.info(f"✓ {name} initialized successfully")
                else:
                    logger.warning(f"✗ {name} initialization failed")
            except Exception as e:
                logger.error(f"✗ {name} initialization error: {e}")
                results[name] = False
        
        return results
    
    async def sync_all(self) -> Dict[str, Dict]:
        """
        Sync products from all enabled integrations.
        
        Returns:
            Dict mapping integration name to sync results
        """
        results = {}
        
        for name, integration in self.integrations.items():
            if not self.enabled.get(name):
                continue
            
            try:
                logger.info(f"Syncing products from {name}...")
                result = await integration.sync_products()
                results[name] = result
                self.last_sync[name] = datetime.now()
                
                if result.get("success"):
                    logger.info(f"✓ {name}: {result.get('products_synced', 0)} products synced")
                else:
                    logger.warning(f"✗ {name} sync failed: {result.get('errors')}")
            except Exception as e:
                logger.error(f"✗ {name} sync error: {e}")
                results[name] = {"success": False, "error": str(e)}
        
        return results
    
    async def create_order(self, integration_name: str, order_data: dict) -> Dict:
        """
        Create order in specific integration.
        
        Args:
            integration_name: Name of integration to use
            order_data: Order data
        
        Returns:
            Order creation result
        """
        integration = self.integrations.get(integration_name)
        
        if not integration:
            return {"success": False, "error": f"Integration '{integration_name}' not found"}
        
        if not self.enabled.get(integration_name):
            return {"success": False, "error": f"Integration '{integration_name}' is disabled"}
        
        try:
            result = await integration.create_order(order_data)
            return result
        except Exception as e:
            logger.error(f"Order creation error ({integration_name}): {e}")
            return {"success": False, "error": str(e)}
    
    async def check_availability(self, sku: str, integration_names: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Check product availability across integrations.
        
        Args:
            sku: Product SKU
            integration_names: List of integrations to check (None = all enabled)
        
        Returns:
            Dict mapping integration name to availability info
        """
        results = {}
        
        targets = integration_names or [
            name for name, enabled in self.enabled.items() if enabled
        ]
        
        for name in targets:
            integration = self.integrations.get(name)
            if not integration:
                continue
            
            try:
                result = await integration.check_availability(sku)
                results[name] = result
            except Exception as e:
                logger.error(f"Availability check error ({name}): {e}")
                results[name] = {"available": False, "error": str(e)}
        
        return results
    
    def get_status(self) -> Dict:
        """
        Get status of all integrations.
        
        Returns:
            Dict with integration status information
        """
        return {
            name: {
                "enabled": self.enabled.get(name, False),
                "last_sync": self.last_sync.get(name),
                "registered": True
            }
            for name in self.integrations.keys()
        }


# Global manager instance
integration_manager = IntegrationManager()


__all__ = ["IntegrationManager", "integration_manager"]
