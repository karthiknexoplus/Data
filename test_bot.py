#!/usr/bin/env python3
"""
Telegram Bot Test Script
Quick test to verify bot setup and configuration
"""

import os
import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import telegram
        print("✅ telegram module imported")
    except ImportError as e:
        print(f"❌ telegram module import failed: {e}")
        return False
    
    try:
        import aiofiles
        print("✅ aiofiles module imported")
    except ImportError as e:
        print(f"❌ aiofiles module import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas module imported")
    except ImportError as e:
        print(f"❌ pandas module import failed: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ openpyxl module imported")
    except ImportError as e:
        print(f"❌ openpyxl module import failed: {e}")
        return False
    
    return True

def test_bot_files():
    """Test if bot files exist and are valid"""
    print("\n📁 Testing bot files...")
    
    bot_files = [
        "telegram_bot.py",
        "enhanced_telegram_bot.py",
        "bot_setup.py",
        "bot_launcher.py",
        "setup_telegram_bot.py"
    ]
    
    for file in bot_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def test_data_files():
    """Test if data files exist"""
    print("\n📊 Testing data files...")
    
    data_dir = Path("/Users/apple/Desktop/Data")
    required_files = [
        "bai_members_comprehensive.json",
        "tcea_complete_data.json",
        "credai_members.json",
        "rera_agents_improved.json",
        "ccmc_contractors.json",
        "sub_reg_offices.json",
        "coimbatore_wards.json",
        "pollachi_wards.json",
        "pincodes.json"
    ]
    
    found_files = 0
    for file in required_files:
        filepath = data_dir / file
        if filepath.exists():
            print(f"✅ {file} exists")
            found_files += 1
        else:
            print(f"⚠️ {file} missing")
    
    print(f"\n📈 Found {found_files}/{len(required_files)} data files")
    return found_files > 0

def test_configuration():
    """Test bot configuration"""
    print("\n⚙️ Testing configuration...")
    
    # Check .env file
    if Path(".env").exists():
        print("✅ .env file exists")
    else:
        print("⚠️ .env file missing (will use system environment)")
    
    # Check bot config
    if Path("bot_config.json").exists():
        print("✅ bot_config.json exists")
    else:
        print("⚠️ bot_config.json missing (will use defaults)")
    
    # Check database
    if Path("users.db").exists():
        print("✅ users.db exists")
    else:
        print("⚠️ users.db missing (will be created)")
    
    return True

def test_bot_token():
    """Test bot token configuration"""
    print("\n🔑 Testing bot token...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token != 'YOUR_BOT_TOKEN_HERE':
        print("✅ Bot token is configured")
        return True
    else:
        print("⚠️ Bot token not configured")
        print("Please set TELEGRAM_BOT_TOKEN environment variable")
        return False

def main():
    """Main test function"""
    print("🤖 Telegram Bot Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("File Test", test_bot_files),
        ("Data Files Test", test_data_files),
        ("Configuration Test", test_configuration),
        ("Bot Token Test", test_bot_token)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Bot is ready to run.")
        print("\nNext steps:")
        print("1. Set your bot token: export TELEGRAM_BOT_TOKEN=your_token")
        print("2. Run the bot: python3 enhanced_telegram_bot.py")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues before running the bot.")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run setup: python3 setup_telegram_bot.py")
        print("3. Check data files are present")

if __name__ == "__main__":
    main()
