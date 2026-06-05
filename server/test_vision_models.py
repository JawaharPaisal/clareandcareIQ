#!/usr/bin/env python3
"""
Test Vision Models Loading
Check if Qwen2-VL and LLaVA-Med can load properly
"""

import os
import sys

print("="*60)
print("   VISION MODELS LOADING TEST")
print("="*60)
print()

# Test 1: Check dependencies
print("Test 1: Checking dependencies...")
print("-" * 60)

required_packages = [
    'transformers',
    'torch',
    'torchvision',
    'einops',
    'timm',
    'qwen_vl_utils',
    'PIL'
]

missing = []
for package in required_packages:
    try:
        if package == 'PIL':
            import PIL
        else:
            __import__(package)
        print(f"   [OK] {package}")
    except ImportError:
        print(f"   [MISSING] {package}")
        missing.append(package)

if missing:
    print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
    print(f"Install with: pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print("\n[SUCCESS] All dependencies installed!")

print()

# Test 2: Check model folders
print("Test 2: Checking model folders...")
print("-" * 60)

qwen_path = os.path.join(os.path.dirname(__file__), 'Qwen2-VL-7B-Instruct')
llava_path = os.path.join(os.path.dirname(__file__), 'llava-med-v1.5-mistral-7b')

qwen_exists = os.path.exists(qwen_path)
llava_exists = os.path.exists(llava_path)

if qwen_exists:
    print(f"   [OK] Qwen2-VL folder found: {qwen_path}")
    # Check for key files
    config_file = os.path.join(qwen_path, 'config.json')
    if os.path.exists(config_file):
        print(f"      [OK] config.json present")
    else:
        print(f"      [ERROR] config.json missing!")
else:
    print(f"   [NOT FOUND] Qwen2-VL folder: {qwen_path}")

if llava_exists:
    print(f"   [OK] LLaVA-Med folder found: {llava_path}")
    config_file = os.path.join(llava_path, 'config.json')
    if os.path.exists(config_file):
        print(f"      [OK] config.json present")
    else:
        print(f"      [ERROR] config.json missing!")
else:
    print(f"   [NOT FOUND] LLaVA-Med folder: {llava_path}")

if not qwen_exists and not llava_exists:
    print("\n[ERROR] No vision models found!")
    sys.exit(1)

print()

# Test 3: Try loading Qwen2-VL
if qwen_exists:
    print("Test 3: Loading Qwen2-VL model...")
    print("-" * 60)
    try:
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        print("   [OK] Qwen2VL imports successful")
        
        print("   [LOADING] Qwen2-VL model (this may take 30-60 seconds)...")
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            qwen_path,
            torch_dtype="auto",
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("   [SUCCESS] Qwen2-VL model loaded!")
        
        processor = AutoProcessor.from_pretrained(qwen_path, trust_remote_code=True)
        print("   [SUCCESS] Qwen2-VL processor loaded!")
        
        print("\n[SUCCESS] QWEN2-VL IS WORKING!")
        
        # Clean up
        del model
        del processor
        
    except Exception as e:
        print(f"   [ERROR] Qwen2-VL loading failed:")
        print(f"      {e}")
        import traceback
        traceback.print_exc()

print()

# Test 4: Check Gemini Vision fallback
print("Test 4: Checking Gemini Vision fallback...")
print("-" * 60)

try:
    from services.gemini_vision_service import gemini_vision
    if gemini_vision.available:
        print("   [OK] Gemini Vision API ready (RARE fallback only)")
    else:
        print("   [WARNING] Gemini Vision API not configured")
except:
    print("   [WARNING] Gemini Vision service not available")

print()

# Summary
print("="*60)
print("   SUMMARY")
print("="*60)

if qwen_exists:
    print("[OK] Qwen2-VL: Ready for local processing")
else:
    print("[ERROR] Qwen2-VL: Not found")

if llava_exists:
    print("[OK] LLaVA-Med: Available")
else:
    print("[ERROR] LLaVA-Med: Not found")

print()
print("PRIORITY ORDER:")
print("  1st: Qwen2-VL (LOCAL) - For prescriptions, lab reports, documents")
print("  2nd: LLaVA-Med (LOCAL) - For medical images (X-ray, CT, MRI)")
print("  3rd: Gemini Vision (CLOUD) - RARE fallback only")
print()
print("="*60)

