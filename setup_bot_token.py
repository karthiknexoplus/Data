#!/usr/bin/env python3
"""
Quick Bot Token Setup Script
Helps you set up the bot token for testing
"""

import os
import sys

def setup_bot_token():
    """Setup bot token for testing"""
    print("🤖 Telegram Bot Token Setup")
    print("=" * 40)
    
    print("\n📝 To get your bot token:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Follow the instructions to create your bot")
    print("4. Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    
    print("\n🔑 Current bot token status:")
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token != 'YOUR_BOT_TOKEN_HERE':
        print(f"✅ Bot token is set: {token[:10]}...")
    else:
        print("❌ Bot token not set")
    
    print("\n⚙️ To set your bot token:")
    print("Option 1 - Environment variable:")
    print("export TELEGRAM_BOT_TOKEN=your_actual_token_here")
    
    print("\nOption 2 - Edit .env file:")
    print("nano .env")
    print("# Replace 'your_bot_token_here' with your actual token")
    
    print("\nOption 3 - Temporary for testing:")
    token_input = input("\nEnter your bot token (or press Enter to skip): ").strip()
    if token_input:
        os.environ['TELEGRAM_BOT_TOKEN'] = token_input
        print("✅ Bot token set for this session")
        
        # Test the bot
        print("\n🧪 Testing bot...")
        try:
            import sys
            sys.path.append('.')
            from enhanced_telegram_bot import EnhancedDataExplorerBot
            
            bot = EnhancedDataExplorerBot()
            print("✅ Bot initialized successfully!")
            print("\n🚀 Ready to start! Run:")
            print("python3 enhanced_telegram_bot.py")
            
        except Exception as e:
            print(f"❌ Error testing bot: {e}")
    else:
        print("⏭️ Skipped token setup")

def main():
    """Main function"""
    setup_bot_token()
    
    print("\n📚 Additional Help:")
    print("• Check TELEGRAM_BOT_README.md for detailed documentation")
    print("• Run python3 test_bot.py to validate setup")
    print("• Run python3 setup_telegram_bot.py for complete setup")

if __name__ == "__main__":
    main()
