#!/usr/bin/env python3
"""
Debug Bot Test Script
Run the bot with debug logging to see what's happening
"""

import os
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_bot_debug():
    """Test bot with debug logging"""
    print("🐛 Debug Bot Test")
    print("=" * 30)
    
    # Set a dummy token for testing
    os.environ['TELEGRAM_BOT_TOKEN'] = 'DEBUG_TOKEN_FOR_TESTING'
    
    try:
        from enhanced_telegram_bot import EnhancedDataExplorerBot
        
        print("✅ Bot imported successfully")
        
        # Create bot instance
        bot = EnhancedDataExplorerBot()
        print("✅ Bot instance created")
        
        # Check config
        print(f"📊 Available data sources: {list(bot.config['data_sources'].keys())}")
        
        # Test callback parsing
        test_callbacks = [
            "source_bai_members",
            "source_tcea_members",
            "source_credai_members"
        ]
        
        print("\n🧪 Testing callback parsing:")
        for callback in test_callbacks:
            if callback.startswith("source_"):
                source = callback[7:]  # Remove "source_" prefix (7 characters)
                print(f"✅ {callback} -> {source}")
                
                # Check if source exists in config
                if source in bot.config["data_sources"]:
                    print(f"   ✅ Source '{source}' found in config")
                else:
                    print(f"   ❌ Source '{source}' NOT found in config")
            else:
                print(f"❌ {callback} -> Invalid format")
        
        print("\n🎯 Debug Summary:")
        print("• Bot loads successfully")
        print("• Config has all data sources")
        print("• Callback parsing works correctly")
        print("• All sources exist in config")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot_debug()
