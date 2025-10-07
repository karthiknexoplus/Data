# 🤖 Data Explorer Telegram Bot

A comprehensive Telegram bot that provides access to all features from the Data Explorer web application through an intuitive chat interface.

## 🚀 Features

### 📊 Data Sources
- **BAI Members** - Builders Association of India members
- **TCEA Members** - Tamil Nadu Civil Engineers Association members
- **CREDAI Members** - Confederation of Real Estate Developers members
- **RERA Agents** - Real Estate Regulatory Authority agents
- **CCMC Contractors** - Coimbatore City Municipal Corporation contractors
- **Sub Registrar Offices** - Government registration offices
- **Educational Institutions** - Colleges and universities
- **NRLM Data** - National Rural Livelihoods Mission data
- **Ward Information** - Coimbatore and Pollachi ward details
- **Pincode Database** - Complete pincode information
- **Local Suppliers** - Construction material suppliers

### 🔍 Search Capabilities
- **Global Search** - Search across all data sources
- **Company Search** - Find companies by name
- **Location Search** - Find by address/location
- **Contact Search** - Find by phone/email
- **Advanced Search** - Use filters and criteria
- **Search History** - View your previous searches

### 📍 Location Services
- **Ward Information** - Get ward details and boundaries
- **Pincode Lookup** - Find location by pincode
- **Local Suppliers** - Find suppliers by pincode
- **Map Integration** - Location-based services
- **Nearby Services** - Find nearby businesses
- **Directions** - Get directions to locations

### 📊 Export Options
- **CSV Export** - Download data in CSV format
- **Excel Export** - Download data in Excel format
- **JSON Export** - Download data in JSON format
- **Report Generation** - Generate formatted reports
- **Bulk Export** - Export multiple data sources
- **Export History** - View your export history

### 📈 Analytics & Statistics
- **User Statistics** - View your usage patterns
- **Search Analytics** - Track search performance
- **Export Analytics** - Monitor export activities
- **System Reports** - Admin-level insights

### 🔧 Admin Features
- **User Management** - Manage bot users
- **System Reports** - View system statistics
- **Search Analytics** - Monitor search patterns
- **Export Analytics** - Track export usage

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- All data files from the main project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Bot
```bash
python bot_setup.py
```

### 3. Set Environment Variables
Create a `.env` file with your bot token:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_PATH=users.db
DATA_DIRECTORY=/Users/apple/Desktop/Data
ADMIN_USERS=123456789,987654321
```

### 4. Run the Bot
```bash
python enhanced_telegram_bot.py
```

## 📱 Usage

### Getting Started
1. Start a chat with your bot on Telegram
2. Send `/start` to begin
3. Use the inline keyboard to navigate
4. Explore data sources, search, and export data

### Commands
- `/start` - Start the bot and show main menu
- `/help` - Show comprehensive help
- `/menu` - Return to main menu
- `/stats` - View your usage statistics
- `/admin` - Admin panel (admin users only)

### Navigation
The bot uses inline keyboards for easy navigation:
- **Main Menu** - Access all features
- **Data Sources** - Browse available datasets
- **Search** - Find information
- **Location Services** - Location-based features
- **Export** - Download data
- **Statistics** - View analytics

## 🎯 Key Features

### 🔍 Advanced Search
- **Case-insensitive** search across all data sources
- **Word-based matching** for better results
- **Match scoring** to rank results by relevance
- **Search history** to track your queries
- **Rate limiting** to prevent abuse

### 📊 Data Export
- **Multiple formats** - CSV, Excel, JSON
- **Bulk export** - Export multiple sources at once
- **Report generation** - Create formatted reports
- **Export history** - Track your downloads
- **File size limits** - Optimized for Telegram

### 📍 Location Services
- **Pincode lookup** - Find locations by pincode
- **Ward information** - Get ward details
- **Local suppliers** - Find nearby suppliers
- **Map integration** - Location-based services
- **Geographic data** - Coordinate information

### 🔧 Admin Panel
- **User management** - Monitor bot users
- **System statistics** - View usage metrics
- **Search analytics** - Track search patterns
- **Export analytics** - Monitor downloads
- **Rate limiting** - Manage user limits

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
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
);
```

### Search History Table
```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    results_count INTEGER DEFAULT 0,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);
```

### Export History Table
```sql
CREATE TABLE export_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    data_source TEXT NOT NULL,
    export_format TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    export_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);
```

## 🔒 Security Features

### Rate Limiting
- **Search limits** - 10 searches per minute
- **Export limits** - 5 exports per hour
- **Message limits** - 20 messages per minute
- **Automatic blocking** - Temporary restrictions

### User Management
- **User registration** - Automatic user creation
- **Session tracking** - Monitor user activity
- **Admin privileges** - Restricted admin access
- **Activity logging** - Track user behavior

### Data Protection
- **Input validation** - Sanitize user inputs
- **SQL injection prevention** - Parameterized queries
- **Error handling** - Graceful error management
- **Logging** - Comprehensive activity logs

## 📊 Performance Optimization

### Data Loading
- **Async file operations** - Non-blocking file reads
- **Caching** - Store frequently accessed data
- **Lazy loading** - Load data on demand
- **Memory management** - Efficient data handling

### Search Optimization
- **Indexed search** - Fast data retrieval
- **Match scoring** - Relevant result ranking
- **Result limiting** - Prevent memory overflow
- **Parallel processing** - Concurrent searches

### Export Optimization
- **Streaming exports** - Handle large datasets
- **Format optimization** - Efficient file formats
- **Compression** - Reduce file sizes
- **Batch processing** - Process multiple exports

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Configure bot
python bot_setup.py

# Run bot
python enhanced_telegram_bot.py
```

### Production Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export DATABASE_PATH=/path/to/database.db
export DATA_DIRECTORY=/path/to/data

# Run with process manager
pm2 start enhanced_telegram_bot.py --name "data-explorer-bot"
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "enhanced_telegram_bot.py"]
```

## 🔧 Configuration

### Bot Configuration
```json
{
  "max_results_per_page": 10,
  "search_timeout": 30,
  "export_formats": ["csv", "excel", "json"],
  "rate_limits": {
    "search_per_minute": 10,
    "export_per_hour": 5,
    "messages_per_minute": 20
  },
  "features": {
    "search_enabled": true,
    "export_enabled": true,
    "location_services": true
  }
}
```

### Environment Variables
```env
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_PATH=users.db
DATA_DIRECTORY=/path/to/data
ADMIN_USERS=123456789,987654321
LOG_LEVEL=INFO
WEBHOOK_URL=https://yourdomain.com/webhook
```

## 📈 Monitoring & Analytics

### User Analytics
- **User registration** - Track new users
- **Active users** - Monitor daily active users
- **Usage patterns** - Analyze user behavior
- **Feature adoption** - Track feature usage

### System Analytics
- **Search performance** - Monitor search speed
- **Export statistics** - Track download volumes
- **Error rates** - Monitor system health
- **Resource usage** - Track system resources

### Business Intelligence
- **Data source popularity** - Most accessed sources
- **Search trends** - Popular search terms
- **Export patterns** - Common export formats
- **User engagement** - User activity metrics

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot token
echo $TELEGRAM_BOT_TOKEN

# Check database connection
python -c "import sqlite3; conn = sqlite3.connect('users.db'); print('OK')"

# Check data files
ls -la /Users/apple/Desktop/Data/*.json
```

#### Search Not Working
```bash
# Check data file permissions
ls -la /Users/apple/Desktop/Data/

# Validate JSON files
python -c "import json; json.load(open('bai_members_comprehensive.json'))"
```

#### Export Issues
```bash
# Check file permissions
chmod 755 /Users/apple/Desktop/Data/

# Check disk space
df -h
```

### Log Analysis
```bash
# View bot logs
tail -f bot.log

# Check error logs
grep ERROR bot.log

# Monitor performance
grep "search_time" bot.log
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd data-explorer-bot

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run bot
python enhanced_telegram_bot.py
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings
- Write tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Telegram Bot API** - For the excellent bot framework
- **Data Sources** - All the organizations providing data
- **Contributors** - Everyone who helped build this project

## 📞 Support

For support and questions:
- **Issues** - Create an issue on GitHub
- **Documentation** - Check the README and help commands
- **Admin** - Contact admin users for assistance

---

**Made with ❤️ for the Data Explorer community**
