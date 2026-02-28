#!/usr/bin/env python3
"""
22-Billion: Hybrid AI Trading Coach
Main entry point that orchestrates all components

Code Name: 22-Billion
Author: Your Quant Engineer
Purpose: Combine data analysis and vision AI for superior trading signals
"""

import json
import sys
import os
from pathlib import Path

# Import our modules
from data_engine import DataEngine
from technical_indicators import TechnicalIndicators
from vision_engine import VisionEngine
from trading_brain import TradingBrain
from gui import TradingGUI
from news_analyzer import NewsAnalyzer
from market_analyzer import MarketAnalyzer


def load_config():
    """Load configuration from config.json"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("❌ Error: config.json not found!")
        print("")
        print("Please follow these steps:")
        print("1. Copy config.example.json to config.json")
        print("2. Edit config.json and add your API keys:")
        print("   - Binance API key and secret")
        print("   - OpenAI API key")
        print("")
        print("Example:")
        print("  cp config.example.json config.json")
        print("  nano config.json  # or use any text editor")
        print("")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate required fields
        required_fields = [
            ('binance', 'api_key'),
            ('binance', 'api_secret'),
            ('openai', 'api_key'),
        ]
        
        for section, field in required_fields:
            if config[section][field] in [None, '', 'YOUR_BINANCE_API_KEY_HERE', 
                                          'YOUR_BINANCE_API_SECRET_HERE', 
                                          'YOUR_OPENAI_API_KEY_HERE']:
                print(f"❌ Error: Please set {section}.{field} in config.json")
                sys.exit(1)
        
        print("✅ Configuration loaded successfully")
        return config
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    directories = ['signals', 'logs', 'charts']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_modules = {
        'ccxt': 'ccxt',
        'talib': 'TA-Lib',
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'openai': 'openai',
        'pyttsx3': 'pyttsx3',
        'websocket': 'websocket-client',
    }
    
    missing = []
    
    for module, package in required_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print("")
        print("❌ Missing dependencies detected!")
        print("")
        print("Please install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        print("")
        print("For TA-Lib installation, see README.md")
        print("")
        return False
    
    print("✅ All dependencies installed")
    return True


def print_banner():
    """Print startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           💰 22-BILLION HYBRID AI TRADING COACH 💰               ║
║                                                                   ║
║              🔹 Data Engine: Real-time Market Analysis           ║
║              🔹 Vision Engine: Chart Pattern Recognition         ║
║              🔹 AI Brain: GPT-4o-mini Decision Making            ║
║                                                                   ║
║                    Code Name: 22-Billion                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main application entry point"""
    
    # Print banner
    print_banner()
    print("")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("")
    
    # Load configuration
    config = load_config()
    print("")
    
    # Create necessary directories
    create_directories()
    print("")
    
    # Initialize components
    print("🔧 Initializing components...")
    print("")
    
    try:
        # Initialize Data Engine
        print("  📊 Initializing Data Engine...")
        data_engine = DataEngine(config)
        
        # Initialize Technical Indicators
        print("  📈 Initializing Technical Indicators...")
        technical_indicators = TechnicalIndicators(config)
        
        # Initialize Vision Engine
        print("  👁️  Initializing Vision Engine...")
        vision_engine = VisionEngine(config)
        
        # Initialize News Analyzer
        print("  📰 Initializing News Analyzer...")
        news_analyzer = NewsAnalyzer(config)
        
        # Initialize Market Analyzer
        print("  🌍 Initializing Market Analyzer...")
        market_analyzer = MarketAnalyzer(config)
        
        # Initialize Trading Brain
        print("  🧠 Initializing Trading Brain...")
        trading_brain = TradingBrain(config, data_engine, technical_indicators, vision_engine)
        
        # Initialize GUI
        print("  🖥️  Initializing GUI...")
        gui = TradingGUI(config, trading_brain, news_analyzer, market_analyzer)
        
        print("")
        print("✅ All components initialized successfully")
        print("="*70)
        print("")
        
        # Important notes
        print("⚠️  IMPORTANT NOTES:")
        print("")
        print("1. This is for EDUCATIONAL PURPOSES ONLY")
        print("2. Start with testnet mode (set in config.json)")
        print("3. Always verify signals manually before trading")
        print("4. Use proper risk management (never risk more than 1-2% per trade)")
        print("5. Past performance does not guarantee future results")
        print("")
        print("="*70)
        print("")
        
        # Run GUI
        print("🚀 Starting GUI...")
        print("")
        gui.run()
        
    except Exception as e:
        print("")
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
