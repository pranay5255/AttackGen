#!/usr/bin/env python3
"""
Quick usage examples for the audit processing pipeline.
"""

def show_examples():
    """Display usage examples for the audit processing pipeline."""
    
    examples = """
🚀 AUDIT PROCESSING PIPELINE - USAGE EXAMPLES
=============================================

1. FULL PIPELINE (Recommended):
   cd scripts
   python process_audit_pipeline.py
   
   Custom parameters:
   python process_audit_pipeline.py \\
     --audits-dir ../audits \\
     --embeddings-output my_embeddings.json \\
     --chunk-size 100 \\
     --device cuda

2. STEP-BY-STEP EXECUTION:

   Step 1 - Extract PDFs only:
   cd scripts
   python extract.py ../audits --recursive --device cuda
   
   Step 2 - Create embeddings only:
   python ../server/create_audit_embeddings.py \\
     --audits-dir ../audits \\
     --output embeddings.json

3. QUICK TEST (Small batch):
   # Process just one subdirectory
   python ../server/create_audit_embeddings.py \\
     --audits-dir ../audits/solo \\
     --output test_embeddings.json \\
     --chunk-size 50

4. WITH CUSTOM MODEL:
   python process_audit_pipeline.py \\
     --embedding-model openai/text-embedding-3-small

5. SKIP EXTRACTION (if MD files exist):
   python process_audit_pipeline.py --skip-extraction

6. FORCE RE-EXTRACTION:
   python process_audit_pipeline.py --force-extraction

📋 ENVIRONMENT SETUP:
=====================
Required environment variables:
export OPENROUTER_API_KEY="your_api_key_here"
# OR
export OPENAI_API_KEY="your_api_key_here"

Optional GPU selection:
export CUDA_VISIBLE_DEVICES=0

📊 EXPECTED OUTPUT:
===================
- Markdown files: audits/solo/md/*.md, audits/team/md/*.md
- Embeddings file: audit_embeddings.json (size depends on documents)
- Log file: pipeline_run_TIMESTAMP.log

🛠️ TROUBLESHOOTING:
===================
1. API Errors: Check OPENROUTER_API_KEY or OPENAI_API_KEY
2. CUDA Errors: Try --device cpu instead of --device cuda
3. Missing Modules: pip install markdown openai numpy

📚 DOCUMENTATION:
=================
See AUDIT_PIPELINE_DOCUMENTATION.md for detailed documentation
"""
    
    print(examples)

if __name__ == '__main__':
    show_examples()