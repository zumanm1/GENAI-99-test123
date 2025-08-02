#!/usr/bin/env python3
"""
Verify that SQLite database and ChromaDB collections exist and are populated.
"""

import os
import sqlite3
import chromadb
from pathlib import Path

def verify_sqlite():
    """Verify SQLite database exists and has tables."""
    db_path = "data/app.db"
    
    if not os.path.exists(db_path):
        print("❌ SQLite database does not exist at data/app.db")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ SQLite database exists at {db_path}")
        print(f"   Tables found: {len(tables)}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error accessing SQLite database: {e}")
        return False

def verify_chromadb():
    """Verify ChromaDB collections exist and are populated."""
    chroma_path = "./chroma_data"
    
    if not os.path.exists(chroma_path):
        print("❌ ChromaDB data directory does not exist at ./chroma_data")
        return False
    
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        collections = client.list_collections()
        
        print(f"✅ ChromaDB exists at {chroma_path}")
        print(f"   Collections found: {len(collections)}")
        
        for collection in collections:
            count = collection.count()
            print(f"   - {collection.name}: {count} documents")
            
            # Sample a few documents to verify content
            if count > 0:
                sample = collection.peek(limit=3)
                print(f"     Sample document IDs: {sample['ids'][:3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing ChromaDB: {e}")
        return False

def main():
    print("🔍 Verifying Database Setup...")
    print("=" * 50)
    
    sqlite_ok = verify_sqlite()
    print()
    chromadb_ok = verify_chromadb()
    
    print()
    print("=" * 50)
    if sqlite_ok and chromadb_ok:
        print("✅ All databases are properly initialized!")
        return True
    else:
        print("❌ Some databases have issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
