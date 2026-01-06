"""
Automated Project Cleanup Script
Removes unnecessary files and organizes documentation
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    print("=" * 60)
    print("[*] PROJECT CLEANUP - E-COMMERCE INTELLIGENCE")
    print("=" * 60)
    
    # Files to delete (definitely not needed)
    files_to_delete = [
        "daraz_page.html",           # Debug HTML (57KB)
        "inspect_daraz.py",          # Debug script
        "fix_linting.py",            # Already ran
        "QUICKSTART.md",             # Duplicate of QUICK_START.md
        "FIXES_SUMMARY.md",          # Old version (superseded)
    ]
    
    # Optional files (ask user)
    optional_delete = [
        "test_api.py",               # Can regenerate
        "test_scraper.py",           # Can regenerate
    ]
    
    deleted_count = 0
    moved_count = 0
    
    # Delete unnecessary files
    print("\n[1] Deleting unnecessary files...")
    for file in files_to_delete:
        file_path = Path(file)
        if file_path.exists():
            try:
                os.remove(file)
                print(f"   [DELETED] {file}")
                deleted_count += 1
            except Exception as e:
                print(f"   [ERROR] Could not delete {file}: {e}")
        else:
            print(f"   [SKIP] {file} (not found)")
    
    # Create docs folder
    print("\n[2] Organizing documentation...")
    docs_dir = Path("docs")
    if not docs_dir.exists():
        docs_dir.mkdir()
        print("   [CREATED] docs/ folder")
    else:
        print("   [EXISTS] docs/ folder")
    
    # Move detailed documentation to docs/
    doc_files_to_move = [
        "FIXING_95_PROBLEMS.md",
        "FRONTEND_BUGS_FIXED.md",
        "FRONTEND_GUIDE.md",
    ]
    
    for doc in doc_files_to_move:
        doc_path = Path(doc)
        if doc_path.exists():
            try:
                shutil.move(str(doc_path), str(docs_dir / doc))
                print(f"   [MOVED] {doc} -> docs/")
                moved_count += 1
            except Exception as e:
                print(f"   [ERROR] Could not move {doc}: {e}")
        else:
            print(f"   [SKIP] {doc} (not found)")
    
    # List remaining important files
    print("\n[3] Verifying essential files...")
    essential_files = [
        "main.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        "QUICK_START.md",
        "DEPLOYMENT_GUIDE.md",
    ]
    
    missing = []
    for file in essential_files:
        if Path(file).exists():
            print(f"   [OK] {file}")
        else:
            print(f"   [MISSING] {file}")
            missing.append(file)
    
    # Summary
    print("\n" + "=" * 60)
    print("[*] CLEANUP SUMMARY")
    print("=" * 60)
    print(f"  Deleted: {deleted_count} files")
    print(f"  Moved to docs/: {moved_count} files")
    if missing:
        print(f"  Missing essential files: {len(missing)}")
        for f in missing:
            print(f"    - {f}")
    print("=" * 60)
    
    # Final structure
    print("\n[*] FINAL PROJECT STRUCTURE:")
    print("""
E-commerce Intelligence/
├── src/                    # Backend code (7 files)
├── frontend/               # Frontend code (3 files)
├── data/                   # Data files
├── docs/                   # Documentation (detailed guides)
├── logs/                   # Log files
├── dashboard/              # Excel dashboard
├── notebooks/              # Jupyter notebooks
│
├── main.py                 # Main orchestrator
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose
├── .env                    # Environment variables
├── .gitignore             # Git ignore
│
├── README.md              # Main documentation
├── QUICK_START.md         # Getting started guide
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
├── 95_PROBLEMS_FIXED.md   # Linting fixes summary
├── FIXES_COMPLETED.md     # All improvements
└── PROJECT_ANALYSIS_AND_FIXES.md  # Detailed analysis
    """)
    
    print("\n[OK] Project cleanup complete!")
    print("\n[*] Next steps:")
    print("  1. Review the changes")
    print("  2. Commit to git (if using version control)")
    print("  3. Start developing!")

if __name__ == "__main__":
    print("\n[WARNING] This will delete and move files!")
    print("Files to delete:")
    print("  - daraz_page.html (57KB debug file)")
    print("  - inspect_daraz.py (debug script)")
    print("  - fix_linting.py (already ran)")
    print("  - QUICKSTART.md (duplicate)")
    print("  - FIXES_SUMMARY.md (old version)")
    print("\nFiles to move to docs/:")
    print("  - FIXING_95_PROBLEMS.md")
    print("  - FRONTEND_BUGS_FIXED.md")
    print("  - FRONTEND_GUIDE.md")
    
    response = input("\nProceed with cleanup? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        cleanup_project()
    else:
        print("\n[CANCELLED] Cleanup cancelled. No changes made.")
