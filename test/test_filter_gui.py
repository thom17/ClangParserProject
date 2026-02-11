"""
Test script for filter configuration GUI and management.
"""
import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from oms.parse_manager import ParseManager
from oms.project_scanner import ProjectScanner


def test_filter_config_management():
    """Test filter configuration management."""
    print("\n" + "="*60)
    print("Testing Filter Configuration Management")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create ParseManager
            print("\n1. Creating ParseManager")
            manager = ParseManager(tmpdir)
            print("   ✓ ParseManager created")
            
            # Check default config exists
            print("\n2. Checking default configuration")
            configs = manager.list_filter_configs()
            assert len(configs) > 0, "No default configuration found"
            print(f"   ✓ Found {len(configs)} configuration(s)")
            for config in configs:
                print(f"     - {config['name']}: {config['description']}")
            
            # Create new configuration
            print("\n3. Creating new configuration")
            config_id = manager.create_filter_config('test_config', 'Test configuration')
            assert config_id is not None, "Failed to create configuration"
            print(f"   ✓ Configuration created with ID: {config_id}")
            
            # Add patterns to config
            print("\n4. Adding patterns to configuration")
            manager.db.add_pattern_to_config(config_id, '**/test/**', 'exclude', 'folder')
            manager.db.add_pattern_to_config(config_id, '**/*.tmp', 'exclude', 'extension')
            print("   ✓ Patterns added")
            
            # Get patterns for config
            print("\n5. Retrieving patterns")
            patterns = manager.db.get_patterns_for_config(config_id)
            print(f"   ✓ Include patterns: {patterns['include']}")
            print(f"   ✓ Exclude patterns: {patterns['exclude']}")
            assert len(patterns['exclude']) == 2, "Expected 2 exclude patterns"
            
            # Switch to new config
            print("\n6. Switching to new configuration")
            manager.switch_filter_config('test_config')
            print("   ✓ Switched to test_config")
            
            # Verify active config
            print("\n7. Verifying active configuration")
            active_patterns = manager.db.get_patterns_for_active_config()
            print(f"   ✓ Active config has {len(active_patterns['exclude'])} exclude patterns")
            
            manager.close()
            print("\n✓ Filter configuration management tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ Filter configuration management test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_project_scanner():
    """Test project scanner functionality."""
    print("\n" + "="*60)
    print("Testing Project Scanner")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create test structure
            print("\n1. Creating test project structure")
            os.makedirs(os.path.join(tmpdir, 'src'))
            os.makedirs(os.path.join(tmpdir, 'include'))
            os.makedirs(os.path.join(tmpdir, 'test'))
            
            # Create test files
            with open(os.path.join(tmpdir, 'src', 'main.cpp'), 'w') as f:
                f.write('// main.cpp\n')
            with open(os.path.join(tmpdir, 'include', 'header.h'), 'w') as f:
                f.write('// header.h\n')
            with open(os.path.join(tmpdir, 'test', 'test.cpp'), 'w') as f:
                f.write('// test.cpp\n')
            print("   ✓ Test structure created")
            
            # Create scanner
            print("\n2. Scanning project")
            scanner = ProjectScanner(tmpdir)
            scanner.scan()
            print("   ✓ Project scanned")
            
            # Check folders
            print("\n3. Checking discovered folders")
            folders = scanner.get_folders()
            print(f"   ✓ Found {len(folders)} folders: {folders}")
            assert 'src' in folders, "src folder not found"
            assert 'include' in folders, "include folder not found"
            assert 'test' in folders, "test folder not found"
            
            # Check extensions
            print("\n4. Checking discovered extensions")
            extensions = scanner.get_extensions()
            print(f"   ✓ Found extensions: {extensions}")
            assert '.cpp' in extensions, ".cpp extension not found"
            assert '.h' in extensions, ".h extension not found"
            
            # Test folder search
            print("\n5. Testing folder search")
            search_results = scanner.get_folders('src')
            print(f"   ✓ Search 'src' returned: {search_results}")
            assert 'src' in search_results, "src not in search results"
            
            # Test pattern generation
            print("\n6. Testing pattern generation")
            folder_patterns = scanner.generate_folder_patterns(['test'], 'exclude')
            print(f"   ✓ Generated folder patterns: {folder_patterns}")
            assert '**/test/**' in folder_patterns, "Expected folder pattern not found"
            
            ext_patterns = scanner.generate_extension_patterns(['.tmp'], 'exclude')
            print(f"   ✓ Generated extension patterns: {ext_patterns}")
            assert '**/*.tmp' in ext_patterns, "Expected extension pattern not found"
            
            # Test preview
            print("\n7. Testing filter preview")
            result = scanner.preview_filter([], ['**/test/**'])
            print(f"   ✓ Preview: {result['total']} total, {len(result['included'])} included, {len(result['excluded'])} excluded")
            assert result['total'] == 3, "Expected 3 total files"
            
            print("\n✓ Project scanner tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ Project scanner test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_gui_integration():
    """Test GUI integration (non-interactive)."""
    print("\n" + "="*60)
    print("Testing GUI Integration")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Create test structure
            print("\n1. Creating test project")
            os.makedirs(os.path.join(tmpdir, 'src'))
            with open(os.path.join(tmpdir, 'src', 'test.cpp'), 'w') as f:
                f.write('// test\n')
            
            # Create manager
            print("\n2. Creating ParseManager")
            manager = ParseManager(tmpdir)
            print("   ✓ ParseManager created")
            
            # Check GUI method exists
            print("\n3. Checking GUI method availability")
            assert hasattr(manager, 'open_filter_config_gui'), "GUI method not found"
            print("   ✓ open_filter_config_gui method exists")
            
            # Note: We can't actually open the GUI in automated tests
            print("\n   Note: GUI display test skipped (requires interactive session)")
            print("   To test GUI manually, run:")
            print("     python -c \"from oms.parse_manager import ParseManager; ")
            print("     manager = ParseManager('.'); manager.open_filter_config_gui()\"")
            
            manager.close()
            print("\n✓ GUI integration tests passed!")
            return True
            
        except Exception as e:
            print(f"\n✗ GUI integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing Filter Configuration System")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Filter Configuration Management", test_filter_config_management()))
    results.append(("Project Scanner", test_project_scanner()))
    results.append(("GUI Integration", test_gui_integration()))
    
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
