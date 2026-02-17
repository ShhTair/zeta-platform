"""
API Client - Communicate with ZETA Platform backend
"""
import aiohttp
import logging

logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


async def search_products_api(query: str, category: str = None, material: str = None, limit: int = 5) -> list:
    """
    Search products in ZETA backend
    
    Args:
        query: Search query
        category: Product category filter
        material: Material filter
        limit: Max results
    
    Returns:
        List of product dicts with keys: sku, name, description, link, etc.
    """
    try:
        params = {
            "q": query,
            "limit": limit
        }
        if category:
            params["category"] = category
        if material:
            params["material"] = material
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/products/search",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get("products", [])
                    logger.info(f"Found {len(products)} products for query: {query}")
                    return products
                else:
                    logger.error(f"API search failed with status {resp.status}")
                    return []
    
    except Exception as e:
        logger.error(f"Product search error: {e}")
        return []


async def get_product_by_sku(sku: str) -> dict:
    """
    Get product details by SKU
    
    Args:
        sku: Product SKU
    
    Returns:
        Product dict or None
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/products/{sku}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    product = await resp.json()
                    return product
                else:
                    logger.error(f"Product {sku} not found (status {resp.status})")
                    return None
    
    except Exception as e:
        logger.error(f"Get product error: {e}")
        return None
