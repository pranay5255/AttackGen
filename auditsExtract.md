# Audit Extraction Workflow

## Overview

This document describes the workflow for extracting security findings from audit PDFs and processing them into a structured format suitable for embedding and database storage.

## Extraction Process

### Step 1: PDF to Markdown Extraction

Use the `scripts/extract.py` script to convert PDF audit reports to markdown format using DeepSeek-OCR.

**Install Dependencies:**
```bash
pip install transformers torch pdf2image pillow
```

**Extract from PDFs:**
```bash
# Extract from solo audits
python scripts/extract.py audits/solo/pdf/ -o audits/solo/md/

# Extract from team audits  
python scripts/extract.py audits/team/pdf/ -o audits/team/md/

# Extract recursively from all audits
python scripts/extract.py audits/ -r -o audits/md/
```

### Step 2: Chunk Creation and Embedding

After extraction, the markdown files need to be:
1. Chunked into smaller, semantically meaningful pieces
2. Converted to embeddings using the embedding model
3. Stored in the database for retrieval

**TODO:**
- Integrate chunking service (using `server/chunkIndex.py` or `server/embedCreate.py`)
- Generate embeddings for all extracted markdown files
- Store embeddings in database with proper metadata

### Step 3: Finding Structure

Extracted findings should follow this JSON structure:

```json
{
  "id": "protocol-finding-code-sequential-id",
  "source": {
    "report": "Protocol-security-review.pdf",
    "protocol": "ProtocolName",
    "auditor": "AuditorName",
    "date": "YYYY-MM-DD"
  },
  "tags": {
    "severity": "High|Medium|Low|Informational",
    "finding_code": "H-01|M-01|L-01|N-01"
  },
  "title": "Brief descriptive title of the finding",
  "category": "math|access-control|reentrancy|logic-error|etc",
  "text": {
    "description": "Detailed description of the vulnerability"
  },
  "code": "```solidity\ncode snippet here\n```",
  "fix": {
    "recommendation": "Recommended fix or mitigation",
    "affected_contracts": ["ContractName1", "ContractName2"],
    "affected_functions": ["function1", "function2"]
  }
}
```

## Example Finding

```json
{
  "id": "sofamon-H01-0001",
  "source": {
    "report": "Sofamon-security-review.pdf",
    "protocol": "Sofamon",
    "auditor": null,
    "date": null
  },
  "tags": {
    "severity": "High",
    "finding_code": "H-01"
  },
  "title": "Rounding issue in price formula",
  "category": "math",
  "text": {
    "description": "The price computation divides before scaling, zeroing terms and enabling underpricing under certain supply values."
  },
  "code": "```solidity\nreturn ((totalSupply * curveFactor) / (totalSupply - x) - ...);\n```",
  "fix": {
    "recommendation": "Reorder operations; scale numerators before division.",
    "affected_contracts": ["SofamonMarket"],
    "affected_functions": ["priceFor"]
  }
}
```

## Next Steps (TODOs)

1. **Run extraction on all audit PDFs:**
   - Process `audits/solo/pdf/` directory
   - Process `audits/team/pdf/` directory
   - Verify markdown output quality

2. **Create chunk embeddings:**
   - Use chunking model from `download_model.py` and `chunking.py`
   - Create embeddings using `code_inspector_service.py`
   - Integrate with `FactsAndMemoriesService` if applicable

3. **Save embeddings to database:**
   - Use `server/chunkIndex.py` or `server/embedCreate.py`
   - Store with metadata linking back to source PDF and finding
   - Ensure proper indexing for retrieval

## Integration Points

- **Extraction**: `scripts/extract.py` - PDF to markdown conversion
- **Chunking**: `server/chunkIndex.py` - Text chunking logic
- **Embeddings**: `server/embedCreate.py` - Embedding generation
- **Database**: `server/loadEmbeddings.py` - Embedding storage and retrieval
