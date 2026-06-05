#!/usr/bin/env python3
"""
Test FAST Vision Service
Simple speed test without Unicode issues
"""

import time
from PIL import Image

def test_fast_vision():
    """Test the fast vision service"""
    print("=" * 50)
    print("   FAST VISION SERVICE TEST")
    print("=" * 50)
    
    try:
        from services.fast_vision_service import fast_vision_service
        print("[OK] Fast vision service imported")
        
        # Create a test image
        test_image = Image.new('RGB', (400, 300), color='white')
        
        print("\nTesting FAST analysis...")
        start_time = time.time()
        
        result = fast_vision_service.analyze_medical_image_fast(
            test_image,
            document_type="lab_report",
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        print(f"\nRESULTS:")
        print(f"   Time taken: {elapsed:.1f} seconds")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Model: {result.get('model', 'unknown')}")
        
        if elapsed < 10:
            print("   [OK] VERY FAST processing!")
        elif elapsed < 30:
            print("   [OK] FAST processing")
        elif elapsed < 60:
            print("   [WARNING] Acceptable speed")
        else:
            print("   [ERROR] Still too slow")
            
        return elapsed
        
    except Exception as e:
        print(f"[ERROR] Error testing fast service: {e}")
        return None

def main():
    """Run speed test"""
    print("Testing FAST Vision Model Speed")
    print("This will test the optimized processing speed")
    
    # Test fast version
    fast_time = test_fast_vision()
    
    print("\n" + "=" * 50)
    print("   SPEED TEST RESULTS")
    print("=" * 50)
    
    if fast_time:
        print(f"   Fast processing time: {fast_time:.1f}s")
        
        if fast_time < 10:
            print("   [OK] EXCELLENT speed!")
        elif fast_time < 30:
            print("   [OK] Good speed")
        else:
            print("   [WARNING] May still be slow")
    else:
        print("   [ERROR] Could not test")
    
    print("\nOPTIMIZATIONS APPLIED:")
    print("   - Image resizing (512x512 max)")
    print("   - Reduced token generation (128 tokens)")
    print("   - Fast model loading")
    print("   - Memory management")
    print("   - 30-second timeout")

if __name__ == "__main__":
    main()
