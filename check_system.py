"""
E-Commerce Intelligence - System Diagnostic & Setup Script
Automatically checks and fixes common issues
Windows Compatible Version
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    print_header("[1] CHECKING PYTHON VERSION")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 10:
        print("[OK] Python version is compatible (3.10+)")
        return True
    else:
        print("[FAIL] Python 3.10+ required. Current version too old.")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("[2] CHECKING DEPENDENCIES")

    required_packages = [
        "pandas", "numpy", "requests", "beautifulsoup4",
        "fastapi", "uvicorn", "prophet", "xgboost",
        "sklearn", "openpyxl", "python-dotenv"
    ]

    missing = []
    installed = []

    for package in required_packages:
        try:
            if package == "sklearn":
                __import__("sklearn")
            elif package == "beautifulsoup4":
                __import__("bs4")
            elif package == "python-dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            installed.append(package)
            print(f"[OK] {package}")
        except ImportError:
            missing.append(package)
            print(f"[MISSING] {package}")

    if missing:
        print(f"\n[WARNING] Missing {len(missing)} packages")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    else:
        print(f"\n[OK] All {len(installed)} packages installed!")
        return True

def check_project_structure():
    """Verify project folder structure"""
    print_header("[3] CHECKING PROJECT STRUCTURE")

    base_dir = Path(__file__).parent
    required_dirs = ["data", "data/raw", "data/cleaned", "data/models",
                     "src", "frontend", "logs", "notebooks"]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"[OK] {dir_name}/")
        else:
            print(f"[MISSING] {dir_name}/ - Creating...")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   -> Created {dir_name}/")
            all_exist = False

    if all_exist:
        print("\n[OK] Project structure is complete")
    else:
        print("\n[INFO] Created missing directories")
    return True

def check_config():
    """Test configuration file"""
    print_header("[4] CHECKING CONFIGURATION")

    try:
        sys.path.append(str(Path(__file__).parent / 'src'))
        from config import BASE_DIR, DATA_DIR, OPENROUTER_API_KEY

        print(f"[OK] Config loaded successfully")
        print(f"   Base Dir: {BASE_DIR}")
        print(f"   Data Dir: {DATA_DIR}")
        print(f"   API Key: {'Set' if OPENROUTER_API_KEY else 'Missing'}")
        return True
    except Exception as e:
        print(f"[FAIL] Config error: {str(e)}")
        return False

def check_data_availability():
    """Check if data files exist"""
    print_header("[5] CHECKING DATA AVAILABILITY")

    base_dir = Path(__file__).parent
    raw_data = list((base_dir / "data" / "raw").glob("*.csv"))
    cleaned_data = list((base_dir / "data" / "cleaned").glob("*.csv"))

    print(f"Raw Data Files: {len(raw_data)}")
    print(f"Cleaned Data Files: {len(cleaned_data)}")

    if raw_data:
        print(f"[OK] Found {len(raw_data)} raw data file(s)")
        for f in raw_data[:3]:  # Show first 3
            print(f"   - {f.name}")
    else:
        print("[INFO] No raw data found. Run scraper first:")
        print("   python main.py --step scrape")

    return len(raw_data) > 0

def test_api_server():
    """Test if API server can start"""
    print_header("[6] TESTING API SERVER")

    try:
        sys.path.append(str(Path(__file__).parent / 'src'))
        import api_server
        print("[OK] API server module loads successfully")
        print("   Start with: python src/api_server.py")
        return True
    except Exception as e:
        print(f"[FAIL] API server error: {str(e)}")
        return False

def print_summary(results):
    """Print final summary"""
    print_header("DIAGNOSTIC SUMMARY")

    checks = [
        ("Python Version", results[0]),
        ("Dependencies", results[1]),
        ("Project Structure", results[2]),
        ("Configuration", results[3]),
        ("Data Availability", results[4]),
        ("API Server", results[5])
    ]

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for check_name, result in checks:
        icon = "[OK]" if result else "[FAIL]"
        print(f"{icon} {check_name}")

    print(f"\n{'='*70}")
    print(f"  SCORE: {passed}/{total} checks passed")
    print(f"{'='*70}\n")

    if passed == total:
        print("SUCCESS! All systems ready for development.")
        print("\nNext Steps:")
        print("   1. python main.py --step scrape")
        print("   2. python src/api_server.py")
        print("   3. Open frontend/index.html")
    else:
        print("WARNING: Some issues found. Please fix them before proceeding.")
        print("\nRecommended Actions:")
        if not results[1]:
            print("   -> pip install -r requirements.txt")
        if not results[4]:
            print("   -> python main.py --step scrape")

def main():
    """Run all diagnostic checks"""
    print("\n" + "="*70)
    print("  E-COMMERCE INTELLIGENCE - SYSTEM DIAGNOSTIC")
    print("="*70)

    results = [
        check_python_version(),
        check_dependencies(),
        check_project_structure(),
        check_config(),
        check_data_availability(),
        test_api_server()
    ]

    print_summary(results)

if __name__ == "__main__":
    main()
