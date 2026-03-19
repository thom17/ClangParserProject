"""
FileInfo module for managing parsed file metadata and associated InfoBase objects.
FileInfo does not inherit from InfoBase but owns an InfoSet containing parsed code elements.
"""
from dataclasses import dataclass, fields, asdict
from typing import Optional, TYPE_CHECKING
import os
from datetime import datetime

from oms.info_set import InfoSet

if TYPE_CHECKING:
    from clangParser.datas.CUnit import CUnit


@dataclass
class FileInfoData:
    """
    Core data for FileInfo, similar to CoreInfoData pattern.
    Stores file metadata and can be converted to/from dict.
    """
    file_path: str
    file_name: str
    file_extension: str
    file_content: str  # Full source code text
    file_modified_at: float  # os.path.getmtime value
    parsed_at: str  # ISO format timestamp when parsing completed
    pair_file_path: str = ""  # h ↔ cpp pair file path
    
    @classmethod
    def from_dict(cls, di: dict) -> 'FileInfoData':
        """Create FileInfoData from dictionary."""
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in di.items() if k in field_names}
        return cls(**filtered)


class FileInfo:
    """
    Container for parsed file metadata and associated InfoBase objects.
    Does not inherit from InfoBase - instead owns an InfoSet.
    """
    
    def __init__(self, file_data: FileInfoData, info_set: Optional[InfoSet] = None):
        """Initialize FileInfo with file data and optional InfoSet."""
        self.file_data = file_data
        self.info_set = info_set if info_set is not None else InfoSet()
        self.pair_file: Optional['FileInfo'] = None
    
    # Factory methods
    
    @classmethod
    def from_cunit(cls, cunit: 'CUnit') -> 'FileInfo':
        """
        Create FileInfo from CUnit without redundant I/O.
        Uses CUnit's existing file_path, file_name, file_extension, code.
        Records modification time and finds pair file.
        """
        file_path = cunit.file_path
        
        # Get modification time
        file_modified_at = 0.0
        if os.path.exists(file_path):
            file_modified_at = os.path.getmtime(file_path)
        
        # Create timestamp
        parsed_at = datetime.now().isoformat()
        
        # Find pair file path
        pair_file_path = cls._find_pair_path(file_path)
        
        # Create FileInfoData
        file_data = FileInfoData(
            file_path=file_path,
            file_name=cunit.file_name,
            file_extension=cunit.file_extension,
            file_content=cunit.code,
            file_modified_at=file_modified_at,
            parsed_at=parsed_at,
            pair_file_path=pair_file_path
        )
        
        return cls(file_data)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'FileInfo':
        """
        Create FileInfo from file path.
        Internally parses with CUnit and delegates to from_cunit.
        """
        # Lazy import to avoid circular dependency
        from clangParser.datas.CUnit import CUnit
        
        cunit = CUnit.parse(file_path)
        return cls.from_cunit(cunit)
    
    @classmethod
    def from_dict(cls, di: dict) -> 'FileInfo':
        """Create FileInfo from dictionary (for DB loading)."""
        file_data = FileInfoData.from_dict(di)
        return cls(file_data)
    
    # Reparse methods
    
    def needs_reparse(self) -> bool:
        """
        Check if file needs reparsing by comparing stored and current modification times.
        Returns False if file doesn't exist, True if times differ.
        """
        if not os.path.exists(self.file_data.file_path):
            return False
        
        current_mtime = os.path.getmtime(self.file_data.file_path)
        return current_mtime != self.file_data.file_modified_at
    
    def refresh_modified_time(self):
        """Update file_modified_at to current file modification time."""
        if os.path.exists(self.file_data.file_path):
            self.file_data.file_modified_at = os.path.getmtime(self.file_data.file_path)
            self.file_data.parsed_at = datetime.now().isoformat()
    
    # InfoBase management methods
    
    def put_info(self, info):
        """Add an InfoBase object to the InfoSet."""
        self.info_set.put_info(info)
    
    def set_info_set(self, info_set: InfoSet):
        """Set the entire InfoSet."""
        self.info_set = info_set
    
    def get_info(self, src_name: str):
        """Get InfoBase by src_name."""
        return self.info_set.get_info(src_name)
    
    def search_info(self, keyword: str):
        """Search InfoBase objects by keyword."""
        return self.info_set.search_info(keyword)
    
    @property
    def info_count(self) -> int:
        """Total number of InfoBase objects."""
        return len(self.info_set)
    
    # Property delegation to file_data
    
    @property
    def file_path(self) -> str:
        return self.file_data.file_path
    
    @property
    def file_name(self) -> str:
        return self.file_data.file_name
    
    @property
    def file_extension(self) -> str:
        return self.file_data.file_extension
    
    @property
    def file_content(self) -> str:
        return self.file_data.file_content
    
    @property
    def parsed_at(self) -> str:
        return self.file_data.parsed_at
    
    @property
    def pair_file_path(self) -> str:
        return self.file_data.pair_file_path
    
    # Utility methods
    
    def to_dict(self) -> dict:
        """Convert FileInfo to dictionary."""
        result = asdict(self.file_data)
        result['info_count'] = self.info_count
        return result
    
    def __str__(self) -> str:
        return f"FileInfo({self.file_path}, infos={self.info_count})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FileInfo):
            return False
        return self.file_path == other.file_path
    
    def __hash__(self) -> int:
        return hash(self.file_path)
    
    @staticmethod
    def _find_pair_path(file_path: str) -> str:
        """
        Find pair file path (h ↔ cpp).
        Returns empty string if pair doesn't exist.
        """
        if not file_path:
            return ""
        
        base_path, ext = os.path.splitext(file_path)
        
        # Determine pair extension
        if ext == '.h':
            pair_ext = '.cpp'
        elif ext == '.cpp':
            pair_ext = '.h'
        else:
            return ""
        
        pair_path = base_path + pair_ext
        
        # Check if pair file exists
        if os.path.exists(pair_path):
            return pair_path
        
        return ""
