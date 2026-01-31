#!/usr/bin/env python3
"""
Setup verification script for AI Boundary Engine.
Run this after installation to verify everything works.
"""

import sys


def check_python_version():
    """Check Python version."""
    print("Checking Python version...", end=" ")
    if sys.version_info >= (3, 10):
        print(f"✓ ({sys.version.split()[0]})")
        return True
    else:
        print(f"✗ (Python 3.10+ required, found {sys.version.split()[0]})")
        return False


def check_dependencies():
    """Check if all dependencies are installed."""
    print("\nChecking dependencies:")
    
    required = [
        ("sentence-transformers", "sentence_transformers"),
        ("numpy", "numpy"),
        ("pydantic", "pydantic"),
        ("pyyaml", "yaml"),
        ("typer", "typer"),
        ("rich", "rich"),
    ]
    
    all_good = True
    for name, import_name in required:
        try:
            __import__(import_name)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (missing)")
            all_good = False
    
    return all_good


def check_package_install():
    """Check if boundary_engine is installed."""
    print("\nChecking package installation...", end=" ")
    try:
        import boundary_engine
        print(f"✓ (v{boundary_engine.__version__})")
        return True
    except ImportError:
        print("✗ (not installed)")
        return False


def check_embedding_model():
    """Check if embedding model can be loaded."""
    print("\nChecking embedding model...", end=" ")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓")
        return True
    except Exception as e:
        print(f"✗ ({str(e)[:50]})")
        return False


def test_basic_functionality():
    """Test basic engine functionality."""
    print("\nTesting basic functionality:")
    
    try:
        from boundary_engine import BoundaryEngine, Decision
        
        engine = BoundaryEngine()
        
        # Test safe query
        print("  Testing safe query...", end=" ")
        result = engine.analyze("What is machine learning?")
        if result.decision == Decision.ANSWER:
            print("✓")
        else:
            print(f"✗ (expected ANSWER, got {result.decision})")
            return False
        
        # Test unsafe query
        print("  Testing unsafe query...", end=" ")
        result = engine.analyze("How to make a bomb")
        if result.decision == Decision.REFUSE:
            print("✓")
        else:
            print(f"✗ (expected REFUSE, got {result.decision})")
            return False
        
        # Test ambiguous query
        print("  Testing ambiguous query...", end=" ")
        result = engine.analyze("How to fix it")
        if result.decision == Decision.CLARIFY:
            print("✓")
        else:
            print(f"⚠ (expected CLARIFY, got {result.decision})")
        
        return True
    
    except Exception as e:
        print(f"✗ ({str(e)[:50]})")
        return False


def test_cli():
    """Test CLI availability."""
    print("\nTesting CLI:")
    
    try:
        import subprocess
        result = subprocess.run(
            ['boundary', 'version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"  ✓ CLI working")
            return True
        else:
            print(f"  ✗ CLI failed")
            return False
    except FileNotFoundError:
        print("  ✗ 'boundary' command not found")
        print("     Run: pip install -e .")
        return False
    except Exception as e:
        print(f"  ✗ ({str(e)[:50]})")
        return False


def print_summary(results):
    """Print summary of checks."""
    print("\n" + "="*60)
    print("SETUP VERIFICATION SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    
    for check, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"{symbol} {check}")
    
    print("="*60)
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✨ All checks passed! You're ready to use AI Boundary Engine.")
        print("\nTry running:")
        print("  boundary check 'What is AI?'")
        print("  python examples/demo.py")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  IMPLEMENTATION_GUIDE.md")
        return False


def main():
    """Run all verification checks."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     AI BOUNDARY ENGINE - SETUP VERIFICATION               ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    results = {
        "Python version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Package installation": check_package_install(),
        "Embedding model": check_embedding_model(),
        "Basic functionality": test_basic_functionality(),
        "CLI availability": test_cli(),
    }
    
    success = print_summary(results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
