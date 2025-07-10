#!/usr/bin/env python3
"""
Migration script to add is_admin field to existing users table
and set admin status for the configured admin email.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.whitelist_service import whitelist_service

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

def migrate_admin_field():
    """Add is_admin field to users table and set admin status"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if is_admin column already exists
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_admin'
        """))
        
        if result.fetchone():
            print("is_admin column already exists")
        else:
            # Add is_admin column
            print("Adding is_admin column to users table...")
            connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            connection.commit()
            print("is_admin column added successfully")
        
        # Get admin email from whitelist service
        admin_email = whitelist_service.get_admin_email()
        print(f"Setting admin status for email: {admin_email}")
        
        # Update admin user
        result = connection.execute(text("""
            UPDATE users 
            SET is_admin = TRUE 
            WHERE LOWER(email) = LOWER(:admin_email)
        """), {"admin_email": admin_email})
        
        connection.commit()
        
        if result.rowcount > 0:
            print(f"Successfully set admin status for {admin_email}")
        else:
            print(f"No user found with email {admin_email}")
            print("Admin status will be set when the admin user registers")

if __name__ == "__main__":
    try:
        migrate_admin_field()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)