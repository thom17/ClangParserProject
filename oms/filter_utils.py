"""
Filter utilities for file pattern matching.
Supports glob patterns and path matching for include/exclude lists.
"""
import os
import fnmatch
from typing import List, Optional
from pathlib import Path


class FileFilter:
    """Handles file filtering based on include/exclude patterns."""
    
    def __init__(self, include_patterns: Optional[List[str]] = None,
                 exclude_patterns: Optional[List[str]] = None,
                 project_root: Optional[str] = None):
        """
        Initialize file filter with patterns.
        
        Args:
            include_patterns: List of glob patterns for files to include
            exclude_patterns: List of glob patterns for files to exclude
            project_root: Root directory for relative path resolution
        """
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.project_root = project_root or os.getcwd()
    
    def should_include(self, file_path: str) -> bool:
        """
        Check if a file should be included based on patterns.
        
        Logic:
        1. If include_patterns exist, file must match at least one
        2. File must not match any exclude_pattern
        3. If no include_patterns, file is included unless excluded
        
        Args:
            file_path: Absolute or relative file path to check
            
        Returns:
            True if file should be included, False otherwise
        """
        # Convert to absolute path
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # Get relative path from project root for pattern matching
        try:
            rel_path = os.path.relpath(file_path, self.project_root)
        except ValueError:
            # On Windows, paths on different drives can't be relative
            rel_path = file_path
        
        # Normalize path separators for consistent matching
        rel_path = rel_path.replace(os.sep, '/')
        
        # Check exclude patterns first (early exit)
        for pattern in self.exclude_patterns:
            if self._match_pattern(rel_path, pattern):
                return False
        
        # If no include patterns, include everything not excluded
        if not self.include_patterns:
            return True
        
        # Check if file matches any include pattern
        for pattern in self.include_patterns:
            if self._match_pattern(rel_path, pattern):
                return True
        
        return False
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
        Match a path against a pattern.
        Supports glob patterns with ** for recursive matching.
        
        Args:
            path: Normalized path to match (with / separators)
            pattern: Glob pattern to match against
            
        Returns:
            True if path matches pattern
        """
        # Normalize pattern separators
        pattern = pattern.replace(os.sep, '/')
        
        # Handle ** for recursive directory matching
        if '**' in pattern:
            # Convert ** pattern to regex-like matching
            parts = pattern.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                # Remove leading/trailing slashes
                prefix = prefix.rstrip('/')
                suffix = suffix.lstrip('/')
                
                # Check prefix
                if prefix and not path.startswith(prefix):
                    return False
                
                # Check suffix
                if suffix:
                    # Remove prefix from path
                    remaining = path[len(prefix):].lstrip('/')
                    # Check if any part of remaining path matches suffix
                    if suffix.endswith('/'):
                        # Directory pattern
                        return any(part.startswith(suffix.rstrip('/')) 
                                 for part in remaining.split('/'))
                    else:
                        # File pattern
                        return fnmatch.fnmatch(remaining, suffix) or \
                               any(fnmatch.fnmatch(part, suffix) 
                                   for part in remaining.split('/'))
                
                return True
        
        # Simple glob matching
        return fnmatch.fnmatch(path, pattern)
    
    def filter_files(self, file_paths: List[str]) -> List[str]:
        """
        Filter a list of file paths based on include/exclude patterns.
        
        Args:
            file_paths: List of file paths to filter
            
        Returns:
            Filtered list of file paths
        """
        return [f for f in file_paths if self.should_include(f)]
    
    @classmethod
    def from_config_file(cls, config_path: str, project_root: Optional[str] = None) -> 'FileFilter':
        """
        Create FileFilter from a config file (like .gitignore format).
        
        Lines starting with '!' are include patterns.
        Other non-empty, non-comment lines are exclude patterns.
        
        Args:
            config_path: Path to config file
            project_root: Root directory for the project
            
        Returns:
            FileFilter instance
        """
        include_patterns = []
        exclude_patterns = []
        
        if not os.path.exists(config_path):
            return cls(include_patterns, exclude_patterns, project_root)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Include patterns start with !
                if line.startswith('!'):
                    include_patterns.append(line[1:].strip())
                else:
                    exclude_patterns.append(line)
        
        return cls(include_patterns, exclude_patterns, project_root)
