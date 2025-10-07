#!/usr/bin/env python3
"""
Telegram Bot Launcher Script
Easy way to start the Data Explorer Telegram Bot
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'telegram',
        'aiofiles',
        'pandas',
        'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Check if all required data files exist"""
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
    
    missing_files = []
    for file in required_files:
        filepath = data_dir / file
        if not filepath.exists():
            missing_files.append(file)
    
    if missing_files:
        print("⚠️ Missing data files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all data files are present before running the bot.")
        return False
    
    return True

def check_bot_token():
    """Check if bot token is configured"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Bot token not configured!")
        print("\nPlease set your TELEGRAM_BOT_TOKEN environment variable:")
        print("export TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("\nOr create a .env file with:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    if env_file.exists():
        print("📝 Loading environment from .env file...")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    else:
        print("📝 No .env file found. Using system environment variables.")

def run_bot(bot_type="enhanced"):
    """Run the selected bot"""
    if bot_type == "enhanced":
        bot_file = "enhanced_telegram_bot.py"
    else:
        bot_file = "telegram_bot.py"
    
    if not Path(bot_file).exists():
        print(f"❌ Bot file not found: {bot_file}")
        return False
    
    print(f"🤖 Starting {bot_type} Telegram Bot...")
    print("Press Ctrl+C to stop the bot")
    
    try:
        subprocess.run([sys.executable, bot_file])
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description="Data Explorer Telegram Bot Launcher")
    parser.add_argument("--bot", choices=["basic", "enhanced"], default="enhanced",
                       help="Choose bot type (default: enhanced)")
    parser.add_argument("--setup", action="store_true",
                       help="Run setup and configuration")
    parser.add_argument("--check", action="store_true",
                       help="Check system requirements")
    
    args = parser.parse_args()
    
    print("🤖 Data Explorer Telegram Bot Launcher")
    print("=" * 50)
    
    # Run setup if requested
    if args.setup:
        print("\n🔧 Running setup...")
        try:
            subprocess.run([sys.executable, "bot_setup.py"])
        except FileNotFoundError:
            print("❌ bot_setup.py not found")
            return
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return
    
    # Check requirements if requested
    if args.check:
        print("\n🔍 Checking system requirements...")
        
        print("1. Checking dependencies...")
        deps_ok = check_dependencies()
        
        print("2. Checking data files...")
        data_ok = check_data_files()
        
        print("3. Checking bot token...")
        token_ok = check_bot_token()
        
        if deps_ok and data_ok and token_ok:
            print("\n✅ All requirements met!")
        else:
            print("\n❌ Some requirements are missing.")
            return
    
    # Setup environment
    setup_environment()
    
    # Check bot token
    if not check_bot_token():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check data files
    if not check_data_files():
        return
    
    # Run the bot
    print(f"\n🚀 Starting {args.bot} bot...")
    success = run_bot(args.bot)
    
    if success:
        print("✅ Bot finished successfully")
    else:
        print("❌ Bot encountered errors")

if __name__ == "__main__":
    main()
