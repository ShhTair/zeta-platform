"""
Product Search API Integration
Reused from Telegram bot with enhancements
"""

import logging
import httpx
from typing import List, Dict, Optional, Any

from config import settings

logger = logging.getLogger(__name__)


class ProductSearchAPI:
    """
    API client for product search and management.
    
    Integrates with ZETA backend API.
    """
    
    def __init__(self):
        self.base_url = settings.api_url
        self.city_id = settings.city_id
    
    async def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        material: Optional[str] = None,
        color: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search products in catalog.
        
        Args:
            query: Search query
            category: Product category filter
            material: Material filter
            color: Color filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            limit: Max results
        
        Returns:
            List of products
        """
        try:
            params = {
                "query": query,
                "city_id": self.city_id,
                "limit": limit
            }
            
            if category:
                params["category"] = category
            if material:
                params["material"] = material
            if color:
                params["color"] = color
            if min_price:
                params["min_price"] = min_price
            if max_price:
                params["max_price"] = max_price
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/search",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                products = data.get("products", [])
                
                logger.info(f"✓ Found {len(products)} products for query: {query}")
                return products
        
        except Exception as e:
            logger.error(f"❌ Product search error: {e}")
            return []
    
    async def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get detailed product information by SKU"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/{sku}",
                    params={"city_id": self.city_id},
                    timeout=10.0
                )
                response.raise_for_status()
                
                product = response.json()
                logger.info(f"✓ Retrieved product: {sku}")
                return product
        
        except Exception as e:
            logger.error(f"❌ Get product error: {e}")
            return None
    
    async def compare_products(self, sku_list: List[str]) -> List[Dict[str, Any]]:
        """Compare multiple products"""
        try:
            products = []
            for sku in sku_list[:3]:  # Max 3 products
                product = await self.get_product_by_sku(sku)
                if product:
                    products.append(product)
            
            return products
        
        except Exception as e:
            logger.error(f"❌ Compare products error: {e}")
            return []
    
    async def recommend_products(
        self,
        based_on_sku: Optional[str] = None,
        category: Optional[str] = None,
        style: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get smart product recommendations.
        
        Based on:
        - Similar products (if based_on_sku provided)
        - Complementary products (if category provided)
        - Style matching
        """
        try:
            params = {
                "city_id": self.city_id,
                "limit": limit
            }
            
            if based_on_sku:
                params["similar_to"] = based_on_sku
            if category:
                params["category"] = category
            if style:
                params["style"] = style
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/recommendations",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                products = data.get("products", [])
                
                logger.info(f"✓ Got {len(products)} recommendations")
                return products
        
        except Exception as e:
            logger.error(f"❌ Recommendations error: {e}")
            return []
    
    async def search_by_image(
        self,
        image_path: str,
        use_ocr: bool = True,
        use_vision: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search products by image.
        
        Methods:
        1. OCR - extract SKU from screenshot
        2. Vision API - describe image and search
        """
        try:
            async with httpx.AsyncClient() as client:
                with open(image_path, "rb") as f:
                    files = {"image": f}
                    data = {
                        "use_ocr": use_ocr,
                        "use_vision": use_vision,
                        "city_id": self.city_id
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/api/products/search-by-image",
                        files=files,
                        data=data,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    products = result.get("products", [])
                    
                    logger.info(f"✓ Image search found {len(products)} products")
                    return products
        
        except Exception as e:
            logger.error(f"❌ Image search error: {e}")
            return []


# Global API instance
product_api = ProductSearchAPI()


__all__ = ["ProductSearchAPI", "product_api"]
