-- Database Creation Script for the Data Application
-- This SQL script creates all necessary tables for the application.

-- Users table - for authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Colleges table - for educational institutions data
CREATE TABLE IF NOT EXISTS colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    s_no TEXT,
    member_code TEXT UNIQUE,
    institution_name TEXT NOT NULL,
    year_established TEXT,
    contact_no TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NRLM Data table - for National Rural Livelihoods Mission data
CREATE TABLE IF NOT EXISTS nrlm_data (
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
);

-- BAI Members table - for Builders Association of India members
CREATE TABLE IF NOT EXISTS bai_members (
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
);

-- DCE Colleges table - for Directorate of Collegiate Education colleges
CREATE TABLE IF NOT EXISTS dce_colleges (
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
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_colleges_member_code ON colleges(member_code);
CREATE INDEX IF NOT EXISTS idx_nrlm_state_district ON nrlm_data(state_code, district_code);
CREATE INDEX IF NOT EXISTS idx_bai_company_name ON bai_members(company_name);
CREATE INDEX IF NOT EXISTS idx_dce_name_district ON dce_colleges(name, district);

-- Insert sample data
INSERT OR IGNORE INTO users (username, password) 
VALUES ('admin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8');

INSERT OR IGNORE INTO colleges (s_no, member_code, institution_name, year_established, contact_no)
VALUES ('1', 'COL001', 'Sample College', '1990', '9876543210');
