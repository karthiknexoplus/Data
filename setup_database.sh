#!/bin/bash

# Database Setup Script for the Data Application
# This script provides multiple ways to create the database

echo "=========================================="
echo "Database Setup Script"
echo "=========================================="

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "Python3 found. Running Python database creation script..."
    python3 create_database.py
elif command -v python &> /dev/null; then
    echo "Python found. Running Python database creation script..."
    python create_database.py
else
    echo "Python not found. Using SQLite directly..."
    
    # Remove existing database if it exists
    if [ -f "users.db" ]; then
        echo "Removing existing database: users.db"
        rm users.db
    fi
    
    # Create database using SQL script
    echo "Creating database using SQL script..."
    sqlite3 users.db < create_database.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Database created successfully using SQLite!"
    else
        echo "❌ Failed to create database"
        exit 1
    fi
fi

echo ""
echo "Database setup complete!"
echo "You can now run your Flask application."
