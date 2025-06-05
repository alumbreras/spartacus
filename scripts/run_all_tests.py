#!/usr/bin/env python3
"""
Run all Spartacus tests and diagnostics
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Run all tests and diagnostics"""
    print("🧪 SPARTACUS COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    scripts = [
        ("Module Check", "scripts/check_modules.py"),
        ("Gmail Test", "scripts/test_gmail.py"),
        ("Backend Test", "scripts/test_backend.py"),
        ("Full Diagnostic", "doc_agent/system_diagnostic_report.py"),
        ("Formal Tests", ["python", "-m", "pytest", "test/", "-v"]),
    ]
    
    results = []
    
    for test_name, script_path in scripts:
        print(f"\n🔍 Running {test_name}...")
        print("-" * 40)
        
        try:
            if isinstance(script_path, list):
                # pytest command
                result = subprocess.run(
                    script_path,
                    cwd=project_root,
                    timeout=60
                )
            else:
                # Python script
                result = subprocess.run(
                    [sys.executable, script_path],
                    cwd=project_root,
                    timeout=60
                )
            
            success = result.returncode == 0
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} TIMED OUT")
            results.append((test_name, False))
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{len(results)} test suites passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  Some tests failed - check output above")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 