#!/usr/bin/env python3
"""
Integration Structure Verification
Checks that all files and directories are created correctly
"""

from pathlib import Path

def check_structure():
    """Verify directory structure and files."""
    print("=" * 60)
    print("ZETA Bot Integration Structure Verification")
    print("=" * 60)
    
    base = Path(__file__).parent
    
    required_files = [
        # Integration system
        "integrations/__init__.py",
        "integrations/manager.py",
        "integrations/onec.py",
        "integrations/bitrix24.py",
        "integrations/README.md",
        
        # Core features
        "core/memory.py",
        "core/rate_limiter.py",
        "core/i18n.py",
        
        # Handlers
        "handlers/document_search.py",
        
        # Config
        "config/integrations.yaml",
        
        # Documentation
        "INTEGRATION_GUIDE.md",
        "INTEGRATION_ARCHITECTURE.md",
        
        # Requirements
        "requirements-integrations.txt",
        
        # Tests
        "test_integrations.py",
        "verify_structure.py",
    ]
    
    api_files = [
        "../api/app/routers/documents.py"
    ]
    
    print("\n📁 Checking bot directory structure...\n")
    
    missing = []
    found = []
    
    for file_path in required_files:
        full_path = base / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size:,} bytes)")
            found.append(file_path)
        else:
            print(f"❌ {file_path} - NOT FOUND")
            missing.append(file_path)
    
    print("\n📁 Checking API directory...\n")
    
    for file_path in api_files:
        full_path = base / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size:,} bytes)")
            found.append(file_path)
        else:
            print(f"❌ {file_path} - NOT FOUND")
            missing.append(file_path)
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"✅ Files found: {len(found)}")
    print(f"❌ Files missing: {len(missing)}")
    
    if missing:
        print("\nMissing files:")
        for f in missing:
            print(f"  • {f}")
    
    print("\n" + "=" * 60)
    
    # Calculate total size
    total_size = sum((base / f).stat().st_size for f in required_files if (base / f).exists())
    total_size += sum((base / f).stat().st_size for f in api_files if (base / f).exists())
    
    print(f"📦 Total code size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    # Count lines of code
    total_lines = 0
    for file_path in required_files + api_files:
        full_path = base / file_path
        if full_path.exists() and full_path.suffix == '.py':
            with open(full_path) as f:
                lines = len(f.readlines())
                total_lines += lines
    
    print(f"📝 Total Python LOC: {total_lines:,} lines")
    
    print("\n" + "=" * 60)
    
    if not missing:
        print("🎉 ALL FILES PRESENT!")
        print("✅ Integration foundation structure is complete")
        return True
    else:
        print("⚠️  SOME FILES MISSING")
        print("❌ Review missing files above")
        return False


def check_imports_syntax():
    """Check Python files for syntax errors."""
    print("\n" + "=" * 60)
    print("🐍 Checking Python syntax...")
    print("=" * 60 + "\n")
    
    import py_compile
    
    base = Path(__file__).parent
    
    py_files = [
        "integrations/__init__.py",
        "integrations/manager.py",
        "integrations/onec.py",
        "integrations/bitrix24.py",
        "core/memory.py",
        "core/rate_limiter.py",
        "core/i18n.py",
        "handlers/document_search.py",
        "test_integrations.py",
    ]
    
    errors = []
    
    for file_path in py_files:
        full_path = base / file_path
        if not full_path.exists():
            continue
        
        try:
            py_compile.compile(str(full_path), doraise=True)
            print(f"✅ {file_path}")
        except py_compile.PyCompileError as e:
            print(f"❌ {file_path}: {e}")
            errors.append(file_path)
    
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ {len(errors)} files have syntax errors")
        return False
    else:
        print("✅ All Python files have valid syntax")
        return True


def check_yaml_syntax():
    """Check YAML config file."""
    print("\n" + "=" * 60)
    print("📝 Checking YAML syntax...")
    print("=" * 60 + "\n")
    
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not installed, skipping YAML check")
        return True
    
    base = Path(__file__).parent
    config_file = base / "config" / "integrations.yaml"
    
    if not config_file.exists():
        print("❌ Config file not found")
        return False
    
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        print(f"✅ {config_file.name}")
        print(f"\n📋 Config sections:")
        for key in config.keys():
            print(f"  • {key}")
        
        return True
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False


def print_summary():
    """Print summary of what was built."""
    print("\n" + "=" * 60)
    print("📋 INTEGRATION FOUNDATION SUMMARY")
    print("=" * 60)
    
    print("""
✅ COMPLETED:

1. Plugin/Integration System
   • Abstract Integration base class
   • IntegrationManager for orchestration
   • Pluggable architecture

2. Integration Stubs
   • 1C:Enterprise connector (stub with TODOs)
   • Bitrix24 CRM connector (stub with TODOs)
   • Clear implementation path

3. Advanced Features
   • Conversation memory (Redis-based)
   • Rate limiting middleware
   • Multilanguage support (RU/KK)

4. Document System
   • Upload API endpoints
   • Search handler for bot
   • Stubs for text extraction & embeddings

5. Configuration
   • Comprehensive YAML config
   • Environment variable support
   • Feature toggles

6. Documentation
   • Integration architecture overview
   • Step-by-step implementation guide
   • Usage examples and troubleshooting

🚀 NEXT PHASE:
   • Implement 1C connector
   • Implement Bitrix24 connector
   • Setup Redis for memory/rate limiting
   • Deploy vector database for document search
   • Enable features in config

📖 READ:
   • INTEGRATION_ARCHITECTURE.md - Overview
   • INTEGRATION_GUIDE.md - Implementation steps
   • integrations/README.md - Usage examples
   • config/integrations.yaml - Configuration options
""")
    
    print("=" * 60)


if __name__ == "__main__":
    structure_ok = check_structure()
    syntax_ok = check_imports_syntax()
    yaml_ok = check_yaml_syntax()
    
    print_summary()
    
    print("\n" + "=" * 60)
    if structure_ok and syntax_ok and yaml_ok:
        print("🎉 VERIFICATION COMPLETE - ALL CHECKS PASSED!")
        print("✅ Ready for Phase 2 implementation")
    else:
        print("⚠️  VERIFICATION INCOMPLETE")
        print("❌ Fix issues above before proceeding")
    print("=" * 60 + "\n")
