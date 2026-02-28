# 💰 22-Billion: Hybrid AI Trading Coach

**Code Name:** 22-Billion  
**Version:** 1.0.0  
**Purpose:** Combine real-time data analysis with AI vision for superior trading signals

## 🎯 Overview

22-Billion is an advanced hybrid trading system that combines:
- **Data Engine**: Real-time market data from Binance Futures via ccxt and WebSocket
- **Vision Engine**: Chart pattern recognition using GPT-4o-mini Vision API
- **AI Brain**: Intelligent decision-making that merges algorithmic and visual analysis

This system provides **data-driven signals** validated by **human-like chart reading**, giving you the best of both worlds.

## ⚠️ DISCLAIMER

**THIS SOFTWARE IS FOR EDUCATIONAL PURPOSES ONLY.**

- Trading cryptocurrencies carries substantial risk of loss
- Past performance does not guarantee future results
- Always use testnet mode first
- Never risk more than 1-2% of your capital per trade
- The authors are not responsible for any financial losses

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     22-BILLION SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Data Engine  │      │Vision Engine │                    │
│  │              │      │              │                    │
│  │ • ccxt       │      │ • Screenshot │                    │
│  │ • WebSocket  │      │ • GPT-4o-mini│                    │
│  │ • TA-Lib     │      │ • OpenCV     │                    │
│  └──────┬───────┘      └──────┬───────┘                    │
│         │                     │                             │
│         └─────────┬───────────┘                             │
│                   ▼                                         │
│            ┌─────────────┐                                  │
│            │Trading Brain│                                  │
│            │             │                                  │
│            │ • Filtering │                                  │
│            │ • Validation│                                  │
│            │ • Risk Mgmt │                                  │
│            └──────┬──────┘                                  │
│                   ▼                                         │
│            ┌─────────────┐                                  │
│            │     GUI     │                                  │
│            │  + Voice    │                                  │
│            └─────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Binance account (for API keys)
- OpenAI account (for GPT-4o-mini API)

### Installation

#### 1. Clone or Download

```bash
# If you have git
git clone <repository-url>
cd 22-billion

# Or simply download and extract the ZIP file
```

#### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Install TA-Lib (Special Instructions)

TA-Lib requires system-level installation. Follow the guide for your OS:

##### 🐧 Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install build-essential wget

# Download and install TA-Lib C library
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install TA-Lib
```

##### 🍎 macOS

```bash
# Using Homebrew
brew install ta-lib

# Install Python wrapper
pip install TA-Lib
```

##### 🪟 Windows

**Option 1: Using pre-built wheel (Recommended)**

1. Download the appropriate wheel file from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   - For Python 3.11 64-bit: `TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl`
   - For Python 3.10 64-bit: `TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`

2. Install the wheel:
```bash
pip install TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl
```

**Option 2: Using conda**

```bash
conda install -c conda-forge ta-lib
```

#### 4. Verify Installation

```bash
python -c "import talib; print('TA-Lib version:', talib.__version__)"
```

If this prints a version number without errors, TA-Lib is installed correctly!

### Configuration

#### 1. Create config.json

```bash
cp config.example.json config.json
```

#### 2. Edit config.json

Open `config.json` in a text editor and add your API keys:

```json
{
  "binance": {
    "api_key": "YOUR_BINANCE_API_KEY",
    "api_secret": "YOUR_BINANCE_API_SECRET",
    "testnet": true
  },
  "openai": {
    "api_key": "YOUR_OPENAI_API_KEY",
    "model": "gpt-4o-mini"
  },
  ...
}
```

**Getting API Keys:**

- **Binance API**: 
  1. Go to https://www.binance.com/en/my/settings/api-management
  2. Create new API key
  3. Enable "Enable Futures" if trading futures
  4. For testnet: https://testnet.binancefuture.com/

- **OpenAI API**:
  1. Go to https://platform.openai.com/api-keys
  2. Create new secret key
  3. Copy and save it immediately (you won't see it again)

#### 3. Important Configuration Options

```json
{
  "trading": {
    "symbol": "BTC/USDT",      // Trading pair
    "timeframe": "1m",          // Candle timeframe
    "update_interval": 0.1,     // Update frequency (seconds)
    "risk_reward_ratio": 2.0    // Target risk:reward
  },
  "indicators": {
    "rsi_period": 14,           // RSI period
    "rsi_oversold": 30,         // Oversold threshold
    "rsi_overbought": 70,       // Overbought threshold
    ...
  },
  "vision": {
    "chart_capture_enabled": true,    // Enable/disable vision
    "screen_region": null,            // [x, y, width, height] or null for full screen
    "analysis_interval": 30           // Minimum seconds between AI analyses
  }
}
```

### Running the System

```bash
python main.py
```

The GUI window will appear. Click **START** to begin market analysis.

## 📊 How It Works

### 1. Data Collection

- **WebSocket**: Receives real-time price updates every 100ms
- **Order Book**: Monitors bid/ask depth to detect buying/selling pressure
- **Candles**: Maintains 200-candle history for technical analysis

### 2. Technical Analysis

Calculates multiple indicators:
- **RSI**: Relative Strength Index (overbought/oversold)
- **Bollinger Bands**: Price volatility and extremes
- **Moving Averages**: Trend direction (EMA 9/21)
- **MACD**: Momentum and trend confirmation
- **ATR**: Volatility for stop-loss calculation

### 3. Signal Generation

**Algorithmic Filter** (Stage 1):
- Scores signals based on multiple indicators
- Requires minimum 50/100 score
- Checks order book confirmation

Example signal criteria:
```
RSI < 30 (oversold)               → +30 points
Price near lower Bollinger Band   → +25 points
Bullish MA crossover              → +20 points
MACD bullish signal               → +15 points
Strong buy wall in order book     → +10 points
───────────────────────────────────────────────
Total: 100 points → STRONG LONG SIGNAL
```

### 4. AI Vision Validation (Stage 2)

If algorithmic signal is strong enough:
1. **Capture**: Takes screenshot of your chart
2. **Analyze**: Sends to GPT-4o-mini with technical context
3. **Validate**: AI checks for:
   - Visual patterns (head & shoulders, triangles, trend lines)
   - Support/resistance levels
   - Risk factors not visible in data
   - Optimal stop-loss and take-profit levels

### 5. Final Decision

**The Brain** combines:
- ✅ Algorithmic signal strength
- ✅ Order book data
- ✅ AI vision analysis
- ✅ Quick pattern detection (OpenCV)

If confidence > 40%, signal is approved and:
- 📊 Displayed in GUI
- 🔊 Voice alert (Korean)
- 💾 Saved to `signals/` folder with annotated chart

## 🎮 Using the GUI

### Main Interface

```
┌────────────────────────────────────────────────┐
│  💰 22-BILLION AI TRADING COACH                │
│  Data Engine + Vision Engine + AI Brain        │
├────────────────────────────────────────────────┤
│  🟢 RUNNING                                    │
│  Price: $92,450  RSI: 28.5  Signal: LONG 85%   │
├────────────────────────────────────────────────┤
│  [▶ START]  [⬛ STOP]                          │
├────────────────────────────────────────────────┤
│  📋 Activity Log                               │
│  ┌──────────────────────────────────────────┐ │
│  │ [12:34:56] 🚀 System started             │ │
│  │ [12:35:02] ✅ Data engine connected      │ │
│  │ [12:35:45] 🎯 LONG signal detected!      │ │
│  │ [12:35:45] Entry: $92,000                │ │
│  │ [12:35:45] Stop: $91,500                 │ │
│  │ [12:35:45] Target: $93,000               │ │
│  │ [12:35:46] 🔊 Voice alert played         │ │
│  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

### Voice Alerts

When a signal is confirmed, you'll hear (in Korean):

> "주인님, 데이터와 차트 모두 롱 포지션을 가리킵니다. 신뢰도 85퍼센트입니다. 진입가 92,000, 손절가 91,500, 목표가 93,000입니다. 승률 높은 자리입니다!"

Translation:
> "Master, both data and chart indicate a long position. Confidence is 85%. Entry 92,000, stop-loss 91,500, target 93,000. High probability setup!"

## 📁 Project Structure

```
22-billion/
├── main.py                    # Main entry point
├── data_engine.py             # Real-time data collection
├── technical_indicators.py    # TA-Lib wrapper
├── vision_engine.py           # Chart capture + GPT-4o-mini
├── trading_brain.py           # Decision-making logic
├── gui.py                     # Tkinter interface
├── requirements.txt           # Python dependencies
├── config.example.json        # Configuration template
├── config.json               # Your configuration (create this)
├── README.md                 # This file
├── signals/                  # Saved signal screenshots
├── logs/                     # Log files
└── charts/                   # Chart captures
```

## 🔧 Configuration Reference

### Trading Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `symbol` | BTC/USDT | Trading pair |
| `timeframe` | 1m | Candle timeframe (1m, 5m, 15m, 1h, etc.) |
| `update_interval` | 0.1 | Analysis update frequency (seconds) |
| `risk_reward_ratio` | 2.0 | Target risk:reward ratio |

### Indicator Settings

| Indicator | Default | Description |
|-----------|---------|-------------|
| `rsi_period` | 14 | RSI calculation period |
| `rsi_oversold` | 30 | Oversold threshold |
| `rsi_overbought` | 70 | Overbought threshold |
| `bb_period` | 20 | Bollinger Bands period |
| `bb_std` | 2 | Bollinger Bands standard deviation |
| `ma_fast` | 9 | Fast EMA period |
| `ma_slow` | 21 | Slow EMA period |

### Vision Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chart_capture_enabled` | true | Enable/disable vision analysis |
| `screen_region` | null | Screenshot region [x, y, w, h] or null for full screen |
| `analysis_interval` | 30 | Minimum seconds between AI calls (rate limiting) |

## 🐛 Troubleshooting

### TA-Lib Installation Issues

**Error: `TA_Lib not found`**

Make sure you installed both:
1. The C library (system-level)
2. The Python wrapper (pip)

Try:
```bash
# Verify C library
ls /usr/lib | grep ta-lib  # Linux
brew list ta-lib           # macOS

# Reinstall Python wrapper
pip uninstall TA-Lib
pip install --no-cache-dir TA-Lib
```

### WebSocket Connection Issues

**Error: `WebSocket connection failed`**

- Check your internet connection
- Verify Binance is accessible in your region
- Try using a VPN if Binance is blocked

### API Key Issues

**Error: `Invalid API key`**

- Double-check keys in `config.json`
- Ensure no extra spaces or quotes
- Verify API key permissions include "Enable Futures"
- For testnet, use testnet API keys

### Vision Engine Issues

**Error: `OpenAI API error`**

- Verify OpenAI API key is correct
- Check you have credits/billing enabled
- `gpt-4o-mini` is much cheaper than `gpt-4o`

**Error: `Screenshot failed`**

- On Linux, install: `sudo apt-get install python3-tk python3-dev`
- On headless servers, vision won't work (set `chart_capture_enabled: false`)

### GUI Issues

**Error: `TclError` or GUI doesn't appear**

```bash
# Linux
sudo apt-get install python3-tk

# macOS (usually pre-installed)
brew install python-tk

# Windows (usually works out of the box)
```

## 🎓 Understanding the Signals

### Signal Anatomy

```
🎯 22-BILLION TRADING SIGNAL
================================================================
신호: LONG 
신뢰도: 85.0%
현재가: $92,450.00

진입가: $92,450.00
손절가: $91,950.00     ← 1.5x ATR below entry
목표가: $93,450.00     ← 2x risk distance
손익비: 1:2.0

📊 기술적 지표:
- RSI: 28.50           ← Oversold
- BB 위치: 12.3%       ← Near lower band
- MA 추세: bullish     ← Uptrend
- MACD: 0.0024        ← Positive histogram

✅ 진입 근거:
  • RSI oversold (28.5)
  • Price near lower Bollinger Band
  • MA trend bullish (separation 2.34%)
  • Strong buy wall (imbalance 0.45)

⚠️ 리스크 요인:
  • None identified

🤖 AI 분석:
✅ 진입 추천
- 패턴: 상승 쐐기형 돌파 준비
- 검증: 지표와 패턴 일치
- 리스크: 91,800 이하 급락시 손절 필수
- 손절가: 91,950
- 목표가: 93,450
- 종합: 매수 타이밍 우수
```

### What Each Section Means

1. **신뢰도 (Confidence)**: Combined score from all analyses (40-100%)
   - 40-60%: Weak signal, be cautious
   - 60-80%: Moderate signal, consider entry
   - 80-100%: Strong signal, high confidence

2. **손익비 (Risk:Reward)**: Target profit vs. maximum loss
   - Always aim for 1:2 minimum
   - Example: Risk $500 to make $1000

3. **진입 근거 (Entry Reasons)**: Why the system thinks this is a good trade
   - More reasons = stronger signal
   - Look for confluence of multiple factors

4. **리스크 요인 (Risk Factors)**: What could go wrong
   - Empty is good (no contradictions found)
   - If many risks listed, avoid the trade

5. **AI 분석 (AI Analysis)**: Human-like chart reading
   - Confirms or rejects algorithmic signal
   - Provides visual pattern context
   - May adjust stop-loss/take-profit levels

## 💡 Best Practices

### 1. Start with Testnet

Always test with Binance Futures Testnet first:
- https://testnet.binancefuture.com/
- Get free testnet USDT
- Practice without real money

### 2. Proper Risk Management

- Never risk more than 1-2% per trade
- Always use stop-losses
- Don't overtrade (max 2-3 trades per day)
- Keep a trading journal

### 3. Signal Validation

Don't blindly follow signals:
- ✅ Check multiple timeframes
- ✅ Verify with your own chart
- ✅ Consider market context (news, overall trend)
- ✅ Wait for confirmation candles

### 4. Customize for Your Style

Adjust settings based on testing:
- More conservative? Increase signal threshold to 60+
- Longer timeframes? Use 5m or 15m candles
- Different instruments? Change symbol to ETH/USDT, etc.

### 5. Monitor Performance

Track your results:
- Win rate
- Average risk:reward
- Total profit/loss
- Drawdown periods

## 🔐 Security

- **Never share your API keys**
- **Use API key restrictions** (IP whitelist, trading-only permissions)
- **Enable 2FA** on your exchange account
- **Keep config.json private** (don't commit to public repos)
- **Use read-only keys** if just testing

## 📈 Performance Optimization

### Reduce API Calls

- Increase `update_interval` to 1-5 seconds
- Increase `analysis_interval` to 60+ seconds
- Disable vision if not needed

### Improve Signal Quality

- Increase minimum confidence to 60-70
- Add more confirmation indicators
- Use higher timeframes (5m, 15m) for less noise
- Backtest different RSI thresholds

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork and modify
- Add new indicators
- Improve AI prompts
- Create different trading strategies
- Share your results (not financial advice!)

## 📝 License

MIT License - Use at your own risk

## 🙏 Acknowledgments

- **ccxt**: Cryptocurrency exchange API library
- **TA-Lib**: Technical analysis library
- **OpenAI**: GPT-4o-mini API
- **Binance**: Market data and trading

## 📞 Support

For issues and questions:
1. Check this README first
2. Review Troubleshooting section
3. Check configuration examples
4. Search online for specific errors

## ⚡ Quick Reference

### Starting the System

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install TA-Lib (see detailed instructions above)

# 3. Configure
cp config.example.json config.json
nano config.json  # Add your API keys

# 4. Run
python main.py
```

### Essential Files

- `config.json` - Your API keys and settings
- `main.py` - Start the system
- `signals/` - Saved trading signals

### Key Shortcuts

- **START**: Begin market analysis
- **STOP**: Stop analysis and close connections
- **Close Window**: Safely shut down (asks confirmation if running)

---

**Remember: This is a tool to assist your trading decisions, not a get-rich-quick scheme. Always trade responsibly and within your means.**

Happy Trading! 💰📈
