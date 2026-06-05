#!/usr/bin/env python3
"""
Test Speed Optimization for Vision Models
Compare old vs new processing times
"""

import time
import os
from PIL import Image
import io

def test_optimized_vision():
    """Test the optimized vision service"""
    print("=" * 60)
    print("   SPEED OPTIMIZATION TEST")
    print("=" * 60)
    
    try:
        from services.optimized_vision_service import optimized_vision_service
        print("[OK] Optimized vision service imported")
        
        # Create a test image
        test_image = Image.new('RGB', (800, 600), color='white')
        
        print("\nTesting FAST analysis...")
        start_time = time.time()
        
        result = optimized_vision_service.analyze_medical_image_fast(
            test_image,
            document_type="lab_report",
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 RESULTS:")
        print(f"   Time taken: {elapsed:.1f} seconds")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Model: {result.get('model', 'unknown')}")
        
        if elapsed < 30:
            print("   [OK] FAST processing achieved!")
        elif elapsed < 60:
            print("   [WARNING] Acceptable speed")
        else:
            print("   [ERROR] Still too slow")
            
        return elapsed
        
    except Exception as e:
        print(f"❌ Error testing optimized service: {e}")
        return None

def test_standard_vision():
    """Test the standard vision service for comparison"""
    print("\n" + "=" * 60)
    print("   STANDARD VISION SERVICE TEST")
    print("=" * 60)
    
    try:
        from services.vision_service import vision_service
        print("[OK] Standard vision service imported")
        
        # Create a test image
        test_image = Image.new('RGB', (800, 600), color='white')
        
        print("\nTesting STANDARD analysis...")
        start_time = time.time()
        
        result = vision_service.analyze_medical_image(
            test_image,
            document_type="lab_report"
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 RESULTS:")
        print(f"   Time taken: {elapsed:.1f} seconds")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Model: {result.get('model', 'unknown')}")
        
        return elapsed
        
    except Exception as e:
        print(f"❌ Error testing standard service: {e}")
        return None

def main():
    """Run speed comparison tests"""
    print("Testing Vision Model Speed Optimization")
    print("This will compare old vs new processing speeds")
    
    # Test optimized version
    optimized_time = test_optimized_vision()
    
    # Test standard version
    standard_time = test_standard_vision()
    
    # Compare results
    print("\n" + "=" * 60)
    print("   SPEED COMPARISON")
    print("=" * 60)
    
    if optimized_time and standard_time:
        speedup = standard_time / optimized_time
        print(f"   Standard time: {standard_time:.1f}s")
        print(f"   Optimized time: {optimized_time:.1f}s")
        print(f"   Speed improvement: {speedup:.1f}x faster")
        
        if speedup > 2:
            print("   [OK] SIGNIFICANT speed improvement!")
        elif speedup > 1.5:
            print("   [OK] Good speed improvement")
        else:
            print("   [WARNING] Minimal improvement")
    else:
        print("   ⚠️ Could not complete comparison")
    
    print("\nOPTIMIZATIONS APPLIED:")
    print("   - Image preprocessing (resize for speed)")
    print("   - Reduced token generation (256 vs 512)")
    print("   - Optimized model loading")
    print("   - Memory management")
    print("   - Timeout handling")
    print("   - GPU memory clearing")

if __name__ == "__main__":
    main()
