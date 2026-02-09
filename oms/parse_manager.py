"""
ParseManager module for managing the complete parsing workflow.
Integrates CUnit parsing, InfoSet creation, and LocalDB storage.
"""
from typing import List, Tuple, Optional
from oms.local_db import LocalDB
from oms.dataset.file_info import FileInfo
from oms.info_set import InfoSet
from clangParser.datas.CUnit import CUnit
from oms.dataset.info_factory import parsing, get_target_cursor


class ParseManager:
    """Manager class for parsing C++ files and storing results in database."""
    
    def __init__(self, db_path: str):
        """Initialize with database path."""
        self.db = LocalDB(db_path)
    
    def parse_and_save(self, file_path: str) -> FileInfo:
        """
        Complete parsing workflow:
        1. Parse with CUnit
        2. Create FileInfo from CUnit
        3. Parse InfoSet from CUnit cursors
        4. Connect InfoSet to FileInfo
        5. Refresh modification time
        6. Save to database
        """
        # Step 1: Parse with CUnit
        print(f"Parsing {file_path}...")
        cunit = CUnit.parse(file_path)
        
        # Step 2: Create FileInfo from CUnit
        file_info = FileInfo.from_cunit(cunit)
        
        # Step 3: Parse InfoSet from CUnit
        info_set = self._parse_info_set(cunit)
        
        # Step 4: Connect InfoSet to FileInfo
        file_info.set_info_set(info_set)
        
        # Step 5: Refresh modification time
        file_info.refresh_modified_time()
        
        # Step 6: Save to database
        print(f"Saving to database... ({file_info.info_count} infos)")
        self.db.save(file_info)
        
        return file_info
    
    def smart_parse(self, file_path: str) -> FileInfo:
        """
        Conditionally parse based on modification time.
        If file hasn't changed, load from DB. Otherwise, re-parse.
        """
        # Try to load from database
        file_info = self.db.load(file_path)
        
        if file_info is None:
            # File not in database, parse it
            print(f"New file: {file_path}")
            return self.parse_and_save(file_path)
        
        # Check if reparse is needed
        if file_info.needs_reparse():
            print(f"Modified file: {file_path}")
            return self.parse_and_save(file_path)
        else:
            print(f"Up-to-date (from DB): {file_path}")
            return file_info
    
    def smart_parse_project(self, project_dir: str, add_h: bool = True) -> List[Tuple[str, FileInfo]]:
        """
        Parse all C++ files in a project directory.
        Shows progress and returns list of (file_path, FileInfo) tuples.
        """
        # Import here to avoid circular dependency
        from clangParser.clangParser import find_cpp_files
        
        # Find all C++ files
        print(f"Scanning directory: {project_dir}")
        file_paths = list(find_cpp_files(project_dir, add_h=add_h))
        total_files = len(file_paths)
        print(f"Found {total_files} files\n")
        
        results = []
        parsed_count = 0
        skipped_count = 0
        
        for idx, file_path in enumerate(file_paths, 1):
            print(f"\n[{idx}/{total_files}] Processing: {file_path}")
            
            try:
                # Try to load from database first
                file_info = self.db.load(file_path)
                
                if file_info is None:
                    # New file - parse it
                    print("  → Status: NEW - parsing...")
                    file_info = self.parse_and_save(file_path)
                    parsed_count += 1
                elif file_info.needs_reparse():
                    # Modified file - reparse
                    print("  → Status: MODIFIED - reparsing...")
                    file_info = self.parse_and_save(file_path)
                    parsed_count += 1
                else:
                    # Up-to-date - skip
                    print("  → Status: UP-TO-DATE - skipping")
                    skipped_count += 1
                
                results.append((file_path, file_info))
                print(f"  → Result: {file_info.info_count} infos")
                
            except Exception as e:
                print(f"  → ERROR: {e}")
                continue
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Project parsing complete!")
        print(f"Total files: {total_files}")
        print(f"Parsed: {parsed_count}")
        print(f"Skipped (up-to-date): {skipped_count}")
        print(f"Errors: {total_files - parsed_count - skipped_count}")
        print(f"{'='*60}\n")
        
        return results
    
    def _parse_info_set(self, cunit: CUnit) -> InfoSet:
        """
        Parse InfoSet from CUnit using existing info_factory logic.
        Reuses the CUnit's cursor list without redundant parsing.
        """
        # Get cursor list from CUnit
        cursor_list = cunit.get_this_Cursor()
        
        # Convert to clang cursors for info_factory
        clang_cursors = [cursor.node for cursor in cursor_list]
        
        # Use existing parsing logic from info_factory
        # Note: do_update=True to populate call relationships
        info_set, clang_src_map = parsing(clang_cursors, do_update=True)
        
        return info_set
    
    def get_stale_files(self) -> List[str]:
        """Get list of file paths that need reparsing."""
        stale_file_infos = self.db.get_stale_files()
        return [f.file_path for f in stale_file_infos]
    
    def print_status(self):
        """Print database status and statistics."""
        stats = self.db.get_stats()
        
        print("\n" + "="*60)
        print("Database Status")
        print("="*60)
        print(f"Total files:     {stats['file_count']}")
        print(f"  - Classes:     {stats['class_count']}")
        print(f"  - Functions:   {stats['function_count']}")
        print(f"  - Variables:   {stats['var_count']}")
        print(f"Reparse needed:  {stats['reparse_needed']}")
        print("="*60 + "\n")
    
    def close(self):
        """Close database connection."""
        self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
