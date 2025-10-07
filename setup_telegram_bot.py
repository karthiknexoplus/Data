#!/usr/bin/env python3
"""
Complete Telegram Bot Setup Script
One-click setup for the Data Explorer Telegram Bot
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("""
🤖 Data Explorer Telegram Bot - Complete Setup
==============================================

This script will help you set up the Telegram bot with all features
from your Data Explorer project.

""")

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file with sample configuration"""
    env_content = """# Telegram Bot Configuration
# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database configuration
DATABASE_PATH=users.db

# Data directory
DATA_DIRECTORY=/Users/apple/Desktop/Data

# Optional: Admin user IDs (comma-separated)
ADMIN_USERS=

# Optional: Webhook URL for production
WEBHOOK_URL=

# Optional: Logging level
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("📝 Created .env file with sample configuration")
        print("⚠️ Please edit .env file with your actual bot token")
    else:
        print("📝 .env file already exists")

def setup_database():
    """Setup database tables"""
    print("\n🗄️ Setting up database...")
    try:
        import sqlite3
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        # Create all necessary tables
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'en',
                is_bot BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                total_searches INTEGER DEFAULT 0,
                total_exports INTEGER DEFAULT 0
            )''',
            
            '''CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                results_count INTEGER DEFAULT 0,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS export_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                data_source TEXT NOT NULL,
                export_format TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                export_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )''',
            
            '''CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                action_count INTEGER DEFAULT 1,
                window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )'''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        conn.commit()
        conn.close()
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def validate_data_files():
    """Validate that all required data files exist"""
    print("\n📁 Validating data files...")
    
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
    existing_files = []
    
    for file in required_files:
        filepath = data_dir / file
        if filepath.exists():
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"✅ Found {len(existing_files)} data files")
    if missing_files:
        print(f"⚠️ Missing {len(missing_files)} data files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nThe bot will still work with available data files.")
    
    return len(existing_files) > 0

def create_bot_config():
    """Create bot configuration file"""
    print("\n⚙️ Creating bot configuration...")
    
    config = {
        "max_results_per_page": 10,
        "search_timeout": 30,
        "export_formats": ["csv", "excel", "json"],
        "rate_limits": {
            "search_per_minute": 10,
            "export_per_hour": 5,
            "messages_per_minute": 20
        },
        "features": {
            "search_enabled": True,
            "export_enabled": True,
            "location_services": True,
            "data_sources": {
                "bai_members": {"file": "bai_members_comprehensive.json", "name": "BAI Members"},
                "tcea_members": {"file": "tcea_complete_data.json", "name": "TCEA Members"},
                "credai_members": {"file": "credai_members.json", "name": "CREDAI Members"},
                "rera_agents": {"file": "rera_agents_improved.json", "name": "RERA Agents"},
                "ccmc_contractors": {"file": "ccmc_contractors.json", "name": "CCMC Contractors"},
                "sr_offices": {"file": "sub_reg_offices.json", "name": "Sub Registrar Offices"},
                "colleges": {"file": "edu_list_tn.json", "name": "Educational Institutions"},
                "nrlm_data": {"file": "nrlm_data.json", "name": "NRLM Data"},
                "cbe_wards": {"file": "coimbatore_wards.json", "name": "Coimbatore Wards"},
                "pollachi_wards": {"file": "pollachi_wards.json", "name": "Pollachi Wards"},
                "pincodes": {"file": "pincodes.json", "name": "Pincodes"},
                "suppliers": {"file": "suppliers_cache/suppliers_641016.json", "name": "Suppliers"}
            }
        }
    }
    
    with open("bot_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Bot configuration created")

def create_startup_scripts():
    """Create startup scripts for easy bot launching"""
    print("\n📜 Creating startup scripts...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting Data Explorer Telegram Bot...
python enhanced_telegram_bot.py
pause
"""
    
    with open("start_bot.bat", "w") as f:
        f.write(windows_script)
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting Data Explorer Telegram Bot..."
python3 enhanced_telegram_bot.py
"""
    
    with open("start_bot.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable
    os.chmod("start_bot.sh", 0o755)
    
    print("✅ Startup scripts created")

def print_next_steps():
    """Print next steps for the user"""
    print("""
🎉 Setup Complete!

Next Steps:
===========

1. Get your bot token from @BotFather on Telegram:
   - Open Telegram and search for @BotFather
   - Send /newbot command
   - Follow the instructions to create your bot
   - Copy the bot token

2. Configure your bot:
   - Edit the .env file
   - Replace 'your_bot_token_here' with your actual bot token
   - Optionally add admin user IDs

3. Start the bot:
   - Run: python enhanced_telegram_bot.py
   - Or use: python bot_launcher.py
   - Or use the startup scripts: start_bot.sh (Unix) or start_bot.bat (Windows)

4. Test your bot:
   - Open Telegram and search for your bot
   - Send /start command
   - Explore the features!

Bot Features:
=============
🏢 Data Sources - Browse all available datasets
🔍 Search - Find information across all sources  
📍 Location Services - Get location-based information
📊 Export - Download data in various formats
📈 Statistics - View usage analytics
🔧 Admin Panel - Manage bot (admin users only

For help:
- Send /help command to the bot
- Check TELEGRAM_BOT_README.md for detailed documentation
- Run: python bot_launcher.py --help

Happy botting! 🤖
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create environment file
    create_env_file()
    
    # Setup database
    if not setup_database():
        return
    
    # Validate data files
    validate_data_files()
    
    # Create bot configuration
    create_bot_config()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
