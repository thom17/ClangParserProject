"""
Demo script showing the new project-based LocalDB with filtering functionality.

This demonstrates:
1. Project-based initialization (no longer individual DB per file)
2. Filter configuration (include/exclude patterns)
3. Loading filters from .clangparse_ignore file
4. Managing filters programmatically
"""
import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from oms.parse_manager import ParseManager


def demo_project_based_initialization():
    """Demonstrate project-based initialization."""
    print("\n" + "="*60)
    print("Demo 1: Project-Based Initialization")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\nProject directory: {tmpdir}")
        
        # Create ParseManager with project directory
        print("\n1. Creating ParseManager with project directory")
        manager = ParseManager(tmpdir)
        
        # Check what was created
        cache_dir = os.path.join(tmpdir, '.clangparse')
        print(f"   → Cache directory: {cache_dir}")
        print(f"   → Database: .clangparse/.clangparse.db")
        
        # Show default patterns
        print("\n2. Default filter patterns:")
        patterns = manager.get_filter_patterns()
        print(f"   → Include patterns: {len(patterns['include'])}")
        print(f"   → Exclude patterns: {len(patterns['exclude'])}")
        print("\n   Default exclusions:")
        for pattern in patterns['exclude'][:5]:
            print(f"      - {pattern}")
        print(f"      ... and {len(patterns['exclude']) - 5} more")
        
        manager.close()
        print("\n✓ Project-based initialization complete")


def demo_filter_management():
    """Demonstrate filter management."""
    print("\n" + "="*60)
    print("Demo 2: Filter Management")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ParseManager(tmpdir)
        
        # Add custom include patterns
        print("\n1. Adding custom include patterns")
        manager.add_include_pattern('**/*.cpp')
        manager.add_include_pattern('**/*.h')
        print("   → Added: **/*.cpp")
        print("   → Added: **/*.h")
        
        # Add custom exclude patterns
        print("\n2. Adding custom exclude patterns")
        manager.add_exclude_pattern('**/temp/**')
        manager.add_exclude_pattern('**/backup/**')
        print("   → Added: **/temp/**")
        print("   → Added: **/backup/**")
        
        # Show current patterns
        print("\n3. Current filter configuration:")
        patterns = manager.get_filter_patterns()
        print(f"   → Include patterns: {patterns['include']}")
        print(f"   → Total exclude patterns: {len(patterns['exclude'])}")
        
        manager.close()
        print("\n✓ Filter management complete")


def demo_config_file():
    """Demonstrate loading configuration from file."""
    print("\n" + "="*60)
    print("Demo 3: Configuration File (.clangparse_ignore)")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a config file
        config_path = os.path.join(tmpdir, '.clangparse_ignore')
        print(f"\n1. Creating config file: {config_path}")
        
        with open(config_path, 'w') as f:
            f.write("# ClangParser ignore file\n")
            f.write("# Similar to .gitignore format\n")
            f.write("\n")
            f.write("# Exclude patterns (one per line)\n")
            f.write("**/build/**\n")
            f.write("**/dist/**\n")
            f.write("**/test/**\n")
            f.write("**/*.o\n")
            f.write("**/*.obj\n")
            f.write("\n")
            f.write("# Include patterns (start with !)\n")
            f.write("!**/*.cpp\n")
            f.write("!**/*.h\n")
            f.write("!**/*.hpp\n")
        
        print("   Config file created with content:")
        with open(config_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    print(f"      {line.strip()}")
        
        # Load config
        print("\n2. Loading config into ParseManager")
        manager = ParseManager(tmpdir)
        manager.load_filter_config(config_path)
        
        # Show loaded patterns
        patterns = manager.get_filter_patterns()
        print("\n3. Loaded patterns:")
        print(f"   Include patterns: {patterns['include']}")
        print(f"   Exclude patterns (showing first 5):")
        for pattern in patterns['exclude'][:5]:
            print(f"      - {pattern}")
        
        manager.close()
        print("\n✓ Config file loading complete")


def demo_filter_in_action():
    """Demonstrate filters in action."""
    print("\n" + "="*60)
    print("Demo 4: Filters in Action")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a project structure
        print(f"\n1. Creating mock project structure")
        dirs = [
            'src',
            'include',
            'test',
            'build',
            '.git',
        ]
        
        files = [
            'src/main.cpp',
            'src/utils.cpp',
            'include/header.h',
            'test/test.cpp',
            'build/output.o',
            '.git/config',
        ]
        
        for d in dirs:
            os.makedirs(os.path.join(tmpdir, d), exist_ok=True)
        
        for f in files:
            fpath = os.path.join(tmpdir, f)
            with open(fpath, 'w') as file:
                file.write(f"// {f}\n")
        
        print(f"   → Created {len(files)} files in {len(dirs)} directories")
        
        # Create manager with filters
        print("\n2. Creating ParseManager with default filters")
        manager = ParseManager(tmpdir)
        
        # Test filtering
        print("\n3. Testing which files would be parsed:")
        from oms.filter_utils import FileFilter
        
        all_files = [os.path.join(tmpdir, f) for f in files]
        
        for file_path in all_files:
            rel_path = os.path.relpath(file_path, tmpdir)
            should_include = manager.file_filter.should_include(file_path)
            status = "✓ INCLUDE" if should_include else "✗ EXCLUDE"
            print(f"   {rel_path:30s} {status}")
        
        manager.close()
        print("\n✓ Filter demonstration complete")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Project-Based LocalDB with Filtering - Demo")
    print("="*60)
    
    try:
        demo_project_based_initialization()
        demo_filter_management()
        demo_config_file()
        demo_filter_in_action()
        
        print("\n" + "="*60)
        print("All demos completed successfully!")
        print("="*60)
        
        print("\n" + "="*60)
        print("Key Improvements:")
        print("="*60)
        print("1. Project-based: One DB per project directory")
        print("2. Centralized: DB stored in .clangparse/ directory")
        print("3. Filtering: Include/exclude patterns like .gitignore")
        print("4. Configurable: Load from file or manage programmatically")
        print("5. Smart defaults: Common build directories excluded")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
