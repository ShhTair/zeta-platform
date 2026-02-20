# Image Search Installation Guide

## Overview
Complete image search feature for ZETA bot using:
- **OCR (Tesseract)** - Extract text/SKU from screenshots
- **OpenAI Vision API (gpt-4o-mini)** - Describe product from photos
- **Hybrid Search** - Falls back gracefully when one method fails

## System Requirements

### 1. Install Tesseract OCR

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

#### Verify Installation:
```bash
tesseract --version
# Should show: tesseract 4.x.x or 5.x.x
```

### 2. Install Python Dependencies

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
pip install -r requirements.txt
```

**New dependencies added:**
- `Pillow==10.4.0` - Image processing
- `pytesseract==0.3.13` - OCR wrapper

## Configuration

### Environment Variables (.env)

The following variables are required:

```env
# Telegram Bot Token
BOT_TOKEN=your_bot_token_here

# OpenAI API Key (for Vision API)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# Webhook settings
WEBHOOK_HOST=your_server_ip
WEBHOOK_PORT=8443
```

**⚠️ Important:** The OpenAI API key is already configured in `.env`

## Architecture

### Handler Flow

```
User sends photo
    ↓
image_search.py: handle_product_photo()
    ↓
1. Download photo to /tmp
    ↓
2. Try OCR (extract_text_with_ocr)
   ├─ Extract SKU pattern (e.g., КР-СТ-12345)
   └─ Search by SKU → Found? ✅
    ↓
3. If no SKU found, use Vision API
   ├─ analyze_image_with_vision()
   ├─ Get product description
   └─ Search by description → Found? ✅
    ↓
4. Display results with inline buttons
    OR
5. Offer alternatives (describe manually, contact manager)
```

### File Structure

```
handlers/
├── image_search.py       # NEW: Main image search handler
├── interactive.py        # Updated: Photo search button now active
├── product_inquiry.py    # Existing: Text-based search
├── callbacks.py          # Existing: Product detail callbacks
└── start.py             # Existing: FSM states

services/
├── api_client.py        # Existing: Catalog API interface
└── prompt_manager.py    # Existing: Dynamic prompts

requirements.txt         # Updated: Added Pillow, pytesseract
main.py                 # Updated: Registered image_search router
```

## Handler Registration Order

**Important:** Handlers are registered in priority order:

1. `start.router` - /start command
2. **`image_search.router`** - F.photo (photos)
3. `interactive.router` - Interactive UI buttons
4. `callbacks.router` - Callback queries
5. `conversation_interactive.router` - Enhanced conversation
6. `product_inquiry.router` - Text search fallback
7. `escalation.router` - Manager escalation

## Testing

### 1. Test OCR (Screenshot with SKU)

Create a test image with text:
```bash
python test_image_search.py
```

Or manually:
1. Take screenshot of product page with SKU
2. Send to bot
3. Should extract SKU and find product

### 2. Test Vision API (Product Photo)

1. Take photo of furniture (chair, table, etc.)
2. Send to bot
3. Should describe product and search catalog

### 3. Test Fallback

1. Send photo of non-furniture item
2. Should offer manual description option

## SKU Patterns

The OCR system recognizes these patterns:

- **Standard:** `КР-СТ-12345`, `ДИВ-КЛА-001`
- **Article markers:** `Артикул: ABC-123`, `SKU: XYZ-456`
- **Product codes:** Any format with dashes and numbers

Regex pattern: `[А-ЯA-Z]{2,5}-[А-ЯA-Z]{2,5}-\d{2,6}`

## Cost Optimization

### OpenAI Vision API Pricing
- Model: `gpt-4o-mini` (cost-effective)
- ~$0.000015 per image (with 200 tokens response)
- For 1000 searches/day: ~$0.015/day or $5.50/month

### Optimization Tips
1. **OCR first:** Free and fast for screenshots
2. **Vision API only when needed:** Fallback after OCR
3. **Cache results:** Store successful searches
4. **Limit resolution:** Use Telegram's medium quality (reduces tokens)

## Troubleshooting

### Issue: "Tesseract not found"
```bash
# Check if installed
which tesseract

# Install if missing
sudo apt-get install tesseract-ocr tesseract-ocr-rus
```

### Issue: "OpenAI API key invalid"
```bash
# Verify key in .env
cat .env | grep OPENAI_API_KEY

# Test key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: OCR extracts garbage
- Ensure image is high quality
- Check language packs: `tesseract --list-langs`
- Should show: `eng`, `rus`

### Issue: Vision API too slow
- Check image size (large images = more tokens)
- Consider downscaling before base64 encoding
- Use `gpt-4o-mini` instead of `gpt-4-vision-preview`

## Success Criteria Checklist

- ✅ Bot accepts photos (F.photo handler)
- ✅ OCR extracts text from images (pytesseract)
- ✅ SKU pattern recognition (regex)
- ✅ Vision API describes products (gpt-4o-mini)
- ✅ Search finds products by description
- ✅ Inline buttons show results
- ✅ Works for screenshots with SKU
- ✅ Works for product photos without text
- ✅ Graceful fallback when nothing found
- ✅ Temp file cleanup

## Deployment

### 1. Update Dependencies
```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
pip install -r requirements.txt
```

### 2. Restart Bot
```bash
# If using systemd
sudo systemctl restart zeta-bot

# If using Docker
docker-compose down
docker-compose up -d --build

# If running manually
pkill -f "python main.py"
python main.py
```

### 3. Verify
```bash
# Check logs
tail -f /var/log/zeta-bot.log

# Or if running in terminal
# Look for:
# ✅ Webhook set: https://...
# ✅ Loaded config for city: default
```

## Monitoring

### Key Metrics to Track

1. **OCR Success Rate:**
   - Check logs for `Found SKU via OCR: XYZ-123`
   - Target: >60% for screenshots with text

2. **Vision API Usage:**
   - Count `Vision API: <description>` log entries
   - Monitor OpenAI API usage dashboard

3. **Product Found Rate:**
   - Track `found X products via <method>`
   - Target: >70% overall success rate

4. **Error Rate:**
   - Watch for `Image search error:` logs
   - Investigate recurring patterns

### Log Examples

**Successful OCR:**
```
INFO - OCR text: Артикул: КР-СТ-12345 Стул деревянный...
INFO - Found SKU via OCR: КР-СТ-12345
INFO - User 123456 found 3 products via OCR → SKU
```

**Successful Vision API:**
```
INFO - OCR extracted 0 characters
INFO - Vision API: Современный деревянный стул со спинкой, темно-коричневого цвета
INFO - User 123456 found 5 products via Vision API
```

## Future Enhancements

### Phase 2: Image Similarity (CLIP)
```python
# Optional: Use CLIP for image embeddings
from transformers import CLIPModel, CLIPProcessor

# Requires pre-computed embeddings for 37K products
# More accurate but slower and resource-intensive
```

**Benefits:**
- Find visually similar products
- Works without text/description
- Better for exact matches

**Challenges:**
- Need to pre-compute 37K embeddings
- Requires GPU for reasonable speed
- Storage: ~10MB for 37K vectors

## Support

If you encounter issues:
1. Check logs: `tail -f /var/log/zeta-bot.log`
2. Verify dependencies: `pip list | grep -E "Pillow|pytesseract|openai"`
3. Test Tesseract: `tesseract test.jpg output -l rus+eng`
4. Test OpenAI: Check API key in dashboard

## Changes Made

### Files Created
- `handlers/image_search.py` - Complete image search implementation

### Files Modified
- `requirements.txt` - Added Pillow, pytesseract
- `main.py` - Registered image_search router
- `handlers/interactive.py` - Updated photo search button text
- `.env` - Updated OPENAI_API_KEY

### No Breaking Changes
- All existing handlers remain functional
- Image search is additive (doesn't break text search)
- Backward compatible with old bot versions
