#!/usr/bin/env python3
"""
Database Creation Script for the Data Application
This script creates all necessary tables for the application.
"""

import sqlite3
import os
import sys
from datetime import datetime

def create_database(db_name='users.db'):
    """
    Create the database with all necessary tables
    """
    # Remove existing database if it exists
    if os.path.exists(db_name):
        print(f"Removing existing database: {db_name}")
        os.remove(db_name)
    
    # Create new database
    print(f"Creating new database: {db_name}")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Users table - for authentication
        print("Creating users table...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Colleges table - for educational institutions data
        print("Creating colleges table...")
        cursor.execute('''
            CREATE TABLE colleges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                s_no TEXT,
                member_code TEXT UNIQUE,
                institution_name TEXT NOT NULL,
                year_established TEXT,
                contact_no TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # NRLM Data table - for National Rural Livelihoods Mission data
        print("Creating nrlm_data table...")
        cursor.execute('''
            CREATE TABLE nrlm_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_code TEXT,
                state_name TEXT,
                district_code TEXT,
                district_name TEXT,
                block_code TEXT,
                block_name TEXT,
                grampanchayat_code TEXT,
                grampanchayat_name TEXT,
                village_code TEXT,
                village_name TEXT,
                shg_name TEXT,
                member_name TEXT,
                member_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # BAI Members table - for Builders Association of India members
        print("Creating bai_members table...")
        cursor.execute('''
            CREATE TABLE bai_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                source_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # DCE Colleges table - for Directorate of Collegiate Education colleges
        print("Creating dce_colleges table...")
        cursor.execute('''
            CREATE TABLE dce_colleges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                s_no TEXT,
                name TEXT NOT NULL,
                district TEXT,
                region TEXT,
                college_type TEXT,
                category TEXT,
                contact TEXT,
                website TEXT,
                established TEXT,
                affiliation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, district)
            )
        ''')
        
        # Create indexes for better performance
        print("Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_colleges_member_code ON colleges(member_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nrlm_state_district ON nrlm_data(state_code, district_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bai_company_name ON bai_members(company_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dce_name_district ON dce_colleges(name, district)')
        
        # Commit all changes
        conn.commit()
        print("Database created successfully!")
        
        # Display table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nCreated tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def create_sample_data(db_name='users.db'):
    """
    Create sample data for testing
    """
    print("\nCreating sample data...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Create a sample user
        cursor.execute('''
            INSERT INTO users (username, password) 
            VALUES ('admin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
        ''')  # password: 'password'
        
        # Create sample college data
        cursor.execute('''
            INSERT INTO colleges (s_no, member_code, institution_name, year_established, contact_no)
            VALUES ('1', 'COL001', 'Sample College', '1990', '9876543210')
        ''')
        
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        conn.rollback()
        
    finally:
        conn.commit()
        conn.close()

def verify_database(db_name='users.db'):
    """
    Verify the database structure
    """
    print(f"\nVerifying database: {db_name}")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Tables found: {len(tables)}")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"  {table_name}: {len(columns)} columns")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
        
        # Get row counts
        print(f"\nRow counts:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} rows")
            
    except Exception as e:
        print(f"Error verifying database: {e}")
        
    finally:
        conn.close()

def main():
    """
    Main function to create the database
    """
    print("=" * 50)
    print("Database Creation Script")
    print("=" * 50)
    
    db_name = 'users.db'
    
    # Create database
    if create_database(db_name):
        # Create sample data
        create_sample_data(db_name)
        
        # Verify database
        verify_database(db_name)
        
        print(f"\n✅ Database '{db_name}' created successfully!")
        print("You can now run your Flask application.")
    else:
        print(f"\n❌ Failed to create database '{db_name}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
