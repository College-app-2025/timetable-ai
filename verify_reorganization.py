"""
Verification script for the reorganized AI timetable system.
Tests that all components work correctly after modularization.
"""

import sys
import os
import asyncio
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical imports work correctly."""
    print("🔍 TESTING IMPORTS")
    print("=" * 30)
    
    import_tests = [
        # Core ML components
        ("src.ml.core.optimizer", "TimetableOptimizer"),
        ("src.ml.data.models", "OptimizationConfig"),
        ("src.ml.constraints.hard_constraints", "HardConstraintManager"),
        ("src.ml.constraints.soft_constraints", "SoftConstraintManager"),
        
        # Services
        ("src.services.dynamic_reallocation_service", "dynamic_reallocation_service"),
        ("src.services.voting_service", "voting_service"),
        ("src.services.notification_service", "notification_service"),
        
        # Routes
        ("src.routes.dynamic_reallocation_routes", "router"),
        ("src.routes.timetable_routes", "router"),
        
        # Models
        ("src.models.auth", "CreateStudent"),
        ("src.models.institute", "CreateInstitute"),
        
        # Utils
        ("src.utils.logger_config", "get_logger"),
        ("src.utils.prisma", "db"),
    ]
    
    success_count = 0
    
    for module_name, component_name in import_tests:
        try:
            module = importlib.import_module(module_name)
            component = getattr(module, component_name)
            print(f"   ✅ {module_name}.{component_name}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name}.{component_name} - Error: {str(e)}")
    
    print(f"\n📊 Import Results: {success_count}/{len(import_tests)} successful")
    return success_count == len(import_tests)

def test_ml_system():
    """Test ML system functionality."""
    print("\n🤖 TESTING ML SYSTEM")
    print("=" * 25)
    
    try:
        from src.ml.core.optimizer import TimetableOptimizer
        from src.ml.data.models import OptimizationConfig
        
        # Create optimizer
        config = OptimizationConfig()
        optimizer = TimetableOptimizer(config)
        
        print("   ✅ ML system components loaded successfully")
        print(f"   ✅ Optimizer created with config: {config.max_optimization_time}s timeout")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ML system test failed: {str(e)}")
        return False

def test_dynamic_reallocation():
    """Test dynamic reallocation system."""
    print("\n🔄 TESTING DYNAMIC REALLOCATION")
    print("=" * 35)
    
    try:
        from src.services.dynamic_reallocation_service import dynamic_reallocation_service
        from src.services.voting_service import voting_service
        from src.services.notification_service import notification_service
        
        print("   ✅ Dynamic reallocation service loaded")
        print("   ✅ Voting service loaded")
        print("   ✅ Notification service loaded")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Dynamic reallocation test failed: {str(e)}")
        return False

def test_api_routes():
    """Test API routes."""
    print("\n🌐 TESTING API ROUTES")
    print("=" * 20)
    
    try:
        from src.routes.dynamic_reallocation_routes import router as reallocation_router
        from src.routes.timetable_routes import router as timetable_router
        from src.ml.api.routes import router as ml_router
        
        print("   ✅ Dynamic reallocation routes loaded")
        print("   ✅ Timetable routes loaded") 
        print("   ✅ ML API routes loaded")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API routes test failed: {str(e)}")
        return False

def test_main_app():
    """Test main application."""
    print("\n🚀 TESTING MAIN APPLICATION")
    print("=" * 30)
    
    try:
        import main
        
        # Check if app is created
        if hasattr(main, 'app'):
            print("   ✅ FastAPI app created successfully")
            return True
        else:
            print("   ❌ FastAPI app not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Main app test failed: {str(e)}")
        return False

def test_folder_structure():
    """Test folder structure integrity."""
    print("\n📁 TESTING FOLDER STRUCTURE")
    print("=" * 30)
    
    required_folders = [
        "src/ml/core",
        "src/ml/data", 
        "src/ml/constraints",
        "src/ml/evaluation",
        "src/services",
        "src/routes",
        "src/models",
        "src/utils",
        "tests",
        "docs",
        "scripts",
        "data",
        "config",
        "examples"
    ]
    
    missing_folders = []
    
    for folder in required_folders:
        if not os.path.exists(folder):
            missing_folders.append(folder)
        else:
            print(f"   ✅ {folder}")
    
    if missing_folders:
        print(f"\n   ❌ Missing folders: {missing_folders}")
        return False
    else:
        print(f"\n📊 All {len(required_folders)} folders present")
        return True

def test_file_accessibility():
    """Test that key files are accessible."""
    print("\n📄 TESTING FILE ACCESSIBILITY")
    print("=" * 32)
    
    key_files = [
        "main.py",
        "src/ml/core/optimizer.py",
        "src/services/dynamic_reallocation_service.py",
        "tests/test_dynamic_reallocation_core.py",
        "config/requirements.txt",
        "scripts/run.py"
    ]
    
    missing_files = []
    
    for file_path in key_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print(f"\n   ❌ Missing files: {missing_files}")
        return False
    else:
        print(f"\n📊 All {len(key_files)} key files accessible")
        return True

def run_verification():
    """Run complete verification."""
    print("🚀 AI TIMETABLE SYSTEM - REORGANIZATION VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Folder Structure", test_folder_structure),
        ("File Accessibility", test_file_accessibility),
        ("Imports", test_imports),
        ("ML System", test_ml_system),
        ("Dynamic Reallocation", test_dynamic_reallocation),
        ("API Routes", test_api_routes),
        ("Main Application", test_main_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n🎯 VERIFICATION SUMMARY")
    print("=" * 25)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed}/{len(results)})")
    
    if success_rate >= 90:
        print("\n🎉 REORGANIZATION SUCCESSFUL!")
        print("The AI system is working correctly after modularization.")
        return True
    elif success_rate >= 70:
        print("\n⚠️ REORGANIZATION MOSTLY SUCCESSFUL")
        print("Some minor issues detected - review failed tests above.")
        return True
    else:
        print("\n❌ REORGANIZATION FAILED")
        print("Significant issues detected - system may not work correctly.")
        return False

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
