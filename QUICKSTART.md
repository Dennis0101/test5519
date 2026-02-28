# 🚀 Quick Start Guide - 22-Billion Trading Coach

## For Complete Beginners (Copy & Paste)

### Step 1: Install Python Libraries
```bash
pip install -r requirements.txt
```

### Step 2: Install TA-Lib

**Windows:**
1. Download: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Choose your Python version (e.g., `TA_Lib-0.4.28-cp311-cp311-win_amd64.whl`)
3. Install:
```bash
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux:**
```bash
sudo apt-get install build-essential wget
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### Step 3: Test Installation
```bash
python test_imports.py
```

If you see "✅ All imports successful!", continue to Step 4.

### Step 4: Create Configuration
```bash
cp config.example.json config.json
```

Edit `config.json` with your API keys:
```json
{
  "binance": {
    "api_key": "YOUR_KEY_HERE",
    "api_secret": "YOUR_SECRET_HERE",
    "testnet": true
  },
  "openai": {
    "api_key": "YOUR_OPENAI_KEY_HERE",
    "model": "gpt-4o-mini"
  }
}
```

**Get API Keys:**
- Binance Testnet: https://testnet.binancefuture.com (FREE, recommended)
- OpenAI: https://platform.openai.com/api-keys

### Step 5: Run
```bash
python main.py
```

Click **START** button in the GUI!

---

## Common Issues

### ❌ "TA-Lib not found"
→ See Step 2 above, TA-Lib needs special installation

### ❌ "Invalid API key"
→ Check `config.json`, make sure keys are correct

### ❌ "WebSocket error"
→ Check internet connection

### ❌ "OpenAI API error"
→ Verify OpenAI API key and billing

---

## Need More Help?

- **Full Guide:** See `README.md`
- **Korean Guide:** See `INSTALL_GUIDE_KR.md`
- **Test Imports:** Run `python test_imports.py`

---

**⚠️ IMPORTANT:**
- Always use **testnet** first (`"testnet": true` in config)
- This is for **education only**
- Trading involves **risk of loss**

Happy Trading! 💰
