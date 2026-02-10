"""
Test script for FileInfo, LocalDB, and ParseManager implementation.
"""
import os
import sys
import tempfile
import time

# Add project root to path (relative to this file)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from oms.dataset.file_info import FileInfo, FileInfoData
from oms.local_db import LocalDB
from oms.parse_manager import ParseManager


def test_file_info():
    """Test FileInfo class functionality."""
    print("\n" + "="*60)
    print("Testing FileInfo class")
    print("="*60)
    
    # Use a simple test file (relative to project root)
    test_file = os.path.join(project_root, "test", "example.cpp")
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    try:
        # Test from_file factory method
        print(f"\n1. Creating FileInfo from file: {test_file}")
        file_info = FileInfo.from_file(test_file)
        print(f"   ✓ FileInfo created: {file_info}")
        print(f"   - File name: {file_info.file_name}")
        print(f"   - Extension: {file_info.file_extension}")
        print(f"   - Modified at: {file_info.file_data.file_modified_at}")
        print(f"   - Parsed at: {file_info.parsed_at}")
        print(f"   - Pair file: {file_info.pair_file_path}")
        
        # Test to_dict
        print("\n2. Testing to_dict()")
        file_dict = file_info.to_dict()
        print(f"   ✓ Dict keys: {list(file_dict.keys())}")
        
        # Test needs_reparse
        print("\n3. Testing needs_reparse()")
        needs_reparse = file_info.needs_reparse()
        print(f"   ✓ Needs reparse: {needs_reparse}")
        
        # Test info_count
        print(f"\n4. Testing info_count property")
        print(f"   ✓ Info count: {file_info.info_count}")
        
        print("\n✓ FileInfo tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ FileInfo test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_local_db():
    """Test LocalDB class functionality."""
    print("\n" + "="*60)
    print("Testing LocalDB class")
    print("="*60)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    test_file = os.path.join(project_root, "test", "example.cpp")
    
    try:
        # Test database creation and schema
        print(f"\n1. Creating database: {db_path}")
        db = LocalDB(db_path)
        print("   ✓ Database created with schema")
        
        # Test save
        print(f"\n2. Parsing and saving file: {test_file}")
        file_info = FileInfo.from_file(test_file)
        
        # Need to parse InfoSet using CUnit
        from clangParser.datas.CUnit import CUnit
        from oms.dataset.info_factory import parsing
        import clangParser.clang_utill as ClangUtil
        
        cunit = CUnit.parse(test_file)
        
        # Deduplicate cursors by src_name
        cursor_list = cunit.get_this_Cursor()
        seen_src_names = set()
        unique_cursors = []
        for cursor in cursor_list:
            src_name = ClangUtil.get_src_name(cursor.node)
            if src_name not in seen_src_names:
                seen_src_names.add(src_name)
                unique_cursors.append(cursor.node)
        
        # Pass deduplicated cursor list to parsing
        info_set, _ = parsing(unique_cursors, do_update=False)
        file_info.set_info_set(info_set)
        
        db.save(file_info)
        print(f"   ✓ Saved FileInfo with {file_info.info_count} infos")
        
        # Test load
        print(f"\n3. Loading file from database")
        loaded_info = db.load(test_file)
        if loaded_info:
            print(f"   ✓ Loaded FileInfo: {loaded_info}")
            print(f"   - Info count: {loaded_info.info_count}")
        else:
            print("   ✗ Failed to load FileInfo")
            return False
        
        # Test load_all
        print(f"\n4. Loading all files")
        all_files = db.load_all()
        print(f"   ✓ Loaded {len(all_files)} files")
        
        # Test get_stats
        print(f"\n5. Getting statistics")
        stats = db.get_stats()
        print(f"   ✓ Statistics:")
        for key, value in stats.items():
            print(f"      - {key}: {value}")
        
        # Test delete
        print(f"\n6. Deleting file")
        db.delete(test_file)
        print(f"   ✓ File deleted")
        
        # Verify deletion
        loaded_after_delete = db.load(test_file)
        if loaded_after_delete is None:
            print("   ✓ Deletion verified")
        else:
            print("   ✗ File still exists after deletion")
            return False
        
        db.close()
        print("\n✓ LocalDB tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ LocalDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)


def test_parse_manager():
    """Test ParseManager class functionality."""
    print("\n" + "="*60)
    print("Testing ParseManager class")
    print("="*60)
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(project_root, "test", "example.cpp")
        
        try:
            # Test ParseManager creation with project directory
            print(f"\n1. Creating ParseManager with project directory")
            manager = ParseManager(tmpdir)
            print("   ✓ ParseManager created")
            
            # Test parse_and_save
            print(f"\n2. Testing parse_and_save")
            file_info = manager.parse_and_save(test_file)
            print(f"   ✓ Parsed and saved: {file_info.info_count} infos")
            
            # Test smart_parse (should load from DB)
            print(f"\n3. Testing smart_parse (should load from DB)")
            file_info2 = manager.smart_parse(test_file)
            print(f"   ✓ Smart parse completed")
            
            # Test print_status
            print(f"\n4. Testing print_status")
            manager.print_status()
            
            # Test get_stale_files
            print(f"\n5. Testing get_stale_files")
            stale_files = manager.get_stale_files()
            print(f"   ✓ Found {len(stale_files)} stale files")
            
            manager.close()
            print("\n✓ ParseManager tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ ParseManager test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Starting Tests for SQLite-based Parsing Data Management")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("FileInfo", test_file_info()))
    results.append(("LocalDB", test_local_db()))
    results.append(("ParseManager", test_parse_manager()))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("="*60)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
