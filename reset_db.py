#!/usr/bin/env python3
"""
Database reset script for Event AI Generator
Run this if you're having database issues
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import Base, engine

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    print("🔄 Resetting database...")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped successfully")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        print("🎉 Database reset complete!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()