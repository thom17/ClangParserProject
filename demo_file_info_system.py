"""
Demo script showing how to use the SQLite-based parsing data management system.

This demonstrates the main features:
1. Creating a ParseManager with a database
2. Parsing individual files with smart caching
3. Parsing entire projects with progress tracking
4. Querying database statistics
5. Finding files that need reparsing
"""
import os
import sys
import tempfile

# Add project root to path (relative to this file)
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from oms.parse_manager import ParseManager


def demo_single_file():
    """Demonstrate parsing a single file with smart caching."""
    print("\n" + "="*60)
    print("Demo 1: Single File Parsing with Smart Caching")
    print("="*60)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    test_file = os.path.join(project_root, "test", "example.cpp")
    
    try:
        with ParseManager(db_path) as manager:
            # First parse - will actually parse the file
            print("\n1. First parse (will actually parse the file):")
            file_info1 = manager.smart_parse(test_file)
            print(f"   Result: {file_info1.info_count} code elements found")
            
            # Second parse - will load from database (no actual parsing)
            print("\n2. Second parse (will load from cache):")
            file_info2 = manager.smart_parse(test_file)
            print(f"   Result: {file_info2.info_count} code elements loaded from DB")
            
            # Show statistics
            print("\n3. Database statistics:")
            manager.print_status()
            
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)


def demo_project_parsing():
    """Demonstrate parsing an entire project directory."""
    print("\n" + "="*60)
    print("Demo 2: Project Directory Parsing")
    print("="*60)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Use the test directory as a mini project
    project_dir = os.path.join(project_root, "test")
    
    try:
        with ParseManager(db_path) as manager:
            print(f"\nParsing project: {project_dir}")
            
            # Parse all files in the project
            # This will show progress and skip unchanged files on subsequent runs
            results = manager.smart_parse_project(project_dir, add_h=True)
            
            print(f"\n✓ Successfully processed {len(results)} files")
            
            # Show what was parsed
            print("\nParsed files:")
            for file_path, file_info in results:
                print(f"  - {file_path}: {file_info.info_count} code elements")
            
            # Show final statistics
            manager.print_status()
            
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)


def demo_database_queries():
    """Demonstrate querying the database."""
    print("\n" + "="*60)
    print("Demo 3: Database Queries")
    print("="*60)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    test_file = os.path.join(project_root, "test", "example.cpp")
    
    try:
        with ParseManager(db_path) as manager:
            # Parse a file first
            print(f"\nParsing {test_file}...")
            file_info = manager.parse_and_save(test_file)
            
            # Search for code elements
            print("\n1. Searching for elements containing 'add':")
            results = manager.db.search_info('add')
            for result in results:
                print(f"   - {result['info_type']}: {result['name']} in {result['file_path']}")
            
            # Get statistics
            print("\n2. Database statistics:")
            stats = manager.db.get_stats()
            for key, value in stats.items():
                print(f"   - {key}: {value}")
            
            # Check for stale files
            print("\n3. Files needing reparse:")
            stale_files = manager.get_stale_files()
            if stale_files:
                for f in stale_files:
                    print(f"   - {f}")
            else:
                print("   None - all files are up-to-date")
            
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("SQLite-based Parsing Data Management System - Demo")
    print("="*60)
    
    # Run demos
    try:
        demo_single_file()
        demo_database_queries()
        # Note: Skipping project parsing demo as it might take longer
        # demo_project_parsing()
        
        print("\n" + "="*60)
        print("Demo completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
