#!/usr/bin/env python3
"""
Jarvis Personal Assistant - Verification Script
Checks all prerequisites and dependencies before running.
"""

import subprocess
import sys
import importlib
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check Python version (3.10+)."""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}\n")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor} (need 3.10+)\n")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("✓ Checking installed packages...")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'requests': 'Requests',
        'pinecone': 'Pinecone',
        'sentence_transformers': 'Sentence Transformers',
        'streamlit': 'Streamlit',
    }
    
    all_installed = True
    for package, name in required.items():
        try:
            importlib.import_module(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} (not installed)")
            all_installed = False
    
    print()
    return all_installed


def check_env_file():
    """Check if .env file exists."""
    print("✓ Checking environment configuration...")
    
    env_path = Path(".env")
    if env_path.exists():
        print("  ✅ .env file found\n")
        return True
    else:
        print("  ⚠️  .env file not found")
        print("  → Copy from .env.example and add your PINECONE_API_KEY\n")
        return False


def check_ollama():
    """Check if Ollama is running."""
    print("✓ Checking Ollama connection...")
    
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            print("  ✅ Ollama is running on localhost:11434\n")
            return True
    except Exception:
        pass
    
    print("  ⚠️  Ollama not running")
    print("  → Start with: ollama serve\n")
    return False


def check_project_structure():
    """Check project folder structure."""
    print("✓ Checking project structure...")
    
    required_dirs = [
        "backend",
        "frontend",
        "data"
    ]
    
    required_files = [
        "requirements.txt",
        "README.md",
        "backend/main.py",
        "backend/rag.py",
        "backend/vector_db.py",
        "backend/llm.py",
        "backend/embeddings.py",
        "frontend/app.py",
        "data/init_data.py",
    ]
    
    all_exist = True
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (missing)")
            all_exist = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            all_exist = False
    
    print()
    return all_exist


def main():
    """Run all checks."""
    print_header("Jarvis - Startup Verification")
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Ollama Server", check_ollama),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"⚠️  Error checking {name}: {str(e)}\n")
            results[name] = False
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "⚠️  CHECK"
        print(f"{status}  {name}")
    
    print(f"\n{passed}/{total} checks passed")
    
    # Instructions
    print_header("Next Steps")
    
    if not results["Python Version"]:
        print("❌ Upgrade Python to 3.10+")
        return False
    
    if not results["Project Structure"]:
        print("❌ Some files are missing. Check the structure.")
        return False
    
    if not results["Dependencies"]:
        print("⚠️  Install dependencies:")
        print("    pip install -r requirements.txt")
        print()
    
    if not results["Environment Configuration"]:
        print("⚠️  Configure environment:")
        print("    cp .env.example .env")
        print("    # Edit .env and add PINECONE_API_KEY")
        print()
    
    if not results["Ollama Server"]:
        print("⚠️  Start Ollama in a separate terminal:")
        print("    ollama pull llama3")
        print("    ollama serve")
        print()
    
    print("✅ Start the system:")
    print("   Terminal 1: ollama serve")
    print("   Terminal 2: cd backend && python main.py")
    print("   Terminal 3: cd data && python init_data.py")
    print("   Terminal 4: cd frontend && streamlit run app.py")
    print()
    print("Then open: http://localhost:8501")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
