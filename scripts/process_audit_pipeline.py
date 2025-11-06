#!/usr/bin/env python3
"""
Complete audit processing pipeline orchestration script.
Runs PDF extraction using DeepSeek-OCR followed by embedding creation.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json
import time
from datetime import datetime

def run_command(command, description, cwd=None):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ {description} completed successfully in {duration:.2f} seconds")
        if result.stdout:
            print("Output:")
            print(result.stdout)
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error code: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error during {description}: {e}")
        return False

def check_pdf_files(audits_dir):
    """Check for PDF files in the audits directory."""
    audits_path = Path(audits_dir)
    pdf_files = []
    
    for subdir in ['solo', 'team']:
        pdf_dir = audits_path / subdir / 'pdf'
        if pdf_dir.exists():
            pdfs = list(pdf_dir.glob('*.pdf'))
            pdf_files.extend(pdfs)
            print(f"Found {len(pdfs)} PDF files in {subdir}/pdf/")
    
    return pdf_files

def check_markdown_files(audits_dir):
    """Check for markdown files in the audits directory."""
    audits_path = Path(audits_dir)
    md_files = []
    
    for subdir in ['solo', 'team']:
        md_dir = audits_path / subdir / 'md'
        if md_dir.exists():
            mds = list(md_dir.glob('*.md'))
            md_files.extend(mds)
            print(f"Found {len(mds)} markdown files in {subdir}/md/")
    
    return md_files

def setup_directories(audits_dir):
    """Ensure necessary directories exist."""
    audits_path = Path(audits_dir)
    
    # Create md directories if they don't exist
    for subdir in ['solo', 'team']:
        md_dir = audits_path / subdir / 'md'
        md_dir.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {md_dir}")

def main():
    """Main orchestration function."""
    parser = argparse.ArgumentParser(
        description="Complete audit processing pipeline: OCR extraction + embeddings"
    )
    parser.add_argument(
        '--audits-dir',
        type=str,
        default='../audits',
        help='Path to audits directory (default: ../audits)'
    )
    parser.add_argument(
        '--embeddings-output',
        type=str,
        default='audit_embeddings.json',
        help='Output file for embeddings (default: audit_embeddings.json)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=100,
        help='Number of words per chunk for embeddings (default: 100)'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='mistralai/codestral-embed-2505',
        help='Embedding model to use (default: mistralai/codestral-embed-2505)'
    )
    parser.add_argument(
        '--force-extraction',
        action='store_true',
        help='Force re-extraction even if markdown files exist'
    )
    parser.add_argument(
        '--skip-extraction',
        action='store_true',
        help='Skip OCR extraction, only create embeddings'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='cuda',
        help='Device for DeepSeek-OCR (default: cuda)'
    )
    
    args = parser.parse_args()
    
    audits_dir = Path(args.audits_dir)
    if not audits_dir.exists():
        print(f"❌ Audits directory does not exist: {audits_dir}")
        return 1
    
    # Change to scripts directory for relative paths
    scripts_dir = Path(__file__).parent
    os.chdir(scripts_dir)
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"pipeline_run_{timestamp}.log"
    
    print(f"🚀 Starting audit processing pipeline")
    print(f"📁 Audits directory: {audits_dir}")
    print(f"📊 Output embeddings file: {args.embeddings_output}")
    print(f"📝 Log file: {log_file}")
    print("-" * 60)
    
    # Setup logging
    with open(log_file, 'w') as f:
        f.write(f"Audit Processing Pipeline Run - {timestamp}\n")
        f.write(f"Audits directory: {audits_dir}\n")
        f.write(f"Embeddings output: {args.embeddings_output}\n")
        f.write(f"Chunk size: {args.chunk_size}\n")
        f.write(f"Embedding model: {args.embedding_model}\n")
        f.write("-" * 60 + "\n\n")
    
    # Check current state
    pdf_files = check_pdf_files(audits_dir)
    existing_md_files = check_markdown_files(audits_dir)
    
    print(f"\n📋 Summary:")
    print(f"  - PDF files found: {len(pdf_files)}")
    print(f"  - Existing markdown files: {len(existing_md_files)}")
    
    # Ensure directories exist
    setup_directories(audits_dir)
    
    success = True
    
    # Step 1: PDF Extraction (if needed)
    if not args.skip_extraction:
        if args.force_extraction or len(existing_md_files) < len(pdf_files):
            print(f"\n🔍 Step 1: PDF Extraction with DeepSeek-OCR")
            
            # Run PDF extraction
            extract_cmd = f"""python3 extract.py "{audits_dir}" \\
                --recursive \\
                --device {args.device} \\
                --base-size 1024 \\
                --image-size 640"""
            
            if not run_command(extract_cmd, "PDF Extraction", cwd=scripts_dir):
                success = False
                print("❌ Pipeline failed at PDF extraction step")
        else:
            print(f"\n✅ Skipping PDF extraction - markdown files already exist")
    
    if not success:
        return 1
    
    # Step 2: Embedding Creation
    print(f"\n🧠 Step 2: Creating Embeddings")
    
    # Run embedding creation
    embed_cmd = f"""python3 ../server/create_audit_embeddings.py \\
        --audits-dir "{audits_dir}" \\
        --output "{args.embeddings_output}" \\
        --chunk-size {args.chunk_size} \\
        --model "{args.embedding_model}" """
    
    if not run_command(embed_cmd, "Embedding Creation", cwd=scripts_dir):
        print("❌ Pipeline failed at embedding creation step")
        success = False
    
    # Final summary
    final_md_files = check_markdown_files(audits_dir)
    embeddings_file = Path(args.embeddings_output)
    
    print(f"\n{'='*60}")
    print("🎯 PIPELINE SUMMARY")
    print('='*60)
    print(f"📁 Markdown files processed: {len(final_md_files)}")
    print(f"🧠 Embeddings file: {embeddings_file}")
    
    if embeddings_file.exists():
        file_size = embeddings_file.stat().st_size / (1024 * 1024)  # MB
        print(f"📊 Embeddings file size: {file_size:.2f} MB")
        
        # Try to load and count embeddings
        try:
            with open(embeddings_file, 'r') as f:
                embeddings_data = json.load(f)
            print(f"🔢 Total embeddings created: {len(embeddings_data)}")
        except:
            print("⚠️  Could not count embeddings in output file")
    
    if success:
        print("✅ Pipeline completed successfully!")
        print(f"📋 Check {log_file} for detailed logs")
        return 0
    else:
        print("❌ Pipeline completed with errors")
        print(f"📋 Check {log_file} for detailed logs")
        return 1

if __name__ == '__main__':
    exit(main())