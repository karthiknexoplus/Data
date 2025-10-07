#!/usr/bin/env python3
"""
Comprehensive Telegram Bot for Data Explorer Project
Integrates all features from the web application into a Telegram bot interface
"""

import os
import json
import sqlite3
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import aiofiles

# Telegram Bot Libraries
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from telegram.constants import ParseMode

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
DATABASE_PATH = 'users.db'
DATA_DIR = '/Users/apple/Desktop/Data'

# Conversation States
MAIN_MENU, DATA_SOURCES, SEARCH, LOCATION, EXPORT, AUTH = range(6)

class DataExplorerBot:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.data_dir = DATA_DIR
        self.user_sessions = {}  # Store user session data
        self.init_database()
        
    def init_database(self):
        """Initialize database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def get_user_data(self, telegram_id: int) -> Optional[Dict]:
        """Get user data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'telegram_id': user[1],
                    'username': user[2],
                    'created_at': user[3],
                    'last_active': user[4]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None
    
    def create_user(self, telegram_id: int, username: str = None) -> bool:
        """Create new user in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, last_active)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (telegram_id, username))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def update_user_activity(self, telegram_id: int):
        """Update user's last active timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_active = CURRENT_TIMESTAMP 
                WHERE telegram_id = ?
            ''', (telegram_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create main menu keyboard"""
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
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_data_sources_keyboard(self) -> InlineKeyboardMarkup:
        """Create data sources submenu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🏗️ BAI Members", callback_data="bai_members"),
                InlineKeyboardButton("🏛️ TCEA Members", callback_data="tcea_members")
            ],
            [
                InlineKeyboardButton("🏘️ CREDAI Members", callback_data="credai_members"),
                InlineKeyboardButton("🏠 RERA Agents", callback_data="rera_agents")
            ],
            [
                InlineKeyboardButton("🏢 CCMC Contractors", callback_data="ccmc_contractors"),
                InlineKeyboardButton("🏛️ Sub Registrar Offices", callback_data="sr_offices")
            ],
            [
                InlineKeyboardButton("🎓 Educational Institutions", callback_data="colleges"),
                InlineKeyboardButton("🏘️ NRLM Data", callback_data="nrlm_data")
            ],
            [
                InlineKeyboardButton("🏘️ Coimbatore Wards", callback_data="cbe_wards"),
                InlineKeyboardButton("🏘️ Pollachi Wards", callback_data="pollachi_wards")
            ],
            [
                InlineKeyboardButton("📮 Pincodes", callback_data="pincodes"),
                InlineKeyboardButton("🏪 Suppliers", callback_data="suppliers")
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_search_keyboard(self) -> InlineKeyboardMarkup:
        """Create search options keyboard"""
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
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_location_keyboard(self) -> InlineKeyboardMarkup:
        """Create location services keyboard"""
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
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_export_keyboard(self) -> InlineKeyboardMarkup:
        """Create export options keyboard"""
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
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        telegram_id = user.id
        
        # Create or update user
        self.create_user(telegram_id, user.username)
        self.update_user_activity(telegram_id)
        
        welcome_message = f"""
🤖 **Welcome to Data Explorer Bot!**

Hello {user.first_name}! 👋

I'm your comprehensive data exploration assistant. I can help you:

🏢 **Browse Data Sources** - Access BAI, TCEA, CREDAI, RERA, and more
🔍 **Search Information** - Find companies, contacts, and locations
📍 **Location Services** - Ward info, pincodes, and local suppliers
📊 **Export Data** - Download CSV, Excel, and reports

Choose an option below to get started:
        """
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return MAIN_MENU
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 **Data Explorer Bot Help**

**Main Features:**
🏢 **Data Sources** - Browse all available datasets
🔍 **Search** - Find specific information across all sources
📍 **Location Services** - Get location-based information
📊 **Export** - Download data in various formats

**Available Data Sources:**
• BAI Members (Builders Association of India)
• TCEA Members (Tamil Nadu Civil Engineers Association)
• CREDAI Members (Confederation of Real Estate Developers)
• RERA Agents (Real Estate Regulatory Authority)
• CCMC Contractors (Coimbatore City Municipal Corporation)
• Sub Registrar Offices
• Educational Institutions
• NRLM Data (National Rural Livelihoods Mission)
• Ward Information (Coimbatore & Pollachi)
• Pincode Database
• Local Suppliers

**Commands:**
/start - Start the bot and show main menu
/help - Show this help message
/menu - Return to main menu
/search - Quick search
/export - Quick export options

**Tips:**
• Use the inline keyboards for easy navigation
• Search is case-insensitive
• You can export data in CSV, Excel, or JSON formats
• Location services work with pincodes and ward names

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
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        self.update_user_activity(user_id)
        
        # Handle data source selection with source_ prefix
        if data.startswith("source_"):
            source = data[7:]  # Remove "source_" prefix (7 characters)
            await self.handle_data_source(query, source)
            return
        
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
            source_names = {
                "bai_members": "BAI Members",
                "tcea_members": "TCEA Members", 
                "credai_members": "CREDAI Members",
                "rera_agents": "RERA Agents",
                "ccmc_contractors": "CCMC Contractors",
                "sr_offices": "Sub Registrar Offices",
                "colleges": "Educational Institutions",
                "nrlm_data": "NRLM Data",
                "cbe_wards": "Coimbatore Wards",
                "pollachi_wards": "Pollachi Wards",
                "pincodes": "Pincodes",
                "suppliers": "Suppliers"
            }
            
            if data_source not in source_names:
                await query.edit_message_text(
                    "❌ **Error**\n\nInvalid data source selected.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Export", callback_data="export")
                    ]]),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            source_name = source_names[data_source]
            
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

    async def handle_data_source(self, query, data_source: str):
        """Handle data source selection"""
        source_names = {
            "bai_members": "BAI Members",
            "tcea_members": "TCEA Members", 
            "credai_members": "CREDAI Members",
            "rera_agents": "RERA Agents",
            "ccmc_contractors": "CCMC Contractors",
            "sr_offices": "Sub Registrar Offices",
            "colleges": "Educational Institutions",
            "nrlm_data": "NRLM Data",
            "cbe_wards": "Coimbatore Wards",
            "pollachi_wards": "Pollachi Wards",
            "pincodes": "Pincodes",
            "suppliers": "Suppliers"
        }
        
        source_name = source_names.get(data_source, data_source)
        
        # Load data from JSON files
        loaded_data = await self.load_data_source(data_source)
        
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
        
        if loaded_data:
            # Show summary and options
            total_records = len(loaded_data)
            message = f"📊 **{source_name}**\n\n"
            message += f"📈 Total Records: {total_records}\n\n"
            
            if total_records > 0:
                # Show sample data
                sample = loaded_data[:3]  # Show first 3 records
                message += "📋 **Sample Records:**\n\n"
                
                for i, record in enumerate(sample, 1):
                    message += f"**{i}.** "
                    if isinstance(record, dict):
                        # Show key fields based on data source
                        if 'company_name' in record:
                            message += f"{record.get('company_name', 'N/A')}\n"
                        elif 'name' in record:
                            message += f"{record.get('name', 'N/A')}\n"
                        elif 'institution_name' in record:
                            message += f"{record.get('institution_name', 'N/A')}\n"
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
        """Load data from JSON files"""
        try:
            file_mapping = {
                "bai_members": "bai_members_comprehensive.json",
                "tcea_members": "tcea_complete_data.json",
                "credai_members": "credai_members.json",
                "rera_agents": "rera_agents_improved.json",
                "ccmc_contractors": "ccmc_contractors.json",
                "sr_offices": "sub_reg_offices.json",
                "colleges": "edu_list_tn.json",
                "nrlm_data": "nrlm_data.json",
                "cbe_wards": "coimbatore_wards.json",
                "pollachi_wards": "pollachi_wards.json",
                "pincodes": "pincodes.json",
                "suppliers": "suppliers_cache/suppliers_641016.json"
            }
            
            filename = file_mapping.get(data_source)
            if not filename:
                return None
            
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
        
        # Store search type in context for later use
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
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text
        self.update_user_activity(user_id)
        
        # Handle search queries
        if len(text) > 0:
            await self.perform_search(update, text)
    
    async def perform_search(self, update: Update, query: str):
        """Perform search across all data sources"""
        await update.message.reply_text(f"🔍 Searching for: **{query}**\n\nPlease wait...", parse_mode=ParseMode.MARKDOWN)
        
        results = []
        
        # Search across all data sources
        data_sources = [
            "bai_members", "tcea_members", "credai_members", "rera_agents",
            "ccmc_contractors", "sr_offices", "colleges", "cbe_wards", 
            "pollachi_wards", "pincodes"
        ]
        
        for source in data_sources:
            data = await self.load_data_source(source)
            if data:
                matches = self.search_in_data(data, query)
                if matches:
                    results.extend(matches[:5])  # Limit to 5 results per source
        
        if results:
            message = f"🔍 **Search Results for: {query}**\n\n"
            message += f"📊 Found {len(results)} matches\n\n"
            
            # Show first 10 results
            for i, result in enumerate(results[:10], 1):
                message += f"**{i}.** "
                if isinstance(result, dict):
                    if 'company_name' in result:
                        message += f"{result.get('company_name', 'N/A')}\n"
                    elif 'name' in result:
                        message += f"{result.get('name', 'N/A')}\n"
                    elif 'institution_name' in result:
                        message += f"{result.get('institution_name', 'N/A')}\n"
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
        """Search for query in data"""
        matches = []
        query_lower = query.lower()
        
        for item in data:
            if isinstance(item, dict):
                # Search in all string values
                for value in item.values():
                    if isinstance(value, str) and query_lower in value.lower():
                        matches.append(item)
                        break
        
        return matches

def main():
    """Main function to run the bot"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your TELEGRAM_BOT_TOKEN environment variable")
        print("Get your bot token from @BotFather on Telegram")
        return
    
    # Create bot instance
    bot = DataExplorerBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("menu", bot.menu_command))
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start the bot
    print("🤖 Starting Data Explorer Telegram Bot...")
    print("Press Ctrl+C to stop the bot")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == '__main__':
    main()
