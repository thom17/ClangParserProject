"""
Test script for GUI improvements.
"""
import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from oms.project_scanner import ProjectScanner


def test_folder_hierarchy():
    """Test folder hierarchy functionality."""
    print("\n" + "="*60)
    print("Testing Folder Hierarchy")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test structure
        os.makedirs(os.path.join(tmpdir, 'src', 'main'))
        os.makedirs(os.path.join(tmpdir, 'src', 'utils'))
        os.makedirs(os.path.join(tmpdir, 'test', 'unit'))
        os.makedirs(os.path.join(tmpdir, 'test', 'integration'))
        os.makedirs(os.path.join(tmpdir, 'docs'))
        
        # Create some files
        with open(os.path.join(tmpdir, 'src', 'main', 'app.cpp'), 'w') as f:
            f.write('// app.cpp\n')
        with open(os.path.join(tmpdir, 'src', 'utils', 'helper.cpp'), 'w') as f:
            f.write('// helper.cpp\n')
        with open(os.path.join(tmpdir, 'test', 'unit', 'test.cpp'), 'w') as f:
            f.write('// test.cpp\n')
        
        # Create scanner
        scanner = ProjectScanner(tmpdir)
        scanner.scan()
        
        # Test hierarchy
        print("\n1. Testing get_folder_hierarchy()")
        hierarchy = scanner.get_folder_hierarchy()
        print(f"   Root level folders: {hierarchy.get('', [])}")
        print(f"   'src' children: {hierarchy.get('src', [])}")
        print(f"   'test' children: {hierarchy.get('test', [])}")
        
        # Test get_all_children
        print("\n2. Testing get_all_children()")
        src_children = scanner.get_all_children('src')
        print(f"   'src' all children: {src_children}")
        test_children = scanner.get_all_children('test')
        print(f"   'test' all children: {test_children}")
        
        # Test search with hierarchy
        print("\n3. Testing search with hierarchy")
        hierarchy_filtered = scanner.get_folder_hierarchy('main')
        print(f"   Search 'main' hierarchy: {hierarchy_filtered}")
        
        print("\n✓ Folder hierarchy tests completed!")
        return True


def test_folder_selection_logic():
    """Test folder selection logic."""
    print("\n" + "="*60)
    print("Testing Folder Selection Logic")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test structure
        os.makedirs(os.path.join(tmpdir, 'parent', 'child1'))
        os.makedirs(os.path.join(tmpdir, 'parent', 'child2'))
        os.makedirs(os.path.join(tmpdir, 'parent', 'child1', 'grandchild'))
        
        scanner = ProjectScanner(tmpdir)
        scanner.scan()
        
        # Simulate selecting parent
        selected = set()
        parent = 'parent'
        
        print("\n1. Selecting parent folder")
        selected.add(parent)
        children = scanner.get_all_children(parent)
        print(f"   Parent: {parent}")
        print(f"   Children: {children}")
        
        # Add all children
        for child in children:
            selected.add(child)
        
        print(f"   Selected folders: {selected}")
        assert parent in selected
        assert os.path.join('parent', 'child1') in selected
        assert os.path.join('parent', 'child2') in selected
        assert os.path.join('parent', 'child1', 'grandchild') in selected
        
        print("\n2. Deselecting parent folder")
        selected.discard(parent)
        for child in children:
            selected.discard(child)
        
        print(f"   Selected folders after deselection: {selected}")
        assert len(selected) == 0
        
        print("\n✓ Folder selection logic tests passed!")
        return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing GUI Improvements")
    print("="*60)
    
    try:
        results = []
        results.append(("Folder Hierarchy", test_folder_hierarchy()))
        results.append(("Selection Logic", test_folder_selection_logic()))
        
        # Print summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        
        for test_name, passed in results:
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test_name:30s}: {status}")
        
        all_passed = all(result[1] for result in results)
        print("="*60)
        
        if all_passed:
            print("\n✓ All tests passed!")
            return 0
        else:
            print("\n✗ Some tests failed")
            return 1
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
