"""
Project structure scanner for filter configuration.
Scans project directories and discovers files, folders, and extensions.
"""
import os
from typing import List, Dict, Set, Optional
from pathlib import Path
import fnmatch


class ProjectScanner:
    """Scans project structure to help configure filters."""
    
    def __init__(self, project_root: str):
        """
        Initialize scanner with project root.
        
        Args:
            project_root: Root directory to scan
        """
        self.project_root = os.path.abspath(project_root)
        self._folders = []
        self._extensions = set()
        self._files_by_folder = {}
        self._files_by_extension = {}
    
    def scan(self, max_depth: Optional[int] = None):
        """
        Scan the project directory structure.
        
        Args:
            max_depth: Maximum depth to scan (None for unlimited)
        """
        self._folders = []
        self._extensions = set()
        self._files_by_folder = {}
        self._files_by_extension = {}
        
        for root, dirs, files in os.walk(self.project_root):
            # Calculate depth
            depth = root[len(self.project_root):].count(os.sep)
            if max_depth is not None and depth >= max_depth:
                dirs[:] = []  # Don't descend further
                continue
            
            rel_root = os.path.relpath(root, self.project_root)
            if rel_root == '.':
                rel_root = ''
            
            # Store folder
            if rel_root:
                self._folders.append(rel_root)
                self._files_by_folder[rel_root] = []
            
            # Process files
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # Get extension
                _, ext = os.path.splitext(file)
                if ext:
                    self._extensions.add(ext)
                    if ext not in self._files_by_extension:
                        self._files_by_extension[ext] = []
                    self._files_by_extension[ext].append(rel_path)
                
                # Add to folder
                if rel_root:
                    self._files_by_folder[rel_root].append(rel_path)
    
    def get_folders(self, search_term: str = "") -> List[str]:
        """
        Get list of folders, optionally filtered by search term.
        
        Args:
            search_term: Optional search term to filter folders
            
        Returns:
            List of folder paths
        """
        if not search_term:
            return sorted(self._folders)
        
        search_lower = search_term.lower()
        return sorted([f for f in self._folders if search_lower in f.lower()])
    
    def get_folder_hierarchy(self, search_term: str = "") -> Dict[str, List[str]]:
        """
        Get folder hierarchy as a dictionary mapping parent to children.
        When searching, includes parent folders to maintain tree structure.
        
        Args:
            search_term: Optional search term to filter folders
            
        Returns:
            Dictionary with parent paths as keys and list of child paths as values
        """
        folders = self.get_folders(search_term)
        
        # If searching, also include all parent folders to maintain hierarchy
        if search_term:
            folders_with_parents = set(folders)
            for folder in folders:
                # Add all parent folders
                parts = folder.split(os.sep)
                for i in range(1, len(parts)):
                    parent = os.sep.join(parts[:i])
                    folders_with_parents.add(parent)
            folders = sorted(folders_with_parents)
        
        hierarchy = {'': []}  # Root level folders
        
        # Build hierarchy
        for folder in folders:
            parts = folder.split(os.sep)
            parent = os.sep.join(parts[:-1]) if len(parts) > 1 else ''
            
            if parent not in hierarchy:
                hierarchy[parent] = []
            if folder not in hierarchy[parent]:  # Avoid duplicates
                hierarchy[parent].append(folder)
        
        return hierarchy
    
    def get_all_children(self, folder: str) -> List[str]:
        """
        Get all child folders (recursively) for a given folder.
        
        Args:
            folder: Parent folder path
            
        Returns:
            List of all child folder paths
        """
        children = []
        folder_prefix = folder + os.sep if folder else ''
        
        for f in self._folders:
            if f.startswith(folder_prefix) and f != folder:
                children.append(f)
        
        return children
    
    def get_extensions(self) -> List[str]:
        """
        Get list of all file extensions found.
        
        Returns:
            Sorted list of extensions (with dot)
        """
        return sorted(self._extensions)
    
    def get_extension_stats(self) -> Dict[str, int]:
        """
        Get statistics on file extensions.
        
        Returns:
            Dictionary mapping extension to file count
        """
        return {ext: len(files) for ext, files in self._files_by_extension.items()}
    
    def get_folder_stats(self) -> Dict[str, int]:
        """
        Get statistics on folders.
        
        Returns:
            Dictionary mapping folder to file count
        """
        return {folder: len(files) for folder, files in self._files_by_folder.items()}
    
    def preview_filter(self, include_patterns: List[str], exclude_patterns: List[str]) -> Dict:
        """
        Preview what files would be included/excluded with given patterns.
        
        Args:
            include_patterns: List of include patterns
            exclude_patterns: List of exclude patterns
            
        Returns:
            Dictionary with included and excluded file lists
        """
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                all_files.append(rel_path)
        
        included = []
        excluded = []
        
        for file_path in all_files:
            # Normalize path
            norm_path = file_path.replace(os.sep, '/')
            
            # Check exclusions first
            is_excluded = False
            for pattern in exclude_patterns:
                if self._match_pattern(norm_path, pattern):
                    is_excluded = True
                    break
            
            if is_excluded:
                excluded.append(file_path)
                continue
            
            # Check inclusions
            if include_patterns:
                is_included = False
                for pattern in include_patterns:
                    if self._match_pattern(norm_path, pattern):
                        is_included = True
                        break
                if is_included:
                    included.append(file_path)
                else:
                    excluded.append(file_path)
            else:
                included.append(file_path)
        
        return {
            'included': included,
            'excluded': excluded,
            'total': len(all_files)
        }
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
        Match path against pattern with ** support.
        
        Args:
            path: File path to match
            pattern: Glob pattern
            
        Returns:
            True if path matches pattern
        """
        pattern = pattern.replace(os.sep, '/')
        
        if '**' in pattern:
            parts = pattern.split('**/')
            if len(parts) >= 2:
                prefix = parts[0].rstrip('/')
                suffix = '/'.join(parts[1:])
                
                if prefix:
                    if not (path.startswith(prefix + '/') or path == prefix):
                        return False
                    if path.startswith(prefix + '/'):
                        path = path[len(prefix)+1:]
                
                if suffix:
                    if suffix.endswith('/**'):
                        dir_pattern = suffix[:-3]
                        path_parts = path.split('/')
                        return any(part == dir_pattern or path.startswith(dir_pattern + '/') 
                                 for part in path_parts)
                    else:
                        return fnmatch.fnmatch(path, suffix) or \
                               any(fnmatch.fnmatch(path[i:], suffix) 
                                   for i in range(len(path)) if path[i] == '/')
                return True
        
        return fnmatch.fnmatch(path, pattern)
    
    def generate_folder_patterns(self, folders: List[str], filter_type: str = 'exclude') -> List[str]:
        """
        Generate filter patterns for selected folders.
        
        Args:
            folders: List of folder paths
            filter_type: 'include' or 'exclude'
            
        Returns:
            List of patterns
        """
        patterns = []
        for folder in folders:
            # Normalize path
            folder = folder.replace(os.sep, '/')
            pattern = f'**/{folder}/**'
            patterns.append(pattern)
        return patterns
    
    def generate_extension_patterns(self, extensions: List[str], filter_type: str = 'exclude') -> List[str]:
        """
        Generate filter patterns for selected extensions.
        
        Args:
            extensions: List of extensions (with or without dot)
            filter_type: 'include' or 'exclude'
            
        Returns:
            List of patterns
        """
        patterns = []
        for ext in extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            pattern = f'**/*{ext}'
            patterns.append(pattern)
        return patterns
