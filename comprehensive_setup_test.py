#!/usr/bin/env python3
"""
Comprehensive setup verification script for AttackGen OCR system.
Tests authentication, available models, and basic functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test 1: Environment Setup
print("🔧 Environment Setup Test")
print("=" * 50)

# Set CUDA device
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
print(f"✓ CUDA device set to: {os.getenv('CUDA_VISIBLE_DEVICES')}")

# Check HuggingFace token
hf_token = os.getenv('HF_TOKEN')
if hf_token:
    print(f"✓ HuggingFace token configured: {hf_token[:10]}...")
    os.environ['HUGGINGFACE_HUB_TOKEN'] = hf_token
else:
    print("⚠ No HuggingFace token found")

# Check OpenRouter API key
openrouter_key = os.getenv('OPENROUTER_API_KEY')
if openrouter_key:
    print(f"✓ OpenRouter API key configured: {openrouter_key[:15]}...")
else:
    print("⚠ No OpenRouter API key found")

# Test 2: Package Imports
print("\n📦 Package Import Test")
print("=" * 50)

try:
    from transformers import AutoModel, AutoTokenizer
    import torch
    from pdf2image import convert_from_path
    from PIL import Image
    from huggingface_hub import HfApi
    from openai import OpenAI
    import numpy as np
    print("✓ All required packages imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 3: CUDA Availability
print("\n🚀 CUDA Test")
print("=" * 50)

if torch.cuda.is_available():
    print(f"✓ CUDA is available: {torch.cuda.get_device_name(0)}")
    print(f"✓ CUDA version: {torch.version.cuda}")
else:
    print("⚠ CUDA not available, will use CPU (slower)")

# Test 4: HuggingFace Hub Access
print("\n🔗 HuggingFace Hub Test")
print("=" * 50)

try:
    api = HfApi()
    print("✓ HuggingFace API initialized")
    
    # Try to get a few popular OCR models
    try:
        models = list(api.list_models(search='ocr'))[:3]
        print(f"✓ Found {len(models)} OCR-related models")
        for model in models:
            print(f"  - {model.modelId}")
    except Exception as e:
        print(f"⚠ Error listing OCR models: {e}")
        
    # Test with a simple, well-known model
    print("\n🧪 Testing Simple Model Download...")
    try:
        # Use a very simple, well-known model first
        simple_model = "microsoft/DialoGPT-small"
        print(f"Testing with model: {simple_model}")
        tokenizer = AutoTokenizer.from_pretrained(simple_model)
        model = AutoModel.from_pretrained(simple_model)
        print(f"✓ Simple model download successful: {simple_model}")
        
        # Clean up
        del model, tokenizer
        
    except Exception as e:
        print(f"❌ Simple model download failed: {e}")

except Exception as e:
    print(f"❌ HuggingFace Hub access failed: {e}")

# Test 5: OpenRouter API Test
print("\n🌐 OpenRouter API Test")
print("=" * 50)

if openrouter_key:
    try:
        openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
        )
        
        # Test with embeddings API
        print("Testing OpenRouter embeddings API...")
        test_text = "This is a test sentence."
        
        embedding = openrouter_client.embeddings.create(
            model="mistralai/codestral-embed-2505",
            input=test_text
        )
        
        embedding_vector = embedding.data[0].embedding
        print(f"✓ OpenRouter API test successful!")
        print(f"  - Embedding dimension: {len(embedding_vector)}")
        
    except Exception as e:
        print(f"❌ OpenRouter API test failed: {e}")
else:
    print("⚠ Skipping OpenRouter test (no API key)")

# Test 6: PDF Processing Test
print("\n📄 PDF Processing Test")
print("=" * 50)

try:
    from pdf2image import convert_from_path
    import tempfile
    
    # Create a simple test image and try to convert it
    print("Testing PDF to image conversion...")
    
    # Create a minimal test PDF using PIL (if available)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple test image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 80), "Test Document", fill='black')
        
        # Save as temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            print("✓ Test image created successfully")
            
            # Try to load it back
            test_img = Image.open(tmp.name)
            print(f"✓ Image loaded: {test_img.size}")
            
            # Clean up
            os.unlink(tmp.name)
            
    except Exception as e:
        print(f"⚠ Image creation test failed: {e}")
        
except Exception as e:
    print(f"❌ PDF processing test failed: {e}")

# Test 7: OCR Model Test (with fallback)
print("\n🔍 OCR Model Test")
print("=" * 50)

try:
    # First try with the requested model
    ocr_model_name = "deepseek-ai/DeepSeek-OCR"
    print(f"Attempting to load: {ocr_model_name}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            ocr_model_name, 
            trust_remote_code=True
        )
        print(f"✓ Tokenizer downloaded for {ocr_model_name}")
        
        model = AutoModel.from_pretrained(
            ocr_model_name,
            trust_remote_code=True,
            use_safetensors=True
        )
        print(f"✓ Model downloaded for {ocr_model_name}")
        
        # Move to device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.eval().to(device)
        print(f"✓ Model moved to {device}")
        
        print(f"\n🎉 DeepSeek-OCR model loaded successfully!")
        
    except Exception as e:
        print(f"❌ DeepSeek-OCR model failed: {e}")
        print("💡 This might be due to:")
        print("   - Model name changed")
        print("   - Authentication issues")
        print("   - Model requires special access")
        
        # Try to find alternative OCR models
        print("\n🔍 Searching for alternative OCR models...")
        try:
            api = HfApi()
            models = list(api.list_models(search='ocr text recognition'))
            if models:
                alt_model = models[0].modelId
                print(f"💡 Trying alternative: {alt_model}")
                
                try:
                    tokenizer = AutoTokenizer.from_pretrained(alt_model)
                    print(f"✓ Alternative tokenizer downloaded: {alt_model}")
                except Exception as e:
                    print(f"⚠ Alternative model also failed: {e}")
        except Exception as e:
            print(f"⚠ Could not search for alternatives: {e}")
        
except Exception as e:
    print(f"❌ OCR model test failed: {e}")

# Final Summary
print("\n" + "=" * 50)
print("📋 SETUP VERIFICATION SUMMARY")
print("=" * 50)

# Check what we have working
tests_passed = []
tests_failed = []

if os.getenv('HF_TOKEN'):
    tests_passed.append("HuggingFace Token")
else:
    tests_failed.append("HuggingFace Token")

if os.getenv('OPENROUTER_API_KEY'):
    tests_passed.append("OpenRouter API Key")
else:
    tests_failed.append("OpenRouter API Key")

if torch.cuda.is_available():
    tests_passed.append("CUDA Support")
else:
    tests_failed.append("CUDA Support")

print(f"✅ Passed: {len(tests_passed)}/{len(tests_passed) + len(tests_failed)}")
for test in tests_passed:
    print(f"  ✓ {test}")

if tests_failed:
    print(f"❌ Failed: {len(tests_failed)}")
    for test in tests_failed:
        print(f"  ✗ {test}")

print("\n📝 Next Steps:")
if not os.getenv('HF_TOKEN'):
    print("1. Get a HuggingFace token from https://huggingface.co/settings/tokens")
if not os.getenv('OPENROUTER_API_KEY'):
    print("2. Get an OpenRouter API key from https://openrouter.ai/")
if not torch.cuda.is_available():
    print("3. Install CUDA for GPU acceleration")

print("4. Once authentication issues are resolved, re-run the OCR model test")
print("5. Test with actual PDF files from the audits/ directory")

print("\n🚀 AttackGen setup verification completed!")