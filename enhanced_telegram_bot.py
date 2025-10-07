#!/usr/bin/env python3
"""
Enhanced Telegram Bot for Data Explorer Project
Advanced features with comprehensive data integration
"""

import os
import json
import sqlite3
import logging
import pandas as pd
import asyncio
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
import io
import base64

# Telegram Bot Libraries
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Document
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError

# Data processing libraries
import requests
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'users.db')
DATA_DIR = os.getenv('DATA_DIRECTORY', '/Users/apple/Desktop/Data')
ADMIN_USERS = os.getenv('ADMIN_USERS', '').split(',') if os.getenv('ADMIN_USERS') else []

# Conversation States
MAIN_MENU, DATA_SOURCES, SEARCH, LOCATION, EXPORT, AUTH, ADMIN = range(7)

class EnhancedDataExplorerBot:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.data_dir = DATA_DIR
        self.user_sessions = {}
        self.rate_limits = {}
        self.init_database()
        self.load_config()
        
    def init_database(self):
        """Initialize database connection and tables"""
        try:
            conn = sqlite3.connect(self.db_path)
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
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def load_config(self):
        """Load bot configuration"""
        self.config = {
            "max_results_per_page": 10,
            "search_timeout": 30,
            "export_formats": ["csv", "excel", "json"],
            "rate_limits": {
                "search_per_minute": 10,
                "export_per_hour": 5,
                "messages_per_minute": 20
            },
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
    
    def check_rate_limit(self, user_id: int, action_type: str) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current window start time
            window_start = datetime.now() - timedelta(minutes=1)
            
            # Count actions in current window
            cursor.execute('''
                SELECT COUNT(*) FROM rate_limits 
                WHERE telegram_id = ? AND action_type = ? AND window_start > ?
            ''', (user_id, action_type, window_start))
            
            count = cursor.fetchone()[0]
            
            # Check against limits
            limits = self.config["rate_limits"]
            if action_type == "search" and count >= limits["search_per_minute"]:
                conn.close()
                return False
            elif action_type == "export" and count >= limits["export_per_hour"]:
                conn.close()
                return False
            elif action_type == "message" and count >= limits["messages_per_minute"]:
                conn.close()
                return False
            
            # Record this action
            cursor.execute('''
                INSERT INTO rate_limits (telegram_id, action_type, window_start)
                VALUES (?, ?, ?)
            ''', (user_id, action_type, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow action if check fails
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT total_searches, total_exports, created_at, last_active
                FROM users WHERE telegram_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    "total_searches": result[0],
                    "total_exports": result[1],
                    "created_at": result[2],
                    "last_active": result[3]
                }
            
            conn.close()
            return {}
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def update_user_stats(self, user_id: int, search_count: int = 0, export_count: int = 0):
        """Update user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET total_searches = total_searches + ?, 
                    total_exports = total_exports + ?,
                    last_active = CURRENT_TIMESTAMP
                WHERE telegram_id = ?
            ''', (search_count, export_count, user_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
    
    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create enhanced main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🏢 Data Sources", callback_data="data_sources"),
                InlineKeyboardButton("🔍 Search", callback_data="search")
            ],
            [
                InlineKeyboardButton("📍 Location Services", callback_data="location"),
                InlineKeyboardButton("📊 Export Data", callback_data="export")
            ],
            [
                InlineKeyboardButton("📈 Statistics", callback_data="stats"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]
        
        # Add admin menu for admin users
        if str(ADMIN_USERS) and any(str(user_id) in ADMIN_USERS for user_id in ADMIN_USERS):
            keyboard.append([
                InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_data_sources_keyboard(self, page: int = 0) -> InlineKeyboardMarkup:
        """Create paginated data sources keyboard"""
        sources = list(self.config["data_sources"].keys())
        sources_per_page = 6
        start_idx = page * sources_per_page
        end_idx = start_idx + sources_per_page
        page_sources = sources[start_idx:end_idx]
        
        keyboard = []
        
        # Create rows of 2 buttons each
        for i in range(0, len(page_sources), 2):
            row = []
            for j in range(2):
                if i + j < len(page_sources):
                    source = page_sources[i + j]
                    source_info = self.config["data_sources"][source]
                    row.append(InlineKeyboardButton(
                        f"📊 {source_info['name']}", 
                        callback_data=f"source_{source}"
                    ))
            keyboard.append(row)
        
        # Navigation buttons
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}"))
        if end_idx < len(sources):
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_search_keyboard(self) -> InlineKeyboardMarkup:
        """Create enhanced search options keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔍 Global Search", callback_data="global_search"),
                InlineKeyboardButton("🏢 Company Search", callback_data="company_search")
            ],
            [
                InlineKeyboardButton("📍 Location Search", callback_data="location_search"),
                InlineKeyboardButton("📞 Contact Search", callback_data="contact_search")
            ],
            [
                InlineKeyboardButton("🔤 Advanced Search", callback_data="advanced_search"),
                InlineKeyboardButton("📊 Search History", callback_data="search_history")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_location_keyboard(self) -> InlineKeyboardMarkup:
        """Create enhanced location services keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🏘️ Ward Information", callback_data="ward_info"),
                InlineKeyboardButton("📮 Pincode Lookup", callback_data="pincode_lookup")
            ],
            [
                InlineKeyboardButton("🏪 Local Suppliers", callback_data="local_suppliers"),
                InlineKeyboardButton("🗺️ Map Integration", callback_data="map_integration")
            ],
            [
                InlineKeyboardButton("📍 Nearby Services", callback_data="nearby_services"),
                InlineKeyboardButton("🚗 Directions", callback_data="directions")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_export_keyboard(self) -> InlineKeyboardMarkup:
        """Create enhanced export options keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📄 CSV Export", callback_data="csv_export"),
                InlineKeyboardButton("📊 Excel Export", callback_data="excel_export")
            ],
            [
                InlineKeyboardButton("📋 JSON Export", callback_data="json_export"),
                InlineKeyboardButton("📈 Report Generation", callback_data="report_generation")
            ],
            [
                InlineKeyboardButton("📊 Bulk Export", callback_data="bulk_export"),
                InlineKeyboardButton("📋 Export History", callback_data="export_history")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with enhanced features"""
        user = update.effective_user
        telegram_id = user.id
        
        # Create or update user
        await self.create_user(telegram_id, user)
        
        # Check if user is admin
        is_admin = str(telegram_id) in ADMIN_USERS
        
        welcome_message = f"""
🤖 **Welcome to Data Explorer Bot!**

Hello {user.first_name}! 👋

I'm your comprehensive data exploration assistant with advanced features:

🏢 **Browse Data Sources** - Access BAI, TCEA, CREDAI, RERA, and more
🔍 **Advanced Search** - Find companies, contacts, and locations
📍 **Location Services** - Ward info, pincodes, and local suppliers
📊 **Export Data** - Download CSV, Excel, and reports
📈 **Statistics** - View your usage and data insights

**New Features:**
• 🔍 Advanced search with filters
• 📊 Real-time statistics
• 📈 Usage analytics
• 🔧 Admin panel (for administrators)
• 📋 Search and export history

Choose an option below to get started:
        """
        
        if is_admin:
            welcome_message += "\n🔧 **Admin Access Detected** - You have access to admin features!"
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return MAIN_MENU
    
    async def create_user(self, telegram_id: int, user):
        """Create or update user in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (telegram_id, username, first_name, last_name, language_code, is_bot, last_active)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                telegram_id, 
                user.username, 
                user.first_name, 
                user.last_name,
                user.language_code,
                user.is_bot
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with comprehensive help"""
        help_text = """
📖 **Data Explorer Bot - Comprehensive Help**

**🚀 Main Features:**
🏢 **Data Sources** - Browse all available datasets
🔍 **Search** - Find specific information across all sources
📍 **Location Services** - Get location-based information
📊 **Export** - Download data in various formats
📈 **Statistics** - View usage analytics

**📊 Available Data Sources:**
• 🏗️ BAI Members (Builders Association of India)
• 🏛️ TCEA Members (Tamil Nadu Civil Engineers Association)
• 🏘️ CREDAI Members (Confederation of Real Estate Developers)
• 🏠 RERA Agents (Real Estate Regulatory Authority)
• 🏢 CCMC Contractors (Coimbatore City Municipal Corporation)
• 🏛️ Sub Registrar Offices
• 🎓 Educational Institutions
• 🏘️ NRLM Data (National Rural Livelihoods Mission)
• 🏘️ Ward Information (Coimbatore & Pollachi)
• 📮 Pincode Database
• 🏪 Local Suppliers

**🔍 Search Types:**
• **Global Search** - Search across all data sources
• **Company Search** - Find companies by name
• **Location Search** - Find by address/location
• **Contact Search** - Find by phone/email
• **Advanced Search** - Use filters and criteria

**📊 Export Formats:**
• **CSV** - Comma-separated values
• **Excel** - Microsoft Excel format
• **JSON** - JavaScript Object Notation
• **Reports** - Formatted reports

**🎯 Commands:**
/start - Start the bot and show main menu
/help - Show this help message
/menu - Return to main menu
/search - Quick search
/export - Quick export options
/stats - View your statistics
/admin - Admin panel (admin users only)

**💡 Tips:**
• Use inline keyboards for easy navigation
• Search is case-insensitive
• You can export data in multiple formats
• Location services work with pincodes and ward names
• Check your statistics to see usage patterns
• Rate limits apply to prevent abuse

**🔧 Admin Features:**
• View all user statistics
• Manage data sources
• Export system reports
• Monitor bot usage

Need more help? Contact the administrator.
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command"""
        await update.message.reply_text(
            "🏠 **Main Menu**\n\nChoose an option:",
            reply_markup=self.get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return MAIN_MENU
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        stats = self.get_user_stats(user_id)
        
        if stats:
            message = f"""
📈 **Your Statistics**

👤 **User Info:**
• Member since: {stats.get('created_at', 'Unknown')}
• Last active: {stats.get('last_active', 'Unknown')}

📊 **Usage Stats:**
• Total searches: {stats.get('total_searches', 0)}
• Total exports: {stats.get('total_exports', 0)}

🎯 **Activity Level:**
"""
            
            total_actions = stats.get('total_searches', 0) + stats.get('total_exports', 0)
            if total_actions == 0:
                message += "• 🆕 New user - Start exploring!"
            elif total_actions < 10:
                message += "• 🌱 Getting started"
            elif total_actions < 50:
                message += "• 📈 Active user"
            elif total_actions < 100:
                message += "• 🔥 Power user"
            else:
                message += "• 🏆 Super user"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Could not retrieve statistics. Please try again.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks with enhanced features"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # Check rate limits
        if not self.check_rate_limit(user_id, "message"):
            await query.edit_message_text(
                "⏰ **Rate Limit Exceeded**\n\nPlease wait a moment before trying again.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Handle pagination
        if data.startswith("page_"):
            page = int(data.split("_")[1])
            await query.edit_message_text(
                "🏢 **Data Sources**\n\nSelect a data source to explore:",
                reply_markup=self.get_data_sources_keyboard(page),
                parse_mode=ParseMode.MARKDOWN
            )
            return DATA_SOURCES
        
        # Handle data source selection
        if data.startswith("source_"):
            source = data[7:]  # Remove "source_" prefix (7 characters)
            await self.handle_data_source(query, source)
            return
        
        # Handle main menu navigation
        if data == "main_menu":
            await query.edit_message_text(
                "🏠 **Main Menu**\n\nChoose an option:",
                reply_markup=self.get_main_menu_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            return MAIN_MENU
            
        elif data == "data_sources":
            await query.edit_message_text(
                "🏢 **Data Sources**\n\nSelect a data source to explore:",
                reply_markup=self.get_data_sources_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            return DATA_SOURCES
            
        elif data == "search":
            await query.edit_message_text(
                "🔍 **Search Options**\n\nChoose search type:",
                reply_markup=self.get_search_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            return SEARCH
            
        elif data == "location":
            await query.edit_message_text(
                "📍 **Location Services**\n\nSelect location service:",
                reply_markup=self.get_location_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            return LOCATION
            
        elif data == "export":
            await query.edit_message_text(
                "📊 **Export Options**\n\nChoose export format:",
                reply_markup=self.get_export_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
            return EXPORT
            
        elif data == "stats":
            await self.stats_command(update, context)
            
        elif data == "help":
            await self.help_command(update, context)
            
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ **Settings**\n\nSettings will be available in future updates.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
            
        elif data == "admin_panel":
            if str(user_id) in ADMIN_USERS:
                await self.show_admin_panel(query)
            else:
                await query.edit_message_text(
                    "❌ **Access Denied**\n\nYou don't have admin privileges.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                    ]]),
                    parse_mode=ParseMode.MARKDOWN
                )
        
        # Handle data source selections (these are handled by the source_ prefix handler above)
            
        # Handle search options
        elif data in ["global_search", "company_search", "location_search", "contact_search"]:
            await self.handle_search_option(query, data)
            
        # Handle location services
        elif data in ["ward_info", "pincode_lookup", "local_suppliers", "map_integration"]:
            await self.handle_location_service(query, data)
            
        # Handle export options
        elif data in ["csv_export", "excel_export", "json_export", "report_generation"]:
            await self.handle_export_option(query, data)
            
        # Handle specific export actions
        elif data.startswith("export_csv_"):
            source = data[11:]  # Remove "export_csv_" prefix
            await self.export_data(query, source, "csv")
        elif data.startswith("export_excel_"):
            source = data[13:]  # Remove "export_excel_" prefix
            await self.export_data(query, source, "excel")
        elif data.startswith("export_json_"):
            source = data[12:]  # Remove "export_json_" prefix
            await self.export_data(query, source, "json")
    
    async def handle_search_option(self, query, search_type: str):
        """Handle search option selection"""
        search_types = {
            "global_search": "Global Search",
            "company_search": "Company Search",
            "location_search": "Location Search",
            "contact_search": "Contact Search"
        }
        
        search_name = search_types.get(search_type, search_type)
        
        await query.edit_message_text(
            f"🔍 **{search_name}**\n\n"
            f"Please enter your search query. I'll search across all available data sources.\n\n"
            f"**Examples:**\n"
            f"• Company name\n"
            f"• Contact person\n"
            f"• Location/address\n"
            f"• Phone number\n\n"
            f"Type your search query:",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SEARCH
    
    async def handle_location_service(self, query, service_type: str):
        """Handle location service selection"""
        service_types = {
            "ward_info": "Ward Information",
            "pincode_lookup": "Pincode Lookup",
            "local_suppliers": "Local Suppliers",
            "map_integration": "Map Integration"
        }
        
        service_name = service_types.get(service_type, service_type)
        
        if service_type == "ward_info":
            await query.edit_message_text(
                f"🏘️ **{service_name}**\n\n"
                f"Available ward information:\n"
                f"• Coimbatore Wards\n"
                f"• Pollachi Wards\n\n"
                f"Select ward type:",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🏘️ Coimbatore Wards", callback_data="cbe_wards"),
                        InlineKeyboardButton("🏘️ Pollachi Wards", callback_data="pollachi_wards")
                    ],
                    [
                        InlineKeyboardButton("🔙 Back to Location Services", callback_data="location")
                    ]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
        elif service_type == "pincode_lookup":
            await query.edit_message_text(
                f"📮 **{service_name}**\n\n"
                f"Enter a pincode to get location information.\n\n"
                f"**Example:** 641001\n\n"
                f"Type the pincode:",
                parse_mode=ParseMode.MARKDOWN
            )
        elif service_type == "local_suppliers":
            await query.edit_message_text(
                f"🏪 **{service_name}**\n\n"
                f"Find local suppliers by pincode.\n\n"
                f"**Example:** 641001\n\n"
                f"Type the pincode:",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"🗺️ **{service_name}**\n\n"
                f"This feature will be available in future updates.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Location Services", callback_data="location")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_export_option(self, query, export_type: str):
        """Handle export option selection"""
        export_types = {
            "csv_export": "CSV Export",
            "excel_export": "Excel Export", 
            "json_export": "JSON Export",
            "report_generation": "Report Generation"
        }
        
        export_name = export_types.get(export_type, export_type)
        
        await query.edit_message_text(
            f"📊 **{export_name}**\n\n"
            f"Select data source to export:",
            reply_markup=self.get_data_sources_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def export_data(self, query, data_source: str, export_format: str):
        """Export data in specified format"""
        try:
            # Check if data source exists
            if data_source not in self.config["data_sources"]:
                await query.edit_message_text(
                    "❌ **Error**\n\nInvalid data source selected.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Export", callback_data="export")
                    ]]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            source_info = self.config["data_sources"][data_source]
            source_name = source_info["name"]
            
            # Load data
            loaded_data = await self.load_data_source(data_source)
            
            if not loaded_data:
                await query.edit_message_text(
                    f"❌ **Error**\n\nCould not load {source_name} data.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Export", callback_data="export")
                    ]]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Show processing message
            await query.edit_message_text(
                f"📊 **Exporting {source_name}**\n\n"
                f"Format: {export_format.upper()}\n"
                f"Records: {len(loaded_data)}\n\n"
                f"⏳ Processing...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Create export based on format
            if export_format == "csv":
                file_content = await self.create_csv_export(loaded_data, source_name)
                filename = f"{data_source}_export.csv"
            elif export_format == "excel":
                file_content = await self.create_excel_export(loaded_data, source_name)
                filename = f"{data_source}_export.xlsx"
            elif export_format == "json":
                file_content = await self.create_json_export(loaded_data, source_name)
                filename = f"{data_source}_export.json"
            else:
                await query.edit_message_text(
                    f"❌ **Error**\n\nUnsupported export format: {export_format}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Export", callback_data="export")
                    ]]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send file to user
            await query.message.reply_document(
                document=file_content,
                filename=filename,
                caption=f"📊 **{source_name} Export**\n\n"
                       f"Format: {export_format.upper()}\n"
                       f"Records: {len(loaded_data)}\n"
                       f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Update user statistics
            self.update_user_stats(query.from_user.id, export_count=1)
            
            # Record export in history
            await self.record_export(query.from_user.id, data_source, export_format, len(loaded_data))
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            await query.edit_message_text(
                f"❌ **Export Error**\n\nAn error occurred while exporting data.\n\nError: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Export", callback_data="export")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def create_csv_export(self, data: List[Dict], source_name: str) -> io.BytesIO:
        """Create CSV export"""
        import csv
        
        output = io.StringIO()
        
        if data and isinstance(data[0], dict):
            # Get all unique keys from all records
            all_keys = set()
            for record in data:
                if isinstance(record, dict):
                    all_keys.update(record.keys())
            
            fieldnames = sorted(list(all_keys))
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in data:
                if isinstance(record, dict):
                    writer.writerow(record)
        
        # Convert to BytesIO
        csv_content = output.getvalue()
        output.close()
        
        file_obj = io.BytesIO()
        file_obj.write(csv_content.encode('utf-8'))
        file_obj.seek(0)
        
        return file_obj
    
    async def create_excel_export(self, data: List[Dict], source_name: str) -> io.BytesIO:
        """Create Excel export"""
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=source_name, index=False)
        
        output.seek(0)
        return output
    
    async def create_json_export(self, data: List[Dict], source_name: str) -> io.BytesIO:
        """Create JSON export"""
        export_data = {
            "source": source_name,
            "exported_at": datetime.now().isoformat(),
            "total_records": len(data),
            "data": data
        }
        
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        file_obj = io.BytesIO()
        file_obj.write(json_content.encode('utf-8'))
        file_obj.seek(0)
        
        return file_obj
    
    async def record_export(self, user_id: int, data_source: str, export_format: str, record_count: int):
        """Record export in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO export_history (telegram_id, data_source, export_format, file_size)
                VALUES (?, ?, ?, ?)
            ''', (user_id, data_source, export_format, record_count))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording export: {e}")

    async def handle_data_source(self, query, data_source: str):
        """Handle data source selection with enhanced features"""
        if data_source not in self.config["data_sources"]:
            await query.edit_message_text(
                "❌ **Error**\n\nInvalid data source selected.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Data Sources", callback_data="data_sources")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        source_info = self.config["data_sources"][data_source]
        source_name = source_info["name"]
        
        # Load data from JSON files
        loaded_data = await self.load_data_source(data_source)
        
        if loaded_data:
            # Ensure loaded_data is a list
            if isinstance(loaded_data, dict):
                # If it's still a dict, try to extract data
                if 'data' in loaded_data:
                    loaded_data = loaded_data['data']
                elif 'members' in loaded_data:
                    loaded_data = loaded_data['members']
                elif 'records' in loaded_data:
                    loaded_data = loaded_data['records']
                elif 'results' in loaded_data:
                    loaded_data = loaded_data['results']
                else:
                    loaded_data = [loaded_data]
            
            # Show summary and options
            total_records = len(loaded_data)
            message = f"📊 **{source_name}**\n\n"
            message += f"📈 Total Records: {total_records}\n\n"
            
            if total_records > 0:
                # Show sample data with better formatting
                sample = loaded_data[:3]  # Show first 3 records
                message += "📋 **Sample Records:**\n\n"
                
                for i, record in enumerate(sample, 1):
                    message += f"**{i}.** "
                    if isinstance(record, dict):
                        # Show key fields based on data source
                        if 'company_name' in record:
                            name = record.get('company_name', 'N/A')
                            contact = record.get('contact_person', 'N/A')
                            message += f"{name}\n   👤 Contact: {contact}\n"
                        elif 'name' in record:
                            name = record.get('name', 'N/A')
                            message += f"{name}\n"
                        elif 'institution_name' in record:
                            name = record.get('institution_name', 'N/A')
                            message += f"{name}\n"
                        else:
                            message += f"Record {i}\n"
                    else:
                        message += f"Record {i}\n"
                
                if total_records > 3:
                    message += f"\n... and {total_records - 3} more records"
            
            # Add action buttons
            keyboard = [
                [
                    InlineKeyboardButton("🔍 Search", callback_data=f"search_{data_source}"),
                    InlineKeyboardButton("📊 View All", callback_data=f"view_all_{data_source}")
                ],
                [
                    InlineKeyboardButton("📄 Export CSV", callback_data=f"export_csv_{data_source}"),
                    InlineKeyboardButton("📊 Export Excel", callback_data=f"export_excel_{data_source}")
                ],
                [
                    InlineKeyboardButton("📋 Export JSON", callback_data=f"export_json_{data_source}"),
                    InlineKeyboardButton("📈 Generate Report", callback_data=f"report_{data_source}")
                ],
                [
                    InlineKeyboardButton("🔙 Back to Data Sources", callback_data="data_sources")
                ]
            ]
            
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"❌ **Error**\n\nCould not load {source_name} data. Please try again later.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Data Sources", callback_data="data_sources")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def load_data_source(self, data_source: str) -> Optional[List[Dict]]:
        """Load data from JSON files with error handling"""
        try:
            if data_source not in self.config["data_sources"]:
                return None
            
            source_info = self.config["data_sources"][data_source]
            filename = source_info["file"]
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    raw_data = json.loads(content)
                    
                    # Handle different JSON structures
                    if isinstance(raw_data, list):
                        # Direct array of records
                        return raw_data
                    elif isinstance(raw_data, dict):
                        # Object with metadata - look for common keys
                        if 'members' in raw_data:
                            return raw_data['members']
                        elif 'data' in raw_data:
                            return raw_data['data']
                        elif 'records' in raw_data:
                            return raw_data['records']
                        elif 'results' in raw_data:
                            return raw_data['results']
                        else:
                            # Return the dict itself as a single record
                            return [raw_data]
                    else:
                        logger.warning(f"Unexpected data type in {filename}: {type(raw_data)}")
                        return None
            else:
                logger.warning(f"File not found: {filepath}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading data source {data_source}: {e}")
            return None
    
    async def show_admin_panel(self, query):
        """Show admin panel for admin users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get system statistics
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM search_history')
            total_searches = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM export_history')
            total_exports = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE last_active > datetime("now", "-24 hours")')
            active_users_24h = cursor.fetchone()[0]
            
            conn.close()
            
            message = f"""
🔧 **Admin Panel**

📊 **System Statistics:**
• Total Users: {total_users}
• Total Searches: {total_searches}
• Total Exports: {total_exports}
• Active Users (24h): {active_users_24h}

🎯 **Quick Actions:**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("👥 User Management", callback_data="admin_users"),
                    InlineKeyboardButton("📊 System Reports", callback_data="admin_reports")
                ],
                [
                    InlineKeyboardButton("🔍 Search Analytics", callback_data="admin_search"),
                    InlineKeyboardButton("📤 Export Analytics", callback_data="admin_export")
                ],
                [
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]
            ]
            
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error showing admin panel: {e}")
            await query.edit_message_text(
                "❌ **Error**\n\nCould not load admin panel. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]]),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with enhanced search"""
        user_id = update.effective_user.id
        text = update.message.text
        self.update_user_activity(user_id)
        
        # Check rate limits
        if not self.check_rate_limit(user_id, "search"):
            await update.message.reply_text(
                "⏰ **Rate Limit Exceeded**\n\nPlease wait a moment before searching again.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Handle search queries
        if len(text) > 0:
            await self.perform_enhanced_search(update, text)
    
    async def perform_enhanced_search(self, update: Update, query: str):
        """Perform enhanced search across all data sources"""
        await update.message.reply_text(f"🔍 Searching for: **{query}**\n\nPlease wait...", parse_mode=ParseMode.MARKDOWN)
        
        results = []
        search_stats = {}
        
        # Search across all data sources
        for source, source_info in self.config["data_sources"].items():
            data = await self.load_data_source(source)
            if data:
                matches = self.search_in_data(data, query)
                if matches:
                    results.extend(matches[:5])  # Limit to 5 results per source
                    search_stats[source_info["name"]] = len(matches)
        
        # Update user statistics
        self.update_user_stats(update.effective_user.id, search_count=1)
        
        # Record search in history
        await self.record_search(update.effective_user.id, query, len(results))
        
        if results:
            message = f"🔍 **Search Results for: {query}**\n\n"
            message += f"📊 Found {len(results)} matches across {len(search_stats)} sources\n\n"
            
            # Show source breakdown
            if search_stats:
                message += "📈 **Results by Source:**\n"
                for source, count in search_stats.items():
                    message += f"• {source}: {count} matches\n"
                message += "\n"
            
            # Show first 10 results with better formatting
            for i, result in enumerate(results[:10], 1):
                message += f"**{i}.** "
                if isinstance(result, dict):
                    if 'company_name' in result:
                        name = result.get('company_name', 'N/A')
                        contact = result.get('contact_person', 'N/A')
                        phone = result.get('phone', 'N/A')
                        message += f"{name}\n   👤 {contact} | 📞 {phone}\n"
                    elif 'name' in result:
                        name = result.get('name', 'N/A')
                        message += f"{name}\n"
                    elif 'institution_name' in result:
                        name = result.get('institution_name', 'N/A')
                        message += f"{name}\n"
                    else:
                        message += f"Match {i}\n"
                else:
                    message += f"Match {i}\n"
            
            if len(results) > 10:
                message += f"\n... and {len(results) - 10} more results"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"❌ No results found for: **{query}**", parse_mode=ParseMode.MARKDOWN)
    
    def search_in_data(self, data: List[Dict], query: str) -> List[Dict]:
        """Enhanced search in data with better matching"""
        matches = []
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for item in data:
            if isinstance(item, dict):
                # Search in all string values
                match_score = 0
                for value in item.values():
                    if isinstance(value, str):
                        value_lower = value.lower()
                        # Exact match gets highest score
                        if query_lower in value_lower:
                            match_score += 10
                        # Word-based matching
                        for word in query_words:
                            if word in value_lower:
                                match_score += 1
                
                if match_score > 0:
                    item['_match_score'] = match_score
                    matches.append(item)
        
        # Sort by match score
        matches.sort(key=lambda x: x.get('_match_score', 0), reverse=True)
        return matches
    
    async def record_search(self, user_id: int, query: str, results_count: int):
        """Record search in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_history (telegram_id, query, results_count)
                VALUES (?, ?, ?)
            ''', (user_id, query, results_count))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording search: {e}")
    
    def update_user_activity(self, user_id: int):
        """Update user's last active timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_active = CURRENT_TIMESTAMP 
                WHERE telegram_id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")

def main():
    """Main function to run the enhanced bot"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your TELEGRAM_BOT_TOKEN environment variable")
        print("Get your bot token from @BotFather on Telegram")
        print("Run: python bot_setup.py to configure the bot")
        return
    
    # Create bot instance
    bot = EnhancedDataExplorerBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("menu", bot.menu_command))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start the bot
    print("🤖 Starting Enhanced Data Explorer Telegram Bot...")
    print("Press Ctrl+C to stop the bot")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == '__main__':
    main()
