#!/usr/bin/env python3
"""
Test script to validate the LLM client fixes
"""

import sys
import os
import asyncio
import json

# Add the FastAPI directory to the path
sys.path.append('servers/fastapi')

def test_imports():
    """Test that all imports work correctly"""
    try:
        print("🔍 Testing imports...")
        
        # Test basic imports
        from services.llm_client import LLMClient
        print("✅ LLMClient imported successfully")
        
        from utils.llm_calls.improved_llm_client import ImprovedLLMClient
        print("✅ ImprovedLLMClient imported successfully")
        
        from utils.llm_calls.generate_slide_content import generate_slide_content_with_schema
        print("✅ generate_slide_content_with_schema imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_method_signatures():
    """Test that method signatures are correct"""
    try:
        print("\n🔍 Testing method signatures...")
        
        # Test LLMClient has generate_slide_content method
        from services.llm_client import LLMClient
        client = LLMClient()
        
        # Check if the method exists
        if hasattr(client, 'generate_slide_content'):
            print("✅ LLMClient has generate_slide_content method")
        else:
            print("❌ LLMClient missing generate_slide_content method")
            return False
        
        # Test ImprovedLLMClient
        from utils.llm_calls.improved_llm_client import ImprovedLLMClient
        improved_client = ImprovedLLMClient()
        
        if hasattr(improved_client, 'generate_slide_content'):
            print("✅ ImprovedLLMClient has generate_slide_content method")
        else:
            print("❌ ImprovedLLMClient missing generate_slide_content method")
            return False
            
        if hasattr(improved_client, '_generate_with_google'):
            print("✅ ImprovedLLMClient has _generate_with_google method")
        else:
            print("❌ ImprovedLLMClient missing _generate_with_google method")
            return False
            
        if hasattr(improved_client, '_generate_with_openai'):
            print("✅ ImprovedLLMClient has _generate_with_openai method")
        else:
            print("❌ ImprovedLLMClient missing _generate_with_openai method")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Method signature test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_validation():
    """Test schema validation functions"""
    try:
        print("\n🔍 Testing schema validation...")
        
        from utils.llm_calls.generate_slide_content import validate_slide_content_against_schema
        
        # Test with a simple schema
        test_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 3, "maxLength": 40},
                "description": {"type": "string", "minLength": 10, "maxLength": 150}
            },
            "required": ["title", "description"]
        }
        
        # Test with valid content
        test_content = {
            "title": "Test Title",
            "description": "This is a test description that meets the requirements"
        }
        
        result = validate_slide_content_against_schema(test_content, test_schema)
        print("✅ Schema validation working")
        print(f"   Result: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Schema validation test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting LLM Client Fix Validation Tests\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Method Signature Tests", test_method_signatures),
        ("Schema Validation Tests", test_schema_validation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
