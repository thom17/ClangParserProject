"""
Demo script to test the improved filter GUI.
Creates a test project structure and opens the GUI.
"""
import os
import sys
import tempfile
import shutil

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def create_test_project():
    """Create a test project structure for GUI testing."""
    # Create in /tmp for easy cleanup
    test_dir = "/tmp/test_filter_gui_project"
    
    # Remove if exists
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Create directory structure
    os.makedirs(os.path.join(test_dir, 'src', 'main', 'core'))
    os.makedirs(os.path.join(test_dir, 'src', 'main', 'utils'))
    os.makedirs(os.path.join(test_dir, 'src', 'lib', 'external'))
    os.makedirs(os.path.join(test_dir, 'test', 'unit', 'core'))
    os.makedirs(os.path.join(test_dir, 'test', 'integration'))
    os.makedirs(os.path.join(test_dir, 'build', 'debug'))
    os.makedirs(os.path.join(test_dir, 'build', 'release'))
    os.makedirs(os.path.join(test_dir, 'docs', 'api'))
    os.makedirs(os.path.join(test_dir, 'examples'))
    
    # Create some files
    files = [
        ('src/main/core/app.cpp', '// Main application\n'),
        ('src/main/core/app.h', '// Header\n'),
        ('src/main/utils/helper.cpp', '// Helper functions\n'),
        ('src/main/utils/helper.h', '// Helper header\n'),
        ('src/lib/external/lib.cpp', '// External library\n'),
        ('test/unit/core/test_app.cpp', '// Unit tests\n'),
        ('test/integration/test_full.cpp', '// Integration tests\n'),
        ('build/debug/main.o', 'binary\n'),
        ('build/release/main.o', 'binary\n'),
        ('docs/api/readme.md', '# API Documentation\n'),
        ('examples/example1.cpp', '// Example 1\n'),
        ('examples/example2.cpp', '// Example 2\n'),
    ]
    
    for file_path, content in files:
        full_path = os.path.join(test_dir, file_path)
        with open(full_path, 'w') as f:
            f.write(content)
    
    print(f"✓ Created test project at: {test_dir}")
    print("\nProject structure:")
    print("  src/")
    print("    main/")
    print("      core/")
    print("      utils/")
    print("    lib/")
    print("      external/")
    print("  test/")
    print("    unit/")
    print("      core/")
    print("    integration/")
    print("  build/")
    print("    debug/")
    print("    release/")
    print("  docs/")
    print("    api/")
    print("  examples/")
    
    return test_dir


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("Filter Configuration GUI - Manual Testing Demo")
    print("="*60)
    print("\nThis will create a test project and open the GUI.")
    print("You can test the following features:")
    print("  1. Folders are displayed in hierarchical tree (collapsible)")
    print("  2. Search filters folders while maintaining hierarchy")
    print("  3. Selecting parent folder selects all children")
    print("\n" + "="*60)
    
    # Create test project
    test_dir = create_test_project()
    
    print("\n" + "="*60)
    print("Opening Filter Configuration GUI...")
    print("="*60)
    
    try:
        from oms.parse_manager import ParseManager
        
        # Initialize ParseManager
        manager = ParseManager(test_dir)
        
        print("\nGUI Features to Test:")
        print("  ✓ Folders Tab:")
        print("    - Folders should be in tree structure (expandable/collapsible)")
        print("    - Click folder names to expand/collapse")
        print("    - Click checkboxes to select/deselect")
        print("    - Selecting parent should select all children")
        print("\n  ✓ Search:")
        print("    - Type 'core' in search box")
        print("    - Should show src/main/core and test/unit/core")
        print("    - Parent folders (src, main, test, unit) should also appear")
        print("\n  ✓ Selection:")
        print("    - Select 'src' folder")
        print("    - All children (main, lib, core, utils, external) should be selected")
        print("    - Deselect 'src' should deselect all children")
        
        print("\nOpening GUI now...")
        print("(Close the GUI window to exit)")
        
        # Open GUI
        manager.open_filter_config_gui()
        
        print("\n✓ GUI closed")
        print(f"\nTo manually inspect, the test project is at: {test_dir}")
        print("(Will be cleaned up on next run)")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: GUI requires X11 display. If running in SSH/headless,")
        print("this is expected. Use the automated tests instead.")


if __name__ == "__main__":
    main()
