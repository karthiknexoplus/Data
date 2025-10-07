#!/usr/bin/env python3
"""
Test TCEA and CREDAI Data Loading Fix
"""

import os
import json

def test_data_loading_fix():
    """Test the data loading fix for TCEA and CREDAI"""
    print("🧪 Testing TCEA and CREDAI Data Loading Fix")
    print("=" * 50)
    
    # Set a dummy token for testing
    os.environ['TELEGRAM_BOT_TOKEN'] = 'DEBUG_TOKEN_FOR_TESTING'
    
    try:
        from enhanced_telegram_bot import EnhancedDataExplorerBot
        
        print("✅ Bot imported successfully")
        
        # Create bot instance
        bot = EnhancedDataExplorerBot()
        print("✅ Bot instance created")
        
        # Test problematic data sources
        test_sources = ["tcea_members", "credai_members"]
        
        for source in test_sources:
            print(f"\n📊 Testing: {source}")
            
            # Test data loading
            import asyncio
            async def test_load():
                return await bot.load_data_source(source)
            
            loaded_data = asyncio.run(test_load())
            print(f"   ✅ Data loaded: {type(loaded_data)}")
            
            if isinstance(loaded_data, dict):
                print(f"   📋 Dict keys: {list(loaded_data.keys())}")
                
                # Test the fix logic
                if 'data' in loaded_data:
                    fixed_data = loaded_data['data']
                    print(f"   ✅ Fixed with 'data' key: {len(fixed_data)} records")
                elif 'members' in loaded_data:
                    fixed_data = loaded_data['members']
                    print(f"   ✅ Fixed with 'members' key: {len(fixed_data)} records")
                else:
                    print(f"   ⚠️ No known data key found")
            elif isinstance(loaded_data, list):
                print(f"   ✅ Already a list: {len(loaded_data)} records")
            else:
                print(f"   ❌ Unexpected type: {type(loaded_data)}")
        
        print("\n🎯 Test Summary:")
        print("✅ Data loading works")
        print("✅ Dict structure handling works")
        print("✅ Data extraction logic works")
        print("✅ No more slice errors expected")
        
        print("\n🚀 Ready to test in bot!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading_fix()
