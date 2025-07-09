#!/usr/bin/env python3
"""
Migration script to add competitive analysis columns to research_reports table.
This script can be run safely multiple times and will only add columns if they don't exist.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_database():
    """Add global_competitors and national_competitors columns to research_reports table"""
    
    # Get database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # For Railway deployment, the DATABASE_URL might need adjustment
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Starting database migration...")
        print(f"📊 Connecting to database...")
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful")
        
        # Check if table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'research_reports' not in tables:
            print("❌ research_reports table does not exist")
            return False
        
        print("✅ research_reports table found")
        
        # Check existing columns
        global_exists = check_column_exists(engine, 'research_reports', 'global_competitors')
        national_exists = check_column_exists(engine, 'research_reports', 'national_competitors')
        
        if global_exists and national_exists:
            print("✅ Both competitive analysis columns already exist, no migration needed")
            return True
        
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            
            try:
                # Add global_competitors column if it doesn't exist
                if not global_exists:
                    print("📝 Adding global_competitors column...")
                    connection.execute(text("""
                        ALTER TABLE research_reports 
                        ADD COLUMN global_competitors JSON
                    """))
                    print("✅ Added global_competitors column")
                else:
                    print("ℹ️ global_competitors column already exists")
                
                # Add national_competitors column if it doesn't exist
                if not national_exists:
                    print("📝 Adding national_competitors column...")
                    connection.execute(text("""
                        ALTER TABLE research_reports 
                        ADD COLUMN national_competitors JSON
                    """))
                    print("✅ Added national_competitors column")
                else:
                    print("ℹ️ national_competitors column already exists")
                
                # Commit the transaction
                trans.commit()
                print("🎉 Database migration completed successfully!")
                
                # Verify the columns were added
                global_exists_after = check_column_exists(engine, 'research_reports', 'global_competitors')
                national_exists_after = check_column_exists(engine, 'research_reports', 'national_competitors')
                
                if global_exists_after and national_exists_after:
                    print("✅ Migration verification successful - both columns exist")
                    return True
                else:
                    print("❌ Migration verification failed - columns may not have been added properly")
                    return False
                    
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed, rolling back: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def show_table_info():
    """Show current table structure for debugging"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        return
    
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        print("📊 Current research_reports table structure:")
        columns = inspector.get_columns('research_reports')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
            
    except Exception as e:
        print(f"❌ Error getting table info: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_table_info()
    else:
        success = migrate_database()
        sys.exit(0 if success else 1)