# Database Setup Guide

This directory contains scripts to create and set up the database for the Data Application.

## Files Created

1. **`create_database.py`** - Python script for database creation
2. **`create_database.sql`** - SQL script for database creation
3. **`setup_database.sh`** - Shell script that automatically chooses the best method
4. **`DATABASE_SETUP.md`** - This documentation file

## Database Schema

The application uses a SQLite database with the following tables:

### 1. `users` - User Authentication
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE NOT NULL)
- `password` (TEXT NOT NULL) - SHA256 hashed
- `created_at` (TIMESTAMP)

### 2. `colleges` - Educational Institutions
- `id` (INTEGER PRIMARY KEY)
- `s_no` (TEXT)
- `member_code` (TEXT UNIQUE)
- `institution_name` (TEXT NOT NULL)
- `year_established` (TEXT)
- `contact_no` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### 3. `nrlm_data` - National Rural Livelihoods Mission Data
- `id` (INTEGER PRIMARY KEY)
- `state_code`, `state_name` (TEXT)
- `district_code`, `district_name` (TEXT)
- `block_code`, `block_name` (TEXT)
- `grampanchayat_code`, `grampanchayat_name` (TEXT)
- `village_code`, `village_name` (TEXT)
- `shg_name` (TEXT)
- `member_name`, `member_code` (TEXT)
- `created_at`, `updated_at` (TIMESTAMP)

### 4. `bai_members` - Builders Association of India Members
- `id` (INTEGER PRIMARY KEY)
- `company_name` (TEXT NOT NULL)
- `contact_person` (TEXT)
- `address` (TEXT)
- `phone` (TEXT)
- `email` (TEXT)
- `source_url` (TEXT)
- `scraped_at` (TIMESTAMP)
- `created_at`, `updated_at` (TIMESTAMP)

### 5. `dce_colleges` - Directorate of Collegiate Education Colleges
- `id` (INTEGER PRIMARY KEY)
- `s_no` (TEXT)
- `name` (TEXT NOT NULL)
- `district`, `region` (TEXT)
- `college_type`, `category` (TEXT)
- `contact`, `website` (TEXT)
- `established`, `affiliation` (TEXT)
- `created_at`, `updated_at` (TIMESTAMP)
- UNIQUE constraint on (name, district)

## How to Create the Database

### Method 1: Using the Shell Script (Recommended)
```bash
./setup_database.sh
```

### Method 2: Using Python Script
```bash
python3 create_database.py
```

### Method 3: Using SQL Script Directly
```bash
sqlite3 users.db < create_database.sql
```

## Sample Data

The scripts create sample data including:
- A default admin user (username: `admin`, password: `password`)
- A sample college record

## Indexes

The following indexes are created for better performance:
- `idx_users_username` on `users(username)`
- `idx_colleges_member_code` on `colleges(member_code)`
- `idx_nrlm_state_district` on `nrlm_data(state_code, district_code)`
- `idx_bai_company_name` on `bai_members(company_name)`
- `idx_dce_name_district` on `dce_colleges(name, district)`

## Verification

After running any of the creation scripts, you can verify the database structure by running:
```bash
sqlite3 users.db ".schema"
sqlite3 users.db ".tables"
```

## Notes

- The scripts will remove any existing `users.db` file before creating a new one
- All timestamps use SQLite's `CURRENT_TIMESTAMP` function
- The password for the default admin user is SHA256 hashed
- The database file will be created in the current directory

## Troubleshooting

If you encounter any issues:
1. Make sure you have Python 3 or SQLite3 installed
2. Check file permissions (the shell script should be executable)
3. Ensure you have write permissions in the current directory
4. Verify that no other process is using the database file
