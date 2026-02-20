"""
Document Search Handler
Allow users to search within uploaded documents (catalogs, manuals, etc.)
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import logging
import os

# TODO: Import when implementing
# from core.api_client import api_client
# from core.i18n import t, get_user_language

logger = logging.getLogger(__name__)

router = Router()

# Configuration
CITY_ID = int(os.getenv("CITY_ID", "1"))


@router.message(Command("docs"))
async def search_documents_command(message: Message):
    """
    Search documents by command.
    
    Usage:
        /docs диван угловой
        /docs прайс лист
    
    TODO (Next Phase):
    - Implement actual document search via API
    - Display results with excerpts
    - Allow viewing full document
    - Track search analytics
    """
    query = message.text.replace("/docs", "").strip()
    
    if not query:
        await message.answer(
            "📚 Поиск в документах\n\n"
            "Используйте: /docs [запрос]\n"
            "Например: /docs диван угловой\n\n"
            "🔍 Доступно для поиска:\n"
            "• Каталоги продукции\n"
            "• Прайс-листы\n"
            "• Инструкции\n"
            "• Руководства\n\n"
            "TODO: Реализовать поиск в следующей фазе"
        )
        return
    
    logger.info(f"Document search: '{query}' from user {message.from_user.id}")
    
    await message.answer("🔍 Ищу в документах...")
    
    # TODO: Implement actual search
    # try:
    #     # Search via API
    #     results = await api_client.search_documents(
    #         city_id=CITY_ID,
    #         query=query,
    #         limit=5
    #     )
    #     
    #     if results and results["count"] > 0:
    #         # Format results
    #         response = f"📚 Найдено в документах ({results['count']}):\n\n"
    #         
    #         for i, result in enumerate(results["results"], 1):
    #             response += f"{i}. **{result['filename']}**\n"
    #             response += f"   {result['excerpt']}\n"
    #             response += f"   Релевантность: {result['score']:.0%}\n\n"
    #         
    #         await message.answer(response)
    #     else:
    #         await message.answer(
    #             "❌ Ничего не нашёл в документах по запросу.\n"
    #             "Попробуйте другие слова или свяжитесь с менеджером."
    #         )
    # except Exception as e:
    #     logger.error(f"Document search error: {e}")
    #     await message.answer("⚠️ Ошибка при поиске. Попробуйте позже.")
    
    # Stub response
    await message.answer(
        "TODO: Поиск в документах пока не реализован.\n\n"
        f"Ваш запрос: \"{query}\"\n\n"
        "В следующей фазе здесь будет:\n"
        "✅ Семантический поиск по каталогам\n"
        "✅ Поиск по прайс-листам\n"
        "✅ Выдержки из документов\n"
        "✅ Ссылки на полные документы"
    )


@router.message(F.text.startswith("📚"))
async def search_documents_inline(message: Message):
    """
    Search documents via inline message (starts with 📚 emoji).
    
    Example:
        📚 диван угловой
    
    TODO: Implement in next phase
    """
    query = message.text.replace("📚", "").strip()
    
    if query:
        logger.info(f"Inline document search: '{query}'")
        await search_documents_command(message)


async def format_document_results(results: list) -> str:
    """
    Format document search results for display.
    
    TODO: Implement nice formatting with:
    - Document name and type
    - Relevant excerpt with highlighting
    - Page/section reference
    - Download link
    
    Args:
        results: List of search results
    
    Returns:
        Formatted string for display
    """
    if not results:
        return "Ничего не найдено"
    
    output = []
    for i, result in enumerate(results, 1):
        output.append(f"{i}. {result.get('filename', 'Unknown')}")
        
        excerpt = result.get("excerpt", "")
        if excerpt:
            output.append(f"   {excerpt[:200]}...")
        
        score = result.get("score", 0)
        output.append(f"   Релевантность: {score:.0%}\n")
    
    return "\n".join(output)


async def get_document_stats(city_id: int) -> dict:
    """
    Get document statistics for city.
    
    TODO: Implement in next phase
    - Count documents by type
    - Total indexed pages
    - Last update date
    
    Args:
        city_id: City ID
    
    Returns:
        Dict with statistics
    """
    # Stub
    return {
        "total_documents": 0,
        "catalogs": 0,
        "price_lists": 0,
        "manuals": 0,
        "last_updated": None
    }


__all__ = ["router"]
