#!/usr/bin/env python3
"""
Quick test to verify all imports work
Run this before the main system to check dependencies
"""

import sys

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    print("-" * 60)
    
    tests = [
        ("ccxt", "Binance Exchange API"),
        ("websocket", "WebSocket Client"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("openai", "OpenAI API"),
        ("pyttsx3", "Text-to-Speech"),
        ("tkinter", "GUI Framework"),
    ]
    
    failed = []
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name:30s} - OK")
        except ImportError as e:
            print(f"❌ {name:30s} - FAILED: {e}")
            failed.append((module, name))
    
    print("-" * 60)
    
    # Special test for TA-Lib
    print("\n🔬 Testing TA-Lib (special)...")
    try:
        import talib
        print(f"✅ TA-Lib v{talib.__version__} - OK")
    except ImportError as e:
        print(f"❌ TA-Lib - FAILED: {e}")
        print("\n📖 TA-Lib requires special installation!")
        print("   See README.md or INSTALL_GUIDE_KR.md for instructions")
        failed.append(("talib", "TA-Lib"))
    
    print("-" * 60)
    
    if failed:
        print(f"\n❌ {len(failed)} module(s) failed to import:")
        for module, name in failed:
            print(f"   - {name} ({module})")
        print("\nInstall missing modules:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All imports successful! Ready to run main.py")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
