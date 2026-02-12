"""
Demo script for filter configuration GUI.
Shows how to use the GUI to configure filters for a project.
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from oms.parse_manager import ParseManager




def demo_filter_gui_basic(project_dir:str ):
    """Basic demonstration of filter configuration GUI."""
    print("\n" + "="*60)
    print("Demo: Filter Configuration GUI")
    print("="*60)

    print(f"\nProject directory: {project_dir}")
    print("\n1. Creating ParseManager...")
    manager = ParseManager(project_dir)
    print("   ✓ ParseManager created")
    
    print("\n2. Listing available filter configurations:")
    configs = manager.list_filter_configs()
    for config in configs:
        status = "DEFAULT" if config['is_default'] else ""
        print(f"   - {config['name']}: {config['description']} {status}")
    
    print("\n3. Current filter patterns:")
    patterns = manager.get_filter_patterns()
    print(f"   Include patterns: {len(patterns['include'])}")
    for p in patterns['include'][:3]:
        print(f"     - {p}")
    if len(patterns['include']) > 3:
        print(f"     ... and {len(patterns['include']) - 3} more")
    
    print(f"   Exclude patterns: {len(patterns['exclude'])}")
    for p in patterns['exclude'][:3]:
        print(f"     - {p}")
    if len(patterns['exclude']) > 3:
        print(f"     ... and {len(patterns['exclude']) - 3} more")
    
    print("\n4. Opening Filter Configuration GUI...")
    print("   (This will open a GUI window)")
    print("\n   GUI Features:")
    print("   - Folders Tab: Select folders to include/exclude")
    print("   - Extensions Tab: Select file extensions to include/exclude")
    print("   - Preview Tab: Preview which files will be filtered")
    print("   - Configuration Management: Create, load, and switch configurations")
    print("\n   Note: Close the GUI window when done to continue")
    
    try:
        # This will open the GUI window
        manager.open_filter_config_gui()
        print("\n   ✓ GUI closed")
        
        # Show updated patterns
        print("\n5. Filter patterns after GUI configuration:")
        patterns = manager.get_filter_patterns()
        print(f"   Include patterns: {len(patterns['include'])}")
        print(f"   Exclude patterns: {len(patterns['exclude'])}")
        
    except Exception as e:
        print(f"\n   ✗ Error opening GUI: {e}")
        print("   This is expected in non-interactive environments (CI/CD, SSH without X11, etc.)")
    
    manager.close()
    print("\n✓ Demo completed")


def demo_programmatic_config(project_dir: str):
    """Demonstrate programmatic filter configuration."""
    print("\n" + "="*60)
    print("Demo: Programmatic Filter Configuration")
    print("="*60)

    print(f"\nProject directory: {project_dir}")
    print("\n1. Creating ParseManager...")
    manager = ParseManager(project_dir)
    
    print("\n2. Creating a new filter configuration...")
    config_id = manager.create_filter_config('demo_config', 'Demo configuration for testing')
    print(f"   ✓ Configuration created with ID: {config_id}")
    
    print("\n3. Adding patterns to configuration...")
    # Add folder exclusions
    manager.db.add_pattern_to_config(config_id, '**/build/**', 'exclude', 'folder')
    manager.db.add_pattern_to_config(config_id, '**/dist/**', 'exclude', 'folder')
    manager.db.add_pattern_to_config(config_id, '**/test/**', 'exclude', 'folder')
    
    # Add extension exclusions
    manager.db.add_pattern_to_config(config_id, '**/*.o', 'exclude', 'extension')
    manager.db.add_pattern_to_config(config_id, '**/*.obj', 'exclude', 'extension')
    
    # Add include patterns
    manager.db.add_pattern_to_config(config_id, '**/*.cpp', 'include', 'extension')
    manager.db.add_pattern_to_config(config_id, '**/*.h', 'include', 'extension')
    
    print("   ✓ Patterns added")
    
    print("\n4. Switching to new configuration...")
    manager.switch_filter_config('demo_config')
    print("   ✓ Switched to demo_config")
    
    print("\n5. Retrieving patterns for active configuration...")
    patterns = manager.db.get_patterns_for_active_config()
    print(f"   Include patterns ({len(patterns['include'])}):")
    for p in patterns['include']:
        print(f"     - {p}")
    print(f"   Exclude patterns ({len(patterns['exclude'])}):")
    for p in patterns['exclude']:
        print(f"     - {p}")
    
    print("\n6. Listing all configurations:")
    configs = manager.list_filter_configs()
    for config in configs:
        active = " (ACTIVE)" if config['name'] == 'demo_config' else ""
        default = " (DEFAULT)" if config['is_default'] else ""
        print(f"   - {config['name']}{active}{default}")
    
    manager.close()
    print("\n✓ Demo completed")


def usage_guide():
    """Print usage guide."""
    print("\n" + "="*60)
    print("Filter Configuration GUI - Usage Guide")
    print("="*60)
    
    print("""
1. OPENING THE GUI:
   
   from oms.parse_manager import ParseManager
   
   manager = ParseManager('/path/to/project')
   manager.open_filter_config_gui()

2. GUI FEATURES:

   Folders Tab:
   - Browse project folder structure
   - Check/uncheck folders to include or exclude
   - Use search box to filter folders
   - Select All / Deselect All buttons
   
   Extensions Tab:
   - View all file extensions in project
   - Check/uncheck extensions to include or exclude
   - See file count for each extension
   
   Preview Tab:
   - See which files will be included/excluded
   - Shows statistics (total, included, excluded)
   - Click Preview button to update
   
   Configuration Management:
   - Create new configurations
   - Load existing configurations
   - Switch between configurations
   - Save current selections

3. MODES:

   Skip (Exclude) Mode:
   - Selected items will be EXCLUDED from parsing
   - Example: Skip test folders, Skip .o files
   
   Include Only Mode:
   - ONLY selected items will be INCLUDED
   - Everything else is excluded
   - Example: Include only .cpp and .h files

4. PROGRAMMATIC USAGE:

   # Create configuration
   manager.create_filter_config('my_config', 'My custom configuration')
   
   # Add patterns
   config_id = manager.db.get_filter_config_id('my_config')
   manager.db.add_pattern_to_config(config_id, '**/src/**', 'include', 'folder')
   
   # Switch configuration
   manager.switch_filter_config('my_config')
   
   # List configurations
   configs = manager.list_filter_configs()

5. EXAMPLES:

   Example 1: Exclude test and build directories
   - Select "test" and "build" folders
   - Set mode to "Skip (Exclude)"
   - Save configuration
   
   Example 2: Include only C++ source files
   - Select ".cpp" and ".h" extensions
   - Set mode to "Include Only"
   - Save configuration
   
   Example 3: Complex filtering
   - Exclude: test/, build/, *.o, *.tmp
   - Include: src/, include/, *.cpp, *.h
   - Create custom configuration with both

6. TIPS:

   - Configurations are saved in the database
   - Can have multiple configurations per project
   - Switch between configurations as needed
   - Use Preview to verify selections
   - Search function helps with large projects
    """)

def main():
    if len(sys.argv) > 1:   # python demo_filter_gui.py --gui
        project_dir = os.getcwd() #현제 작업 경로 가져오기
        if sys.argv[1] == '--guide':
            usage_guide()
            return
        elif sys.argv[1] == '--programmatic':
            demo_programmatic_config(project_dir)
            return
        elif sys.argv[1] == '--gui':
            demo_filter_gui_basic(project_dir)
            return
    else:
        # 폴더 선택 창 열기
        from filemanager.window_file_open import get_folder_path
        project_dir = get_folder_path('project 선택')
        if project_dir:
            demo_filter_gui_basic(project_dir)







if __name__ == "__main__":
    main()
