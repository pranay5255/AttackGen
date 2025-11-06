#!/usr/bin/env python3
"""
Comprehensive embedding creation script for audit documents.
Processes all markdown files in the audits directory and creates embeddings.
"""

import os
import json
import markdown
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Any
import argparse

# Load environment variables from .env file
load_dotenv()

# Initialize OpenRouter client for embeddings
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY'),
)

def parse_markdown_files(folder_path: str, chunk_size: int = 100) -> List[Dict[str, Any]]:
    """
    Parse all markdown files in a folder and return their content as chunks.
    
    Parameters:
    - folder_path: Path to the folder containing markdown files.
    - chunk_size: Number of words per chunk for splitting large documents.

    Returns:
    - List of document chunks with metadata.
    """
    chunks = []
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"Warning: Folder {folder_path} does not exist")
        return chunks
        
    print(f"Processing markdown files in: {folder_path}")
    
    for file_path in folder_path.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                # Convert markdown to plain text
                plain_text = markdown.markdown(content)
                words = plain_text.split()
                
                print(f"  Processing {file_path.name} ({len(words)} words)")
                
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i + chunk_size])
                    if chunk.strip():  # Only add non-empty chunks
                        chunks.append({
                            "file": str(file_path.relative_to(folder_path.parent)),  # Relative path from audits/
                            "chunk_index": i // chunk_size,
                            "text": chunk,
                            "full_file_path": str(file_path)
                        })
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    return chunks

def create_embeddings(text: str, model: str = 'mistralai/codestral-embed-2505') -> List[float]:
    """Create embeddings using OpenRouter's API."""
    try:
        embedding = openrouter_client.embeddings.create(
            model=model,
            input=text,
            encoding_format="float"
        )
        return embedding.data[0].embedding
    except Exception as e:
        print(f"Error creating embedding: {e}")
        raise

def create_embeddings_for_chunks(chunks: List[Dict[str, Any]], model: str = 'mistralai/codestral-embed-2505') -> List[Dict[str, Any]]:
    """
    Create embeddings for each chunk of markdown content using OpenRouter embeddings API.
    
    Parameters:
    - chunks: List of dictionaries with chunked text data.
    - model: Embedding model to use.

    Returns:
    - List of embeddings and corresponding chunk metadata.
    """
    embeddings = []
    total_chunks = len(chunks)
    
    print(f"Creating embeddings for {total_chunks} chunks using model: {model}")
    
    for i, chunk in enumerate(chunks):
        try:
            if (i + 1) % 10 == 0:  # Progress update every 10 chunks
                print(f"  Progress: {i + 1}/{total_chunks} chunks processed")
            
            embedding = create_embeddings(chunk['text'], model)
            embeddings.append({
                "file": chunk['file'],
                "chunk_index": chunk['chunk_index'],
                "embedding": embedding,
                "text": chunk['text'][:500] + "..." if len(chunk['text']) > 500 else chunk['text'],  # Truncate for storage
                "full_file_path": chunk['full_file_path']
            })
        except Exception as e:
            print(f"Error creating embedding for chunk {i + 1}: {e}")
            continue
            
    return embeddings

def save_embeddings_to_file(embeddings: List[Dict[str, Any]], output_file: str) -> None:
    """Save the embeddings to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(embeddings, f, ensure_ascii=False, indent=2)
        print(f"Embeddings saved to {output_file}")
        print(f"Total embeddings saved: {len(embeddings)}")
    except Exception as e:
        print(f"Error saving embeddings: {e}")
        raise

def process_audits_directory(audits_dir: str, output_file: str, chunk_size: int = 100, model: str = 'mistralai/codestral-embed-2505') -> None:
    """
    Process all markdown files in the audits directory and create embeddings.
    
    Parameters:
    - audits_dir: Path to the audits directory
    - output_file: Output file path for embeddings
    - chunk_size: Number of words per chunk
    - model: Embedding model to use
    """
    audits_path = Path(audits_dir)
    
    if not audits_path.exists():
        raise ValueError(f"Audits directory does not exist: {audits_dir}")
    
    all_chunks = []
    
    # Process solo and team directories
    for subdir in ['solo', 'team']:
        md_dir = audits_path / subdir / 'md'
        if md_dir.exists():
            print(f"\nProcessing {subdir} directory...")
            chunks = parse_markdown_files(md_dir, chunk_size)
            all_chunks.extend(chunks)
        else:
            print(f"Warning: {subdir}/md directory not found")
    
    if not all_chunks:
        print("No markdown files found to process")
        return
    
    print(f"\nTotal chunks to process: {len(all_chunks)}")
    
    # Create embeddings
    embeddings = create_embeddings_for_chunks(all_chunks, model)
    
    if embeddings:
        save_embeddings_to_file(embeddings, output_file)
    else:
        print("No embeddings created")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create embeddings for all audit markdown files"
    )
    parser.add_argument(
        '--audits-dir',
        type=str,
        default='../audits',
        help='Path to audits directory (default: ../audits)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='audit_embeddings.json',
        help='Output file for embeddings (default: audit_embeddings.json)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=100,
        help='Number of words per chunk (default: 100)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='mistralai/codestral-embed-2505',
        help='Embedding model to use (default: mistralai/codestral-embed-2505)'
    )
    
    args = parser.parse_args()
    
    # Validate API key
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENROUTER_API_KEY or OPENAI_API_KEY environment variable not set")
        return 1
    
    try:
        print("Starting audit embeddings creation...")
        print(f"Audits directory: {args.audits_dir}")
        print(f"Output file: {args.output}")
        print(f"Chunk size: {args.chunk_size} words")
        print(f"Model: {args.model}")
        print("-" * 60)
        
        process_audits_directory(args.audits_dir, args.output, args.chunk_size, args.model)
        
        print("\nEmbedding creation completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())