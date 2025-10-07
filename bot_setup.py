#!/usr/bin/env python3
"""
Telegram Bot Configuration and Setup Script
"""

import os
import json
import sqlite3
from datetime import datetime

class BotConfig:
    """Configuration class for the Telegram bot"""
    
    def __init__(self):
        self.config_file = 'bot_config.json'
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "bot_token": "",
            "database_path": "users.db",
            "data_directory": "/Users/apple/Desktop/Data",
            "max_results_per_page": 10,
            "search_timeout": 30,
            "export_formats": ["csv", "excel", "json"],
            "supported_languages": ["en"],
            "admin_users": [],
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
                    "bai_members": True,
                    "tcea_members": True,
                    "credai_members": True,
                    "rera_agents": True,
                    "ccmc_contractors": True,
                    "sr_offices": True,
                    "colleges": True,
                    "nrlm_data": True,
                    "cbe_wards": True,
                    "pollachi_wards": True,
                    "pincodes": True,
                    "suppliers": True
                }
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def setup_database(self):
        """Setup database tables"""
        try:
            conn = sqlite3.connect(self.config['database_path'])
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT DEFAULT 'en',
                    is_bot BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    session_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Search history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    query TEXT NOT NULL,
                    results_count INTEGER DEFAULT 0,
                    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Export history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    data_source TEXT NOT NULL,
                    export_format TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    export_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Rate limiting table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    action_count INTEGER DEFAULT 1,
                    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database tables created successfully")
            
        except Exception as e:
            print(f"Error setting up database: {e}")
    
    def validate_data_files(self):
        """Validate that all required data files exist"""
        data_dir = self.config['data_directory']
        required_files = [
            'bai_members_comprehensive.json',
            'tcea_complete_data.json',
            'credai_members.json',
            'rera_agents_improved.json',
            'ccmc_contractors.json',
            'sub_reg_offices.json',
            'coimbatore_wards.json',
            'pollachi_wards.json',
            'pincodes.json'
        ]
        
        missing_files = []
        for file in required_files:
            filepath = os.path.join(data_dir, file)
            if not os.path.exists(filepath):
                missing_files.append(file)
        
        if missing_files:
            print("⚠️ Missing data files:")
            for file in missing_files:
                print(f"  - {file}")
            print("\nPlease ensure all data files are present before running the bot.")
            return False
        else:
            print("✅ All required data files are present")
            return True
    
    def create_sample_env_file(self):
        """Create sample environment file"""
        env_content = """# Telegram Bot Configuration
# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database configuration
DATABASE_PATH=users.db

# Data directory
DATA_DIRECTORY=/Users/apple/Desktop/Data

# Optional: Admin user IDs (comma-separated)
ADMIN_USERS=123456789,987654321

# Optional: Webhook URL for production
WEBHOOK_URL=https://yourdomain.com/webhook

# Optional: Logging level
LOG_LEVEL=INFO
"""
        
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write(env_content)
            print("📝 Created .env file with sample configuration")
            print("Please edit .env file with your actual bot token")
        else:
            print("📝 .env file already exists")

def main():
    """Main setup function"""
    print("🤖 Telegram Bot Setup")
    print("=" * 50)
    
    config = BotConfig()
    
    # Setup database
    print("\n1. Setting up database...")
    config.setup_database()
    
    # Validate data files
    print("\n2. Validating data files...")
    config.validate_data_files()
    
    # Create environment file
    print("\n3. Creating environment file...")
    config.create_sample_env_file()
    
    print("\n✅ Setup completed!")
    print("\nNext steps:")
    print("1. Get your bot token from @BotFather on Telegram")
    print("2. Edit .env file with your bot token")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Run the bot: python telegram_bot.py")
    
    print("\n📖 Bot Features:")
    print("• Browse all data sources (BAI, TCEA, CREDAI, etc.)")
    print("• Search across all datasets")
    print("• Location services (wards, pincodes, suppliers)")
    print("• Export data in CSV, Excel, JSON formats")
    print("• User session management")
    print("• Rate limiting and security")

if __name__ == '__main__':
    main()
