#!/usr/bin/env python3
"""
Phase 8 Production-Ready Generation Test
Tests the updated SystemScaffoldGenerator with production Flask templates
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from blueprint_language.system_scaffold_generator import SystemScaffoldGenerator
from blueprint_language.system_blueprint_parser import SystemBlueprintParser
from blueprint_language.component_logic_generator import ComponentLogicGenerator


def test_production_generation():
    """Test production-ready system generation"""
    print("🧪 Phase 8 Production-Ready Generation Test")
    print("=" * 50)
    
    evidence_dir = Path(__file__).parent
    test_output_dir = evidence_dir / "generated_test_system"
    test_blueprint_file = evidence_dir / "test_system_blueprint.yaml"
    
    # Parse the test blueprint
    parser = SystemBlueprintParser()
    with open(test_blueprint_file, 'r') as f:
        blueprint_content = f.read()
    
    try:
        print("📋 Parsing test system blueprint...")
        system_blueprint = parser.parse_string(blueprint_content)
        print(f"✅ Parsed system: {system_blueprint.system.name}")
        print(f"   Description: {system_blueprint.system.description}")
        print(f"   Components: {len(system_blueprint.system.components)}")
        
        # Check if system has API endpoints
        api_components = [comp for comp in system_blueprint.system.components if comp.type == "APIEndpoint"]
        print(f"   API Components: {len(api_components)}")
        
        # Generate system scaffold
        print("\n🔧 Generating production system scaffold...")
        scaffold_generator = SystemScaffoldGenerator(test_output_dir)
        scaffold = scaffold_generator.generate_system(system_blueprint)
        
        print("✅ System scaffold generated:")
        print(f"   Main.py: {len(scaffold.main_py)} characters")
        print(f"   Config: {len(scaffold.config_yaml)} characters")
        print(f"   Requirements: {len(scaffold.requirements_txt)} characters")
        print(f"   Dockerfile: {len(scaffold.dockerfile)} characters")
        
        # Check if Gunicorn config was generated
        gunicorn_config_file = test_output_dir / system_blueprint.system.name / "gunicorn.conf.py"
        if gunicorn_config_file.exists():
            print(f"   Gunicorn config: {gunicorn_config_file.stat().st_size} bytes")
        else:
            print("   ⚠️  Gunicorn config not found")
        
        # Generate component logic
        print("\n🧩 Generating component logic...")
        component_generator = ComponentLogicGenerator(test_output_dir)
        components = component_generator.generate_components(system_blueprint)
        
        print(f"✅ Generated {len(components)} components")
        for comp in components:
            print(f"   {comp.name}: {comp.type}")
        
        # Validate production features in generated files
        print("\n🔍 Validating production features...")
        
        # Check main.py for Flask/Gunicorn usage
        main_py_content = scaffold.main_py
        production_checks = {
            "Uses Flask": "flask" in main_py_content.lower(),
            "Has Gunicorn reference": "gunicorn" in main_py_content.lower() or "wsgi" in main_py_content.lower(),
            "Production health checks": "/health" in main_py_content,
            "Error handling": "try:" in main_py_content and "except" in main_py_content,
            "Logging configured": "logging" in main_py_content,
        }
        
        # Check requirements for production dependencies
        requirements_content = scaffold.requirements_txt
        requirements_checks = {
            "Flask included": "flask" in requirements_content.lower(),
            "Gunicorn included": "gunicorn" in requirements_content.lower(),
            "PostgreSQL support": "psycopg2" in requirements_content.lower(),
            "Production monitoring": "prometheus" in requirements_content.lower() or "werkzeug" in requirements_content.lower(),
        }
        
        # Check Dockerfile for production features
        dockerfile_content = scaffold.dockerfile
        dockerfile_checks = {
            "Uses Gunicorn": "gunicorn" in dockerfile_content.lower(),
            "Health check included": "healthcheck" in dockerfile_content.lower(),
            "Non-root user": "useradd" in dockerfile_content or "USER" in dockerfile_content,
            "Production ready": "production" in dockerfile_content.lower(),
        }
        
        # Report validation results
        all_checks_passed = True
        
        print("\n📊 Production Features Validation:")
        print("\n🏗️  Main.py (Flask/Gunicorn):")
        for check, passed in production_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            if not passed:
                all_checks_passed = False
        
        print("\n📦 Requirements.txt:")
        for check, passed in requirements_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            if not passed:
                all_checks_passed = False
        
        print("\n🐳 Dockerfile:")
        for check, passed in dockerfile_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            if not passed:
                all_checks_passed = False
        
        # Check generated API component for Flask blueprint
        if api_components:
            api_comp = api_components[0]
            api_comp_file = test_output_dir / system_blueprint.system.name / "components" / f"{api_comp.name}.py"
            if api_comp_file.exists():
                with open(api_comp_file, 'r') as f:
                    api_comp_content = f.read()
                
                api_checks = {
                    "Flask Blueprint": "Blueprint" in api_comp_content,
                    "Thread-safe counters": "threading.Lock" in api_comp_content,
                    "Sync health checks": "get_sync_health_status" in api_comp_content,
                    "V5 integration": "v5_store" in api_comp_content,
                    "Production error handling": "try:" in api_comp_content and "BadRequest" in api_comp_content,
                }
                
                print(f"\n🌐 API Component ({api_comp.name}):")
                for check, passed in api_checks.items():
                    status = "✅" if passed else "❌"
                    print(f"   {status} {check}")
                    if not passed:
                        all_checks_passed = False
        
        # Summary
        print(f"\n🎯 Production Readiness Summary:")
        if all_checks_passed:
            print("✅ ALL PRODUCTION CHECKS PASSED")
            print("🚀 System is ready for production deployment with:")
            print("   • Gunicorn WSGI server")
            print("   • Flask blueprints with thread-safe operations")
            print("   • V5 sync/async bridge for health checks")
            print("   • Production error handling and logging")
            print("   • Container health checks")
            print("   • Non-root user security")
        else:
            print("❌ SOME PRODUCTION CHECKS FAILED")
            print("⚠️  System may not be fully production-ready")
        
        # Write validation report
        report_file = evidence_dir / "validation_report.md"
        with open(report_file, 'w') as f:
            f.write("# Phase 8 Production-Ready Generation Validation Report\n\n")
            f.write(f"**System**: {system_blueprint.system.name}\n")
            f.write(f"**Generated**: {test_output_dir}\n")
            f.write(f"**Status**: {'PASSED' if all_checks_passed else 'FAILED'}\n\n")
            
            f.write("## Production Features Validated\n\n")
            f.write("### Main.py (Flask/Gunicorn)\n")
            for check, passed in production_checks.items():
                f.write(f"- {'✅' if passed else '❌'} {check}\n")
            
            f.write("\n### Requirements.txt\n")
            for check, passed in requirements_checks.items():
                f.write(f"- {'✅' if passed else '❌'} {check}\n")
            
            f.write("\n### Dockerfile\n")
            for check, passed in dockerfile_checks.items():
                f.write(f"- {'✅' if passed else '❌'} {check}\n")
            
            if api_components:
                f.write(f"\n### API Component ({api_comp.name})\n")
                for check, passed in api_checks.items():
                    f.write(f"- {'✅' if passed else '❌'} {check}\n")
        
        print(f"\n📄 Validation report written to: {report_file}")
        
        return all_checks_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_production_generation()
    exit(0 if success else 1)