#!/usr/bin/env python3
"""
Startup migration script that runs automatically when the backend starts.
This ensures the database schema is up to date.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_and_migrate():
    """Check if migration is needed and apply it if necessary"""
    
    # Get database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("⚠️ DATABASE_URL environment variable not set, skipping migration")
        return True  # Don't fail startup if no database configured
    
    # For Railway deployment, the DATABASE_URL might need adjustment
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Check if table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'research_reports' not in tables:
            print("ℹ️ research_reports table does not exist yet, skipping competitive analysis migration")
            return True
        
        # Check if competitive analysis columns exist
        columns = [col['name'] for col in inspector.get_columns('research_reports')]
        global_exists = 'global_competitors' in columns
        national_exists = 'national_competitors' in columns
        
        if global_exists and national_exists:
            print("✅ Competitive analysis columns already exist")
            return True
        
        print("🔄 Applying competitive analysis migration...")
        
        with engine.connect() as connection:
            trans = connection.begin()
            
            try:
                # Add global_competitors column if it doesn't exist
                if not global_exists:
                    print("📝 Adding global_competitors column...")
                    connection.execute(text("""
                        ALTER TABLE research_reports 
                        ADD COLUMN global_competitors JSON
                    """))
                
                # Add national_competitors column if it doesn't exist
                if not national_exists:
                    print("📝 Adding national_competitors column...")
                    connection.execute(text("""
                        ALTER TABLE research_reports 
                        ADD COLUMN national_competitors JSON
                    """))
                
                trans.commit()
                print("✅ Competitive analysis migration completed successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
            
    except Exception as e:
        print(f"⚠️ Could not connect to database for migration: {e}")
        # Don't fail startup if database is not available
        return True

if __name__ == "__main__":
    success = check_and_migrate()
    sys.exit(0 if success else 1)