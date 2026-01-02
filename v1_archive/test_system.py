#!/usr/bin/env python3
"""
Quick System Test
"""

import sys
from pathlib import Path

def test_imports():
    """Test alle wichtigen Imports"""
    print("🔍 Testing imports...\n")
    
    tests = {
        'torch': 'PyTorch',
        'whisper': 'Whisper',
        'cv2': 'OpenCV',
        'ffmpeg': 'FFmpeg-Python',
        'transformers': 'Transformers',
        'scenedetect': 'PySceneDetect'
    }
    
    failed = []
    for module, name in tests.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            failed.append(name)
    
    return len(failed) == 0

def test_device():
    """Test GPU/Device"""
    print("\n🎮 Testing device...\n")
    
    try:
        from backend.utils.device_utils import get_device_info
        info = get_device_info()
        
        print(f"Device: {info['device']}")
        print(f"Type: {info['type']}")
        print(f"Platform: {info['platform']}")
        
        return True
    except Exception as e:
        print(f"❌ Device test failed: {e}")
        return False

def test_video_processor():
    """Test VideoProcessor"""
    print("\n🎬 Testing VideoProcessor...\n")
    
    try:
        from backend.processors.video_processor import VideoProcessor
        print("✅ VideoProcessor imported")
        return True
    except Exception as e:
        print(f"❌ VideoProcessor test failed: {e}")
        return False

def test_transcriber():
    """Test Transcriber"""
    print("\n🎤 Testing Transcriber...\n")
    
    try:
        from backend.processors.transcriber import Transcriber
        print("✅ Transcriber imported")
        
        # Optional: Load model (nimmt Zeit)
        # transcriber = Transcriber(model_size="tiny")
        # print("✅ Model loaded")
        
        return True
    except Exception as e:
        print(f"❌ Transcriber test failed: {e}")
        return False

def test_storage():
    """Test Storage Setup"""
    print("\n📁 Testing storage...\n")
    
    try:
        from backend.core.config import settings
        
        paths = [
            settings.STORAGE_PATH,
            settings.MODEL_PATH,
            settings.STORAGE_PATH / "uploads",
            settings.STORAGE_PATH / "outputs"
        ]
        
        for path in paths:
            if path.exists():
                print(f"✅ {path}")
            else:
                print(f"⚠️  Creating: {path}")
                path.mkdir(parents=True, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False

def main():
    print("="*60)
    print("🍎 CUSTOM CLIP FINDER - SYSTEM TEST")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Device", test_device),
        ("Storage", test_storage),
        ("VideoProcessor", test_video_processor),
        ("Transcriber", test_transcriber),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("\n📚 Next steps:")
        print("   1. Add test video: ~/custom-clip-finder/data/uploads/test.mp4")
        print("   2. Run demo: python demo.py")
        print("   3. Start API: uvicorn backend.api.main:app --reload")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
