# Quick Deployment Guide - Image Search

## Prerequisites Check

```bash
# 1. Verify Tesseract is installed
tesseract --version
# Should show: tesseract 5.3.4

# 2. Check language support
tesseract --list-langs
# Should include: eng, rus

# 3. Verify Python dependencies
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
source venv/bin/activate
pip list | grep -E "Pillow|pytesseract|openai"
# Should show: Pillow, pytesseract, openai
```

## Configuration

### 1. Update Environment Variables

Edit `.env`:
```bash
nano .env
```

Required variables:
```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key  # For Vision API
WEBHOOK_HOST=your_server_ip
WEBHOOK_PORT=8443
```

**Important:** The OpenAI API key provided may be expired. Get a new one from:
https://platform.openai.com/api-keys

### 2. Test the Setup

```bash
# Activate virtual environment
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
source venv/bin/activate

# Run tests
python test_image_search.py

# Expected results:
# ✅ Tesseract Installation
# ✅ OCR Text Extraction
# ✅ SKU Pattern Recognition
# ⚠️ OpenAI API Connection (may fail if key invalid)
```

## Deployment Options

### Option 1: Direct Run (for testing)

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
source venv/bin/activate
python main.py
```

### Option 2: Systemd Service (recommended for production)

Create service file:
```bash
sudo nano /etc/systemd/system/zeta-bot.service
```

Content:
```ini
[Unit]
Description=ZETA Telegram Bot
After=network.target

[Service]
Type=simple
User=tair
WorkingDirectory=/home/tair/.openclaw/workspace/zeta-platform/apps/bot
Environment="PATH=/home/tair/.openclaw/workspace/zeta-platform/apps/bot/venv/bin"
ExecStart=/home/tair/.openclaw/workspace/zeta-platform/apps/bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zeta-bot
sudo systemctl start zeta-bot
sudo systemctl status zeta-bot
```

### Option 3: Docker (if you use containers)

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
docker build -t zeta-bot .
docker run -d --name zeta-bot --env-file .env zeta-bot
```

## Verification

### 1. Check Logs

```bash
# If running directly
# Watch terminal output

# If using systemd
sudo journalctl -u zeta-bot -f

# Look for:
# ✅ Webhook set: https://...
# ✅ Loaded config for city: default
```

### 2. Test Image Search

Send to your bot on Telegram:

**Test 1: Screenshot with text**
- Take screenshot with product code/SKU
- Send to bot
- Should extract and search

**Test 2: Product photo**
- Take photo of furniture
- Send to bot
- Should describe and search (needs valid API key)

**Test 3: Random image**
- Send non-product image
- Should offer alternatives

### 3. Monitor Performance

```bash
# Watch for errors
tail -f /var/log/zeta-bot.log  # If logging to file

# Check metrics
# - OCR success rate: grep "Found SKU via OCR" logs
# - Vision API usage: grep "Vision API:" logs
# - Error rate: grep "Image search error:" logs
```

## Troubleshooting

### Bot doesn't respond to photos

**Check:**
1. Handler registration order in `main.py`
2. Bot has webhook set: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
3. Logs for errors

### OCR not working

**Fix:**
```bash
# Reinstall Tesseract
sudo apt-get install --reinstall tesseract-ocr tesseract-ocr-rus

# Verify
tesseract --version
```

### Vision API errors

**Fix:**
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# If invalid, get new key from OpenAI dashboard
```

### Dependencies missing

**Fix:**
```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot
source venv/bin/activate
pip install -r requirements.txt --only-binary=:all:
```

## Rollback (if needed)

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot

# Revert main.py
git checkout main.py

# Revert requirements.txt
git checkout requirements.txt

# Revert handlers/interactive.py
git checkout handlers/interactive.py

# Remove new files
rm handlers/image_search.py
rm INSTALL_IMAGE_SEARCH.md
rm IMAGE_SEARCH_SUMMARY.md
rm DEPLOY.md
rm test_image_search.py

# Restart bot
sudo systemctl restart zeta-bot
```

## Performance Tuning

### Reduce Vision API costs

```python
# In image_search.py, adjust:
max_tokens=100  # Instead of 200 (saves money)

# Or disable Vision API temporarily:
openai_client = None  # Forces OCR-only mode
```

### Speed up OCR

```python
# In image_search.py:
text = pytesseract.image_to_string(
    image,
    lang='rus+eng',
    config='--psm 6 --oem 3'  # Use LSTM engine
)
```

## Support

**Documentation:**
- Full guide: `INSTALL_IMAGE_SEARCH.md`
- Summary: `IMAGE_SEARCH_SUMMARY.md`
- Tests: `python test_image_search.py`

**Key Files:**
- Handler: `handlers/image_search.py`
- Config: `.env`
- Entry: `main.py`

**Logs Location:**
- Systemd: `sudo journalctl -u zeta-bot`
- Direct: Terminal output

---

**Ready to deploy!** 🚀

Start with OCR-only mode (works now), then add Vision API when key is validated.
