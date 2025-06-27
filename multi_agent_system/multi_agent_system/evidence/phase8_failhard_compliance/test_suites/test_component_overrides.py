#!/usr/bin/env python3
"""
Test that all generated components properly override base methods
"""
import sys
import inspect
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_generated_components_override_base_methods():
    """Test that generated components properly override base class methods"""
    print("🔍 Testing Generated Components Override Base Methods")
    print("=" * 60)
    
    test_results = {}
    
    # Test Task Management API components
    print("\n📋 Testing Task Management API Components:")
    
    try:
        # Test Source component
        from examples.task_management_api.components.task_source import GeneratedSource_task_source
        from autocoder.components.source import Source
        
        print("\n  Testing GeneratedSource_task_source...")
        
        # Check that it inherits from Source
        assert issubclass(GeneratedSource_task_source, Source), "Should inherit from Source"
        print("    ✅ Inherits from Source base class")
        
        # Check that it overrides _generate_data
        source_generate_data = Source._generate_data
        generated_generate_data = GeneratedSource_task_source._generate_data
        
        assert source_generate_data != generated_generate_data, "_generate_data should be overridden"
        print("    ✅ Overrides _generate_data method")
        
        # Check that the override is not just calling super()
        source_code = inspect.getsource(generated_generate_data)
        assert "super()._generate_data" not in source_code, "Should not call super() for _generate_data"
        assert "NotImplementedError" not in source_code, "Should implement actual logic, not raise NotImplementedError"
        print("    ✅ Implements custom logic (not calling super or raising NotImplementedError)")
        
        test_results["task_source"] = True
        
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        test_results["task_source"] = False
    
    try:
        # Test Transformer component
        from examples.task_management_api.components.task_processor import GeneratedTransformer_task_processor
        from autocoder.components.transformer import Transformer
        
        print("\n  Testing GeneratedTransformer_task_processor...")
        
        # Check that it inherits from Transformer
        assert issubclass(GeneratedTransformer_task_processor, Transformer), "Should inherit from Transformer"
        print("    ✅ Inherits from Transformer base class")
        
        # Check that it overrides _transform_data
        transformer_transform_data = Transformer._transform_data
        generated_transform_data = GeneratedTransformer_task_processor._transform_data
        
        assert transformer_transform_data != generated_transform_data, "_transform_data should be overridden"
        print("    ✅ Overrides _transform_data method")
        
        # Check that the override implements actual logic
        source_code = inspect.getsource(generated_transform_data)
        assert "NotImplementedError" not in source_code, "Should implement actual logic"
        assert len(source_code) > 200, "Should have substantial implementation"
        print("    ✅ Implements substantial custom logic")
        
        test_results["task_processor"] = True
        
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        test_results["task_processor"] = False
    
    try:
        # Test Store component
        from examples.task_management_api.components.task_store import GeneratedStore_task_store
        from autocoder.components.v5_enhanced_store import V5EnhancedStore
        
        print("\n  Testing GeneratedStore_task_store...")
        
        # Check that it inherits from V5EnhancedStore
        assert issubclass(GeneratedStore_task_store, V5EnhancedStore), "Should inherit from V5EnhancedStore"
        print("    ✅ Inherits from V5EnhancedStore base class")
        
        # Check that it has _store_data method
        assert hasattr(GeneratedStore_task_store, '_store_data'), "Should have _store_data method"
        print("    ✅ Has _store_data method")
        
        # Check implementation quality
        source_code = inspect.getsource(GeneratedStore_task_store._store_data)
        assert "NotImplementedError" not in source_code, "Should implement actual logic"
        assert len(source_code) > 300, "Should have substantial implementation"
        print("    ✅ Implements substantial custom logic")
        
        test_results["task_store"] = True
        
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        test_results["task_store"] = False
    
    # Summary
    print("\n📊 Component Override Test Results:")
    print("=" * 40)
    
    passed_components = sum(test_results.values())
    total_components = len(test_results)
    success_rate = (passed_components / total_components) * 100
    
    for component_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {component_name}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_components}/{total_components})")
    
    if success_rate == 100:
        print("\n🎉 SUCCESS: All generated components properly override base methods!")
        print("   • No reliance on default implementations")
        print("   • Proper inheritance from correct base classes")  
        print("   • Substantial custom logic implementation")
        print("   • No NotImplementedError fallbacks")
        return True
    else:
        print("\n⚠️ Some components still using default implementations")
        return False

def test_base_methods_are_fail_hard():
    """Test that base class methods now fail hard instead of providing defaults"""
    print("\n🔍 Testing Base Class Methods Are Fail-Hard")
    print("=" * 50)
    
    try:
        from autocoder.components.source import Source
        from autocoder.components.transformer import Transformer
        from autocoder.components.sink import Sink
        from autocoder.components.model import Model
        
        # Test that base methods raise NotImplementedError
        base_classes = [
            (Source, "_generate_data"),
            (Transformer, "_transform_data"), 
            (Sink, "_output_data"),
            (Model, "_load_model"),
            (Model, "_run_inference")
        ]
        
        for base_class, method_name in base_classes:
            print(f"\n  Testing {base_class.__name__}.{method_name}...")
            
            # Get the method
            method = getattr(base_class, method_name)
            source_code = inspect.getsource(method)
            
            # Check that it raises NotImplementedError
            assert "NotImplementedError" in source_code, f"{method_name} should raise NotImplementedError"
            assert "NO FALLBACK" in source_code or "fail hard" in source_code.lower(), f"{method_name} should mention no fallback"
            print(f"    ✅ {base_class.__name__}.{method_name} properly fails hard")
        
        print("\n✅ All base class methods properly fail hard")
        return True
        
    except Exception as e:
        print(f"\n❌ Base class fail-hard test failed: {e}")
        return False

def main():
    """Run all component override tests"""
    print("🎯 Component Override Verification")
    print("=" * 50)
    print("Verifying that generated systems override base methods properly")
    print()
    
    # Test 1: Generated components override base methods
    test1_result = test_generated_components_override_base_methods()
    
    # Test 2: Base methods are fail-hard
    test2_result = test_base_methods_are_fail_hard()
    
    # Overall results
    print("\n📊 Final Results:")
    print("=" * 30)
    print(f"Generated Components Override: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Base Methods Fail-Hard: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    overall_success = test1_result and test2_result
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("   • Generated components properly override base methods")
        print("   • Base classes fail hard when methods not overridden")
        print("   • No reliance on default implementations")
        print("   • Fail-hard compliance achieved")
    else:
        print("\n❌ Some tests failed")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)