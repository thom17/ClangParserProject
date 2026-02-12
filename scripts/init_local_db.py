'''
Test 코드를 가져와 Script로 작성 (프로젝트 선택 및 DB 초기화)
1. 프로젝트 선택
2. ParseManager 생성
3. .clangparse 디렉토리 및 DB 생성 확인
4. Update
'''
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

def get_dir_by_explore():
    import sys
    sys.path.append(r'D:\dev\python_pure_projects\PyUtil')
    from filemanager.window_file_open import get_folder_path
    return get_folder_path(title='프로젝트 폴더 선택')

def get_file_by_explore():
    import sys
    sys.path.append(r'D:\dev\python_pure_projects\PyUtil')
    from filemanager.window_file_open import get_file_path
    return get_file_path(title='db 선택')


def main():
    """프로젝트 설정 및 파싱"""
    print("\n" + "=" * 60)
    print("Testing ParseManager Project-Based Initialization")
    print("=" * 60)

    project_path = get_dir_by_explore()
    print(project_path)
    if project_path:
        try:
            # Create ParseManager with project directory
            print("\n1. Creating ParseManager with project directory")
            manager = ParseManager(project_path)

            # Check .clangparse directory created
            cache_dir = os.path.join(project_path, '.clangparse')
            assert os.path.exists(cache_dir), ".clangparse directory not created"
            print(f"   ✓ Cache directory created: {cache_dir}")

            # Check database created
            db_path = os.path.join(cache_dir, '.clangparse.db')
            assert os.path.exists(db_path), "Database file not created"
            print(f"   ✓ Database file created: {db_path}")

            # Check project root set correctly
            print("\n2. Checking project root")
            project_root = manager.db.get_project_root()
            assert os.path.samefile(project_root, project_path), "Project root mismatch"
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

            manager.smart_parse_project()

            manager.close()
            print("\n✓ ParseManager project-based tests passed!")
            return True

        except Exception as e:
            print(f"\n✗ ParseManager project-based test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    main()