"""
Test suite for project-based LocalDB with filtering functionality.
Tests new requirements for project-based configuration and include/exclude patterns.
"""
import os
import sys
import tempfile
import shutil

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from oms.local_db import LocalDB
from oms.filter_utils import FileFilter
from oms.parse_manager import ParseManager


def test_localdb_project_config():
    """Test LocalDB project configuration."""
    print("\n" + "="*60)
    print("Testing LocalDB Project Configuration")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        project_root = tmpdir
        
        try:
            # Create LocalDB with project root
            print("\n1. Creating LocalDB with project root")
            db = LocalDB(db_path, project_root=project_root)
            
            # Check project_config table exists
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='project_config'
            """)
            assert cursor.fetchone() is not None, "project_config table not found"
            print("   ✓ project_config table created")
            
            # Check filter_patterns table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='filter_patterns'
            """)
            assert cursor.fetchone() is not None, "filter_patterns table not found"
            print("   ✓ filter_patterns table created")
            
            # Test config get/set
            print("\n2. Testing config get/set")
            db.set_config('test_key', 'test_value')
            value = db.get_config('test_key')
            assert value == 'test_value', f"Expected 'test_value', got '{value}'"
            print("   ✓ Config get/set works")
            
            # Test project root
            print("\n3. Testing project root")
            stored_root = db.get_project_root()
            assert stored_root == project_root, f"Project root mismatch"
            print(f"   ✓ Project root: {stored_root}")
            
            db.close()
            print("\n✓ LocalDB project config tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ LocalDB project config test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_filter_patterns():
    """Test filter pattern management."""
    print("\n" + "="*60)
    print("Testing Filter Pattern Management")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        
        try:
            db = LocalDB(db_path, project_root=tmpdir)
            
            # Check default exclude patterns
            print("\n1. Checking default exclude patterns")
            excludes = db.get_exclude_patterns()
            assert len(excludes) > 0, "No default exclude patterns"
            assert any('.git' in p for p in excludes), ".git pattern not in defaults"
            print(f"   ✓ Found {len(excludes)} default exclude patterns")
            
            # Add custom include pattern
            print("\n2. Adding custom include pattern")
            db.add_include_pattern('**/*.cpp')
            includes = db.get_include_patterns()
            assert '**/*.cpp' in includes, "Include pattern not added"
            print("   ✓ Custom include pattern added")
            
            # Add custom exclude pattern
            print("\n3. Adding custom exclude pattern")
            db.add_exclude_pattern('**/test/**')
            excludes = db.get_exclude_patterns()
            assert '**/test/**' in excludes, "Exclude pattern not added"
            print("   ✓ Custom exclude pattern added")
            
            # Remove pattern
            print("\n4. Removing pattern")
            db.remove_pattern('**/*.cpp')
            includes = db.get_include_patterns()
            assert '**/*.cpp' not in includes, "Pattern not removed"
            print("   ✓ Pattern removed successfully")
            
            # Get all patterns
            print("\n5. Getting all patterns")
            all_patterns = db.get_all_patterns()
            assert 'include' in all_patterns, "Include key missing"
            assert 'exclude' in all_patterns, "Exclude key missing"
            print(f"   ✓ Include: {len(all_patterns['include'])} patterns")
            print(f"   ✓ Exclude: {len(all_patterns['exclude'])} patterns")
            
            # Clear patterns
            print("\n6. Clearing exclude patterns")
            db.clear_patterns('exclude')
            excludes = db.get_exclude_patterns()
            assert len(excludes) == 0, "Patterns not cleared"
            print("   ✓ Exclude patterns cleared")
            
            db.close()
            print("\n✓ Filter pattern tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ Filter pattern test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_file_filter():
    """Test FileFilter utility."""
    print("\n" + "="*60)
    print("Testing FileFilter Utility")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Test basic exclude
            print("\n1. Testing basic exclude pattern")
            filter_obj = FileFilter(
                exclude_patterns=['**/.git/**', '**/build/**'],
                project_root=tmpdir
            )
            
            test_files = [
                os.path.join(tmpdir, 'src/main.cpp'),
                os.path.join(tmpdir, '.git/config'),
                os.path.join(tmpdir, 'build/output.o'),
                os.path.join(tmpdir, 'include/header.h'),
            ]
            
            filtered = filter_obj.filter_files(test_files)
            assert len(filtered) == 2, f"Expected 2 files, got {len(filtered)}"
            assert any('main.cpp' in f for f in filtered), "main.cpp was filtered out"
            assert not any('.git' in f for f in filtered), ".git file not filtered"
            print(f"   ✓ Filtered {len(test_files) - len(filtered)} files")
            
            # Test include pattern
            print("\n2. Testing include pattern")
            filter_obj = FileFilter(
                include_patterns=['**/*.cpp'],
                exclude_patterns=[],
                project_root=tmpdir
            )
            
            test_files = [
                os.path.join(tmpdir, 'src/main.cpp'),
                os.path.join(tmpdir, 'src/utils.h'),
                os.path.join(tmpdir, 'test/test.cpp'),
            ]
            
            filtered = filter_obj.filter_files(test_files)
            assert len(filtered) == 2, f"Expected 2 .cpp files, got {len(filtered)}"
            assert all('.cpp' in f for f in filtered), "Non-.cpp file included"
            print(f"   ✓ Included only {len(filtered)} .cpp files")
            
            # Test combined include/exclude
            print("\n3. Testing combined include/exclude")
            filter_obj = FileFilter(
                include_patterns=['**/*.cpp', '**/*.h'],
                exclude_patterns=['**/test/**'],
                project_root=tmpdir
            )
            
            test_files = [
                os.path.join(tmpdir, 'src/main.cpp'),
                os.path.join(tmpdir, 'src/utils.h'),
                os.path.join(tmpdir, 'test/test.cpp'),
                os.path.join(tmpdir, 'README.md'),
            ]
            
            filtered = filter_obj.filter_files(test_files)
            assert len(filtered) == 2, f"Expected 2 files, got {len(filtered)}"
            assert not any('test.cpp' in f for f in filtered), "test file not excluded"
            assert not any('README' in f for f in filtered), "README not excluded"
            print(f"   ✓ Filtered to {len(filtered)} files with combined rules")
            
            print("\n✓ FileFilter tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ FileFilter test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_config_file_loading():
    """Test loading configuration from .clangparse_ignore file."""
    print("\n" + "="*60)
    print("Testing Config File Loading")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create a config file
            config_path = os.path.join(tmpdir, '.clangparse_ignore')
            with open(config_path, 'w') as f:
                f.write("# Exclude patterns\n")
                f.write("**/build/**\n")
                f.write("**/.git/**\n")
                f.write("**/test/**\n")
                f.write("\n")
                f.write("# Include patterns (start with !)\n")
                f.write("!**/*.cpp\n")
                f.write("!**/*.h\n")
            
            print("\n1. Loading config from file")
            filter_obj = FileFilter.from_config_file(config_path, tmpdir)
            
            assert len(filter_obj.include_patterns) == 2, "Include patterns not loaded"
            assert len(filter_obj.exclude_patterns) == 3, "Exclude patterns not loaded"
            print(f"   ✓ Loaded {len(filter_obj.include_patterns)} include patterns")
            print(f"   ✓ Loaded {len(filter_obj.exclude_patterns)} exclude patterns")
            
            # Test with ParseManager
            print("\n2. Testing with ParseManager")
            manager = ParseManager(tmpdir)
            manager.load_filter_config(config_path)
            
            patterns = manager.get_filter_patterns()
            assert len(patterns['include']) == 2, "Include patterns not in DB"
            assert len(patterns['exclude']) == 3, "Exclude patterns not in DB"
            print("   ✓ Patterns loaded into ParseManager")
            
            manager.close()
            print("\n✓ Config file loading tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ Config file loading test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_parse_manager_project_based():
    """Test ParseManager with project-based initialization."""
    print("\n" + "="*60)
    print("Testing ParseManager Project-Based Initialization")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create ParseManager with project directory
            print("\n1. Creating ParseManager with project directory")
            manager = ParseManager(tmpdir)
            
            # Check .clangparse directory created
            cache_dir = os.path.join(tmpdir, '.clangparse')
            assert os.path.exists(cache_dir), ".clangparse directory not created"
            print(f"   ✓ Cache directory created: {cache_dir}")
            
            # Check database created
            db_path = os.path.join(cache_dir, '.clangparse.db')
            assert os.path.exists(db_path), "Database file not created"
            print(f"   ✓ Database file created: {db_path}")
            
            # Check project root set correctly
            print("\n2. Checking project root")
            project_root = manager.db.get_project_root()
            assert os.path.samefile(project_root, tmpdir), "Project root mismatch"
            print(f"   ✓ Project root: {project_root}")
            
            # Test filter patterns
            print("\n3. Testing filter patterns")
            patterns = manager.get_filter_patterns()
            assert 'include' in patterns, "Include patterns missing"
            assert 'exclude' in patterns, "Exclude patterns missing"
            print(f"   ✓ Filter patterns available")
            
            # Add custom pattern
            print("\n4. Adding custom pattern")
            manager.add_exclude_pattern('**/temp/**')
            patterns = manager.get_filter_patterns()
            assert '**/temp/**' in patterns['exclude'], "Pattern not added"
            print("   ✓ Custom pattern added")
            
            manager.close()
            print("\n✓ ParseManager project-based tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ ParseManager project-based test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing Project-Based LocalDB with Filtering")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("LocalDB Project Config", test_localdb_project_config()))
    results.append(("Filter Patterns", test_filter_patterns()))
    results.append(("FileFilter Utility", test_file_filter()))
    results.append(("Config File Loading", test_config_file_loading()))
    results.append(("ParseManager Project-Based", test_parse_manager_project_based()))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:40s}: {status}")
    
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
