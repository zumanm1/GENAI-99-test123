#!/usr/bin/env python3
"""
Seed ChromaDB with document embeddings from the docs directory.
Usage: python scripts/seed_embeddings.py --source docs/
"""

import os
import sys
import argparse
import chromadb
from chromadb.config import Settings
from pathlib import Path


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def seed_embeddings(source: str):
    """Seed ChromaDB with embeddings from document files."""
    print(f"Seeding embeddings from {source}")
    
    # Check if source directory exists
    if not os.path.exists(source):
        print(f"Error: Source directory '{source}' does not exist.")
        return False
    
    try:
        # Initialize ChromaDB client
        # Using persistent client for local development
        client = chromadb.PersistentClient(path="./chroma_data")
        
        # Create or get collection
        collection_name = "network_docs"
        try:
            collection = client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
        except:
            collection = client.create_collection(
                name=collection_name,
                metadata={"description": "Network automation documentation"}
            )
            print(f"Created new collection: {collection_name}")
        
        documents = []
        metadatas = []
        ids = []
        
        # Process all markdown and text files
        source_path = Path(source)
        file_count = 0
        
        for file_path in source_path.glob("**/*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                # Split content into chunks for better retrieval
                chunks = chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{file_path.stem}_chunk_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "chunk_index": i,
                        "file_type": "markdown"
                    })
                    ids.append(doc_id)
                
                file_count += 1
                print(f"Processed: {file_path.name} ({len(chunks)} chunks)")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        # Process text files
        for file_path in source_path.glob("**/*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                # Split content into chunks
                chunks = chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{file_path.stem}_chunk_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "chunk_index": i,
                        "file_type": "text"
                    })
                    ids.append(doc_id)
                
                file_count += 1
                print(f"Processed: {file_path.name} ({len(chunks)} chunks)")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        if documents:
            # Add documents to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"\nSuccessfully seeded {len(documents)} document chunks from {file_count} files to ChromaDB!")
            print(f"Collection '{collection_name}' now contains {collection.count()} total documents.")
        else:
            print("No documents found to seed.")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print("Make sure ChromaDB is running locally or install it with: pip install chromadb")
        return False


def main():
    parser = argparse.ArgumentParser(description="Seed ChromaDB with document embeddings")
    parser.add_argument("--source", default="docs/", help="Source directory containing documents")
    
    args = parser.parse_args()
    
    success = seed_embeddings(args.source)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
