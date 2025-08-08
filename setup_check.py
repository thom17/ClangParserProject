#!/usr/bin/env python3
"""
Setup script for ClangParserProject
Checks system dependencies and provides setup guidance
"""

import sys
import subprocess
import platform
import shutil
import os

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} - OK")
    return True

def check_clang_installation():
    """Check if Clang/LLVM is installed"""
    clang_path = shutil.which("clang")
    if clang_path:
        try:
            result = subprocess.run(['clang', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ Clang found: {version_line}")
                return True
        except Exception:
            pass
    
    print("❌ Clang/LLVM not found")
    system = platform.system()
    if system == "Linux":
        print("   Install with: sudo apt-get install libclang-dev clang")
    elif system == "Darwin":
        print("   Install with: brew install llvm")
    elif system == "Windows":
        print("   Download from: https://releases.llvm.org/")
    
    return False

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'sqlalchemy',
        'clang',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    return missing_packages

def install_python_dependencies(missing_packages):
    """Install missing Python packages"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def test_basic_functionality():
    """Test if the basic parsing functionality works"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from clangParser.clangParser import parse_context
        
        test_code = """
        int main() {
            return 0;
        }
        """
        
        tu = parse_context(test_code)
        print("✅ Basic C++ parsing - OK")
        return True
        
    except Exception as e:
        print(f"❌ Basic parsing test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 ClangParserProject Setup Check")
    print("=" * 40)
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
        
    # Check Clang installation
    if not check_clang_installation():
        all_good = False
        
    # Check Python dependencies
    missing = check_python_dependencies()
    if missing:
        print(f"\n📋 Missing dependencies detected. Install them? (y/n)", end=" ")
        if input().lower().startswith('y'):
            if not install_python_dependencies(missing):
                all_good = False
        else:
            print("⚠️ You can install them later with: pip install -r requirements.txt")
            all_good = False
    
    # Test basic functionality if everything looks good
    if all_good:
        if not test_basic_functionality():
            all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 Setup complete! You're ready to use ClangParserProject")
        print("\nQuick start:")
        print("  python example_usage.py    # Run examples")
        print("  python main_script.py      # Run main script")
        print("  jupyter notebook          # Start Jupyter for analysis")
    else:
        print("⚠️ Setup incomplete. Please address the issues above.")
        print("\nFor help, check the README.md file")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())