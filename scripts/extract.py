"""
PDF to Markdown extraction script using DeepSeek-OCR.
Processes PDF files and extracts text from each page, saving as markdown files.
TODOs:
1. integrate and run this script on the pdfs in the audits from pashov grp
2. create chunks embeddings for the markdown and extracted pdf files
3. save the embeddings to a db


"""

import os
import sys
from pathlib import Path
import tempfile

os.environ["CUDA_VISIBLE_DEVICES"] = '0'

try:
    from transformers import AutoModel, AutoTokenizer
    import torch
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install: pip install transformers torch pdf2image pillow")
    sys.exit(1)


def initialize_model(
    model_name: str = 'deepseek-ai/DeepSeek-OCR',
    device: str = 'cuda'
) -> tuple:
    """Initialize the DeepSeek-OCR model and tokenizer."""
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, 
        trust_remote_code=True
    )
    model = AutoModel.from_pretrained(
        model_name,
        _attn_implementation='flash_attention_2',
        trust_remote_code=True,
        use_safetensors=True
    )
    model = model.eval().to(device).to(torch.bfloat16)
    print("Model loaded successfully")
    return model, tokenizer


def pdf_to_images(pdf_path: Path, dpi: int = 200) -> list[Image.Image]:
    """Convert PDF pages to PIL Images."""
    try:
        images = convert_from_path(str(pdf_path), dpi=dpi)
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []


def extract_text_from_image(
    model,
    tokenizer,
    image: Image.Image,
    prompt: str = "<image>\n<|grounding|>Convert the document to markdown. ",
    base_size: int = 1024,
    image_size: int = 640,
    crop_mode: bool = True
) -> str:
    """Extract text from a single image using DeepSeek-OCR."""
    try:
        # Save image temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            image.save(tmp_path, 'JPEG', quality=95)
        
        try:
            res = model.infer(
                tokenizer,
                prompt=prompt,
                image_file=tmp_path,
                output_path='',
                base_size=base_size,
                image_size=image_size,
                crop_mode=crop_mode,
                save_results=False,
                test_compress=True
            )
            return res if isinstance(res, str) else str(res)
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def process_pdf(
    pdf_path: Path,
    output_dir: Path,
    model,
    tokenizer,
    prompt: str = "<image>\n<|grounding|>Convert the document to markdown. ",
    base_size: int = 1024,
    image_size: int = 640,
    crop_mode: bool = True
) -> bool:
    """Process a single PDF file and extract text to markdown."""
    print(f"\nProcessing: {pdf_path.name}")
    
    # Convert PDF to images
    images = pdf_to_images(pdf_path)
    if not images:
        print(f"Failed to convert PDF: {pdf_path}")
        return False
    
    print(f"Found {len(images)} pages")
    
    # Extract text from each page
    extracted_texts = []
    for i, image in enumerate(images, 1):
        print(f"  Processing page {i}/{len(images)}...", end=' ', flush=True)
        text = extract_text_from_image(
            model, tokenizer, image, prompt, base_size, image_size, crop_mode
        )
        if text:
            extracted_texts.append(f"## Page {i}\n\n{text}\n")
            print("✓")
        else:
            print("✗")
    
    if not extracted_texts:
        print(f"No text extracted from {pdf_path}")
        return False
    
    # Combine all pages
    combined_text = "\n\n".join(extracted_texts)
    
    # Generate output filename
    output_filename = pdf_path.stem + '.md'
    output_path = output_dir / output_filename
    
    # Save markdown file
    output_path.write_text(combined_text, encoding='utf-8')
    print(f"Saved: {output_path}")
    return True


def process_directory(
    input_dir: Path,
    output_dir: Path,
    model,
    tokenizer,
    recursive: bool = False,
    pattern: str = "*.pdf"
) -> None:
    """Process all PDF files in a directory."""
    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    if recursive:
        pdf_files = list(input_dir.rglob(pattern))
    else:
        pdf_files = list(input_dir.glob(pattern))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s)")
    
    # Process each PDF
    successful = 0
    failed = 0
    
    for pdf_path in pdf_files:
        try:
            if process_pdf(pdf_path, output_dir, model, tokenizer):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Processing complete: {successful} successful, {failed} failed")
    print(f"{'='*50}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files using DeepSeek-OCR"
    )
    parser.add_argument(
        'input',
        type=str,
        help='Input PDF file or directory containing PDF files'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory for markdown files (default: same as input or input_dir/md)'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process PDFs recursively in subdirectories'
    )
    parser.add_argument(
        '--base-size',
        type=int,
        default=1024,
        help='Base size for OCR processing (default: 1024)'
    )
    parser.add_argument(
        '--image-size',
        type=int,
        default=640,
        help='Image size for OCR processing (default: 640)'
    )
    parser.add_argument(
        '--no-crop',
        action='store_true',
        help='Disable crop mode'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='deepseek-ai/DeepSeek-OCR',
        help='Model name or path (default: deepseek-ai/DeepSeek-OCR)'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='cuda',
        help='Device to use (default: cuda)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
    elif input_path.is_file():
        # If input is a file, use same directory
        output_dir = input_path.parent / 'md'
    else:
        # If input is a directory, create md subdirectory
        output_dir = input_path / 'md'
    
    # Initialize model
    print("Initializing DeepSeek-OCR model...")
    try:
        model, tokenizer = initialize_model(args.model, args.device)
    except Exception as e:
        print(f"Failed to initialize model: {e}")
        sys.exit(1)
    
    # Process input
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # Single file
        process_pdf(
            input_path,
            output_dir,
            model,
            tokenizer,
            base_size=args.base_size,
            image_size=args.image_size,
            crop_mode=not args.no_crop
        )
    elif input_path.is_dir():
        # Directory
        process_directory(
            input_path,
            output_dir,
            model,
            tokenizer,
            recursive=args.recursive,
            pattern="*.pdf"
        )
    else:
        print(f"Invalid input: {input_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()

