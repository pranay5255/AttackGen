# Audit Processing Pipeline Documentation

This documentation describes the complete pipeline for extracting text from PDF audit reports using DeepSeek-OCR and creating embeddings for vector similarity search.

## Overview

The pipeline consists of three main components:

1. **PDF Extraction** (`scripts/extract.py`) - Uses DeepSeek-OCR to extract text from PDF files
2. **Embedding Creation** (`server/create_audit_embeddings.py`) - Creates vector embeddings from markdown files
3. **Pipeline Orchestration** (`scripts/process_audit_pipeline.py`) - Coordinates the entire process

## Architecture

```
audits/
├── solo/
│   ├── pdf/          # Original PDF files
│   └── md/           # Extracted markdown files
└── team/
    ├── pdf/          # Original PDF files
    └── md/           # Extracted markdown files
```

## Components

### 1. PDF Extraction (`scripts/extract.py`)

**Purpose**: Converts PDF files to markdown text using DeepSeek-OCR

**Key Features**:
- DeepSeek-OCR model integration
- PDF to image conversion (200 DPI)
- Page-by-page text extraction
- Automatic markdown formatting
- Progress tracking

**Usage**:
```bash
python scripts/extract.py ../audits --recursive --device cuda
```

**Parameters**:
- `--device`: CUDA device for GPU acceleration
- `--base-size`: Base size for OCR processing (default: 1024)
- `--image-size`: Image size for OCR processing (default: 640)
- `--no-crop`: Disable crop mode

### 2. Embedding Creation (`server/create_audit_embeddings.py`)

**Purpose**: Creates vector embeddings from markdown files for similarity search

**Key Features**:
- 100-word chunking strategy
- OpenRouter API integration
- JSON output format
- Progress tracking and error handling

**Usage**:
```bash
python server/create_audit_embeddings.py \
  --audits-dir ../audits \
  --output audit_embeddings.json \
  --chunk-size 100 \
  --model mistralai/codestral-embed-2505
```

**Parameters**:
- `--audits-dir`: Path to audits directory
- `--output`: Output JSON file for embeddings
- `--chunk-size`: Words per chunk (default: 100)
- `--model`: Embedding model (default: mistralai/codestral-embed-2505)

### 3. Pipeline Orchestration (`scripts/process_audit_pipeline.py`)

**Purpose**: Coordinates the complete pipeline execution

**Key Features**:
- Automatic PDF extraction detection
- Smart re-processing (only new files)
- Comprehensive logging
- Error handling and recovery
- Progress reporting

**Usage**:
```bash
python scripts/process_audit_pipeline.py \
  --audits-dir ../audits \
  --embeddings-output audit_embeddings.json \
  --chunk-size 100
```

**Parameters**:
- `--audits-dir`: Path to audits directory
- `--embeddings-output`: Output file for embeddings
- `--chunk-size`: Words per chunk
- `--embedding-model`: Model for embeddings
- `--force-extraction`: Force re-extraction
- `--skip-extraction`: Skip OCR, only create embeddings
- `--device`: CUDA device for OCR

## Environment Setup

### Required Environment Variables

```bash
# OpenRouter API for embeddings
OPENROUTER_API_KEY=your_openrouter_api_key

# Alternative: OpenAI API
OPENAI_API_KEY=your_openai_api_key

# CUDA_VISIBLE_DEVICES (optional, for GPU selection)
CUDA_VISIBLE_DEVICES=0
```

### Python Dependencies

```bash
# Core dependencies
pip install transformers torch pdf2image pillow
pip install markdown openai numpy scikit-learn
pip install tiktoken python-dotenv
```

### GPU Requirements

For optimal performance:
- NVIDIA GPU with CUDA support
- At least 8GB VRAM
- CUDA drivers installed

## Workflow

### 1. Initial Setup

```bash
# Set environment variables
export OPENROUTER_API_KEY="your_key_here"

# Ensure directories exist
mkdir -p audits/solo/md audits/team/md
```

### 2. Full Pipeline Execution

```bash
# Run complete pipeline
cd scripts
python process_audit_pipeline.py

# Or with custom parameters
python process_audit_pipeline.py \
  --audits-dir ../audits \
  --embeddings-output my_embeddings.json \
  --chunk-size 150 \
  --device cuda
```

### 3. Step-by-Step Execution

```bash
# Step 1: Extract PDFs only
python extract.py ../audits --recursive --device cuda

# Step 2: Create embeddings only
python ../server/create_audit_embeddings.py \
  --audits-dir ../audits \
  --output embeddings.json
```

## Output Format

### Embeddings JSON Structure

```json
[
  {
    "file": "solo/md/Azuro-security-review.md",
    "chunk_index": 0,
    "embedding": [0.1, 0.2, ...],
    "text": "First 100 words of the document...",
    "full_file_path": "/path/to/file.md"
  },
  ...
]
```

### Markdown File Structure

```markdown
## Page 1

Extracted text from page 1...

## Page 2

Extracted text from page 2...
```

## Error Handling

### Common Issues

1. **API Authentication Errors**
   ```
   Error code: 401 - No cookie auth credentials found
   ```
   **Solution**: Ensure `OPENROUTER_API_KEY` or `OPENAI_API_KEY` is set

2. **CUDA Out of Memory**
   ```
   CUDA out of memory
   ```
   **Solution**: Reduce batch size or use CPU processing with `--device cpu`

3. **Missing Dependencies**
   ```
   ModuleNotFoundError: No module named 'markdown'
   ```
   **Solution**: Install missing packages with `pip install package_name`

### Recovery Strategies

- **Partial Processing**: The pipeline saves progress after each file
- **Incremental Updates**: Only processes new/changed files
- **Resume Capability**: Can restart from interruption point

## Performance Optimization

### GPU Optimization
- Use `--device cuda` for GPU acceleration
- Adjust `--image-size` parameter (640-1024 range)
- Monitor GPU memory usage

### Processing Speed
- Batch processing for multiple files
- Progress tracking for long operations
- Parallel API calls where possible

### Storage Management
- JSON files can be large (hundreds of MB)
- Consider compression for long-term storage
- Archive old embedding files

## Integration with Existing Code

### Using with Server Components

The embeddings can be used with existing server utilities:

```python
# Load embeddings
from server.loadEmbeddings import load_embeddings_from_file
embeddings = load_embeddings_from_file('audit_embeddings.json')

# Search similar content
from server.localAttack import get_relevant_chunks
chunks = get_relevant_chunks(contract_code, contract_abi)
```

### API Integration

The embeddings integrate with the FastAPI server in `server/main.py`:

```python
# Use embeddings for contract analysis
@app.post("/analyze-contract")
def analyze_contract(req: ContractAnalysisRequest):
    # Load embeddings and perform similarity search
    # Returns top similar chunks
```

## Monitoring and Logging

### Log Files

Pipeline execution creates timestamped log files:
```
pipeline_run_20241106_123456.log
```

### Progress Tracking

- Real-time progress updates during execution
- Summary statistics at completion
- Error reporting with detailed messages

### Performance Metrics

- Processing time per file
- Total chunks processed
- API call success rates
- Memory usage monitoring

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip install --upgrade transformers torch
   ```

2. **Clean Temporary Files**
   ```bash
   find . -name "*.tmp" -delete
   ```

3. **Archive Old Embeddings**
   ```bash
   mv audit_embeddings.json audit_embeddings_$(date +%Y%m%d).json
   ```

### Backup Strategy

- Backup original PDF files
- Archive previous embedding files
- Keep processing logs for debugging

## Troubleshooting Guide

### Step-by-Step Debugging

1. **Check Environment**
   ```bash
   echo $OPENROUTER_API_KEY
   nvidia-smi  # Check GPU availability
   ```

2. **Test Individual Components**
   ```bash
   # Test OCR
   python extract.py test.pdf --device cpu
   
   # Test embeddings
   python ../server/create_audit_embeddings.py --output test.json
   ```

3. **Verify File Structure**
   ```bash
   ls -la audits/solo/pdf/
   ls -la audits/team/pdf/
   ```

### Support Information

When reporting issues, include:
- Error messages and stack traces
- Environment details (GPU, Python version)
- File structure information
- Processing logs

## Future Enhancements

### Planned Features

1. **Database Storage**: PostgreSQL with pgvector
2. **Incremental Updates**: Only process new files
3. **Multi-language Support**: OCR for non-English documents
4. **Advanced Chunking**: Semantic rather than fixed-size chunks
5. **Real-time Updates**: Webhook-based processing

### Extensibility

The pipeline is designed for easy extension:
- Custom OCR models
- Alternative embedding providers
- Different output formats
- Additional processing steps