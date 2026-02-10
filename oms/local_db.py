"""
LocalDB module for SQLite-based storage and retrieval of FileInfo and InfoBase objects.
Supports project-based configuration with include/exclude filters.
"""
import sqlite3
import os
from typing import Optional, List, Dict
from oms.dataset.file_info import FileInfo, FileInfoData
from oms.info_set import InfoSet
from oms.dataset.class_info import ClassInfo
from oms.dataset.function_info import FunctionInfo
from oms.dataset.var_info import VarInfo
from oms.dataset.info_base import CoreInfoData


class LocalDB:
    """SQLite database manager for parsed file information with project configuration."""
    
    def __init__(self, db_path: str, project_root: Optional[str] = None):
        """
        Initialize database connection and schema.
        
        Args:
            db_path: Path to the SQLite database file
            project_root: Root directory of the project (optional, defaults to db directory)
        """
        self.db_path = db_path
        self.project_root = project_root or os.path.dirname(os.path.abspath(db_path))
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        self._ensure_project_config()
    
    def _init_schema(self):
        """Create tables and indexes if they don't exist."""
        cursor = self.conn.cursor()
        
        # Create project_config table for project-wide settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create filter_patterns table for include/exclude patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filter_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                filter_type TEXT NOT NULL CHECK(filter_type IN ('include', 'exclude')),
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create file_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL UNIQUE,
                file_name TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                file_content TEXT,
                file_modified_at REAL NOT NULL,
                parsed_at TEXT NOT NULL,
                pair_file_path TEXT DEFAULT '',
                info_count INTEGER DEFAULT 0
            )
        """)
        
        # Create info_base table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS info_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                info_type TEXT NOT NULL CHECK(info_type IN ('ClassInfo', 'FunctionInfo', 'VarInfo')),
                name TEXT NOT NULL,
                src_name TEXT NOT NULL,
                comment TEXT DEFAULT '',
                is_static INTEGER DEFAULT 0,
                is_virtual INTEGER DEFAULT 0,
                modifier TEXT DEFAULT '',
                file_path TEXT NOT NULL,
                code TEXT DEFAULT '',
                type_str TEXT DEFAULT '',
                owner_src_name TEXT DEFAULT '',
                FOREIGN KEY (file_id) REFERENCES file_info(id) ON DELETE CASCADE,
                UNIQUE(file_id, src_name)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_info_base_file_id 
            ON info_base(file_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_info_base_src_name 
            ON info_base(src_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_info_base_info_type 
            ON info_base(info_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filter_patterns_type 
            ON filter_patterns(filter_type)
        """)
        
        self.conn.commit()
    
    def _ensure_project_config(self):
        """Ensure project configuration exists with defaults."""
        from datetime import datetime
        
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # Set project root if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO project_config (key, value, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, ('project_root', self.project_root, now, now))
        
        # Add default exclude patterns if none exist
        cursor.execute("SELECT COUNT(*) FROM filter_patterns")
        if cursor.fetchone()[0] == 0:
            default_excludes = [
                '**/.git/**',
                '**/.svn/**',
                '**/build/**',
                '**/dist/**',
                '**/node_modules/**',
                '**/__pycache__/**',
                '**/*.pyc',
                '**/CMakeFiles/**',
                '**/out/**',
                '**/.vscode/**',
                '**/.idea/**',
            ]
            for pattern in default_excludes:
                cursor.execute("""
                    INSERT INTO filter_patterns (pattern, filter_type, is_active, created_at)
                    VALUES (?, 'exclude', 1, ?)
                """, (pattern, now))
        
        self.conn.commit()
    
    def add_include_pattern(self, pattern: str):
        """Add an include pattern for file filtering."""
        from datetime import datetime
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO filter_patterns (pattern, filter_type, is_active, created_at)
            VALUES (?, 'include', 1, ?)
        """, (pattern, datetime.now().isoformat()))
        self.conn.commit()
    
    def add_exclude_pattern(self, pattern: str):
        """Add an exclude pattern for file filtering."""
        from datetime import datetime
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO filter_patterns (pattern, filter_type, is_active, created_at)
            VALUES (?, 'exclude', 1, ?)
        """, (pattern, datetime.now().isoformat()))
        self.conn.commit()
    
    def remove_pattern(self, pattern: str):
        """Remove a filter pattern."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM filter_patterns WHERE pattern = ?", (pattern,))
        self.conn.commit()
    
    def get_include_patterns(self) -> List[str]:
        """Get all active include patterns."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pattern FROM filter_patterns 
            WHERE filter_type = 'include' AND is_active = 1
        """)
        return [row[0] for row in cursor.fetchall()]
    
    def get_exclude_patterns(self) -> List[str]:
        """Get all active exclude patterns."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pattern FROM filter_patterns 
            WHERE filter_type = 'exclude' AND is_active = 1
        """)
        return [row[0] for row in cursor.fetchall()]
    
    def get_all_patterns(self) -> Dict[str, List[str]]:
        """Get all filter patterns grouped by type."""
        return {
            'include': self.get_include_patterns(),
            'exclude': self.get_exclude_patterns()
        }
    
    def clear_patterns(self, filter_type: Optional[str] = None):
        """Clear filter patterns. If filter_type is None, clears all patterns."""
        cursor = self.conn.cursor()
        if filter_type:
            cursor.execute("DELETE FROM filter_patterns WHERE filter_type = ?", (filter_type,))
        else:
            cursor.execute("DELETE FROM filter_patterns")
        self.conn.commit()
    
    def set_config(self, key: str, value: str):
        """Set a configuration value."""
        from datetime import datetime
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO project_config (key, value, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (key, value, now, now))
        self.conn.commit()
    
    def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM project_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default
    
    def get_project_root(self) -> str:
        """Get the project root directory."""
        return self.get_config('project_root', self.project_root)
    
    def save(self, file_info: FileInfo):
        """
        Save FileInfo and all associated InfoBase objects to database.
        Uses UPSERT for file_info, deletes existing info_base entries, then inserts new ones.
        """
        cursor = self.conn.cursor()
        
        try:
            # UPSERT file_info
            cursor.execute("""
                INSERT INTO file_info (
                    file_path, file_name, file_extension, file_content,
                    file_modified_at, parsed_at, pair_file_path, info_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    file_name = excluded.file_name,
                    file_extension = excluded.file_extension,
                    file_content = excluded.file_content,
                    file_modified_at = excluded.file_modified_at,
                    parsed_at = excluded.parsed_at,
                    pair_file_path = excluded.pair_file_path,
                    info_count = excluded.info_count
            """, (
                file_info.file_path,
                file_info.file_name,
                file_info.file_extension,
                file_info.file_content,
                file_info.file_data.file_modified_at,
                file_info.parsed_at,
                file_info.pair_file_path,
                file_info.info_count
            ))
            
            # Get file_id
            cursor.execute("SELECT id FROM file_info WHERE file_path = ?", (file_info.file_path,))
            file_id = cursor.fetchone()[0]
            
            # Delete existing info_base entries for this file
            cursor.execute("DELETE FROM info_base WHERE file_id = ?", (file_id,))
            
            # Insert ClassInfo objects
            for src_name, class_info in file_info.info_set.classInfos.items():
                owner_src_name = class_info.owner.src_name if class_info.owner != class_info else ""
                cursor.execute("""
                    INSERT INTO info_base (
                        file_id, info_type, name, src_name, comment,
                        is_static, is_virtual, modifier, file_path, code, type_str, owner_src_name
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id, 'ClassInfo', class_info.name, class_info.src_name,
                    class_info.comment, int(class_info.is_static), int(class_info.is_virtual),
                    class_info.modifier, class_info.file_path, class_info.code,
                    class_info.type_str, owner_src_name
                ))
            
            # Insert FunctionInfo objects
            for src_name, func_info in file_info.info_set.functionInfos.items():
                owner_src_name = func_info.owner.src_name if func_info.owner != func_info else ""
                cursor.execute("""
                    INSERT INTO info_base (
                        file_id, info_type, name, src_name, comment,
                        is_static, is_virtual, modifier, file_path, code, type_str, owner_src_name
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id, 'FunctionInfo', func_info.name, func_info.src_name,
                    func_info.comment, int(func_info.is_static), int(func_info.is_virtual),
                    func_info.modifier, func_info.file_path, func_info.code,
                    func_info.type_str, owner_src_name
                ))
            
            # Insert VarInfo objects
            for src_name, var_info in file_info.info_set.varInfos.items():
                owner_src_name = var_info.owner.src_name if var_info.owner != var_info else ""
                cursor.execute("""
                    INSERT INTO info_base (
                        file_id, info_type, name, src_name, comment,
                        is_static, is_virtual, modifier, file_path, code, type_str, owner_src_name
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id, 'VarInfo', var_info.name, var_info.src_name,
                    var_info.comment, int(var_info.is_static), int(var_info.is_virtual),
                    var_info.modifier, var_info.file_path, var_info.code,
                    var_info.type_str, owner_src_name
                ))
            
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def load(self, file_path: str) -> Optional[FileInfo]:
        """
        Load FileInfo from database and restore all InfoBase objects with owner relationships.
        Returns None if file not found.
        """
        cursor = self.conn.cursor()
        
        # Load file_info
        cursor.execute("""
            SELECT file_path, file_name, file_extension, file_content,
                   file_modified_at, parsed_at, pair_file_path
            FROM file_info
            WHERE file_path = ?
        """, (file_path,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Create FileInfoData
        file_data = FileInfoData(
            file_path=row[0],
            file_name=row[1],
            file_extension=row[2],
            file_content=row[3],
            file_modified_at=row[4],
            parsed_at=row[5],
            pair_file_path=row[6]
        )
        
        file_info = FileInfo(file_data)
        
        # Get file_id
        cursor.execute("SELECT id FROM file_info WHERE file_path = ?", (file_path,))
        file_id = cursor.fetchone()[0]
        
        # Load info_base entries
        cursor.execute("""
            SELECT info_type, name, src_name, comment, is_static, is_virtual,
                   modifier, file_path, code, type_str, owner_src_name
            FROM info_base
            WHERE file_id = ?
        """, (file_id,))
        
        rows = cursor.fetchall()
        
        # First pass: create all InfoBase objects without owner relationships
        info_map = {}  # src_name -> InfoBase
        
        for row in rows:
            info_type, name, src_name, comment, is_static, is_virtual, \
                modifier, info_file_path, code, type_str, owner_src_name = row
            
            core_data = CoreInfoData(
                name=name,
                src_name=src_name,
                comment=comment,
                is_static=bool(is_static),
                is_virtual=bool(is_virtual),
                modifier=modifier,
                file_path=info_file_path,
                code=code,
                type_str=type_str
            )
            
            # Create appropriate InfoBase type
            if info_type == 'ClassInfo':
                info = ClassInfo(core_data, owner=None)
            elif info_type == 'FunctionInfo':
                info = FunctionInfo(core_data, owner=None)
            elif info_type == 'VarInfo':
                info = VarInfo(core_data, owner=None)
            else:
                continue
            
            info_map[src_name] = info
            file_info.info_set.put_info(info)
        
        # Second pass: restore owner relationships and hasInfoMap
        cursor.execute("""
            SELECT src_name, owner_src_name
            FROM info_base
            WHERE file_id = ? AND owner_src_name != ''
        """, (file_id,))
        
        owner_rows = cursor.fetchall()
        for src_name, owner_src_name in owner_rows:
            if src_name in info_map and owner_src_name in info_map:
                child_info = info_map[src_name]
                owner_info = info_map[owner_src_name]
                child_info.owner = owner_info
                # Add to owner's hasInfoMap
                owner_info.relationInfo.hasInfoMap.put_info(child_info)
        
        return file_info
    
    def load_all(self, include_content: bool = False) -> List[FileInfo]:
        """
        Load all FileInfo metadata from database.
        By default excludes file_content to save memory.
        """
        cursor = self.conn.cursor()
        
        if include_content:
            cursor.execute("""
                SELECT file_path, file_name, file_extension, file_content,
                       file_modified_at, parsed_at, pair_file_path
                FROM file_info
            """)
        else:
            cursor.execute("""
                SELECT file_path, file_name, file_extension, '',
                       file_modified_at, parsed_at, pair_file_path
                FROM file_info
            """)
        
        rows = cursor.fetchall()
        file_infos = []
        
        for row in rows:
            file_data = FileInfoData(
                file_path=row[0],
                file_name=row[1],
                file_extension=row[2],
                file_content=row[3],
                file_modified_at=row[4],
                parsed_at=row[5],
                pair_file_path=row[6]
            )
            file_info = FileInfo(file_data)
            file_infos.append(file_info)
        
        return file_infos
    
    def get_stale_files(self) -> List[FileInfo]:
        """Get list of files that need reparsing."""
        all_files = self.load_all(include_content=False)
        return [f for f in all_files if f.needs_reparse()]
    
    def search_info(self, keyword: str) -> List[dict]:
        """Search for InfoBase objects by keyword in src_name."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT fi.file_path, ib.info_type, ib.name, ib.src_name, 
                   ib.file_path, ib.code
            FROM info_base ib
            JOIN file_info fi ON ib.file_id = fi.id
            WHERE ib.src_name LIKE ?
        """, (f'%{keyword}%',))
        
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            results.append({
                'file_path': row[0],
                'info_type': row[1],
                'name': row[2],
                'src_name': row[3],
                'info_file_path': row[4],
                'code': row[5]
            })
        
        return results
    
    def get_stats(self) -> dict:
        """Get overall statistics."""
        cursor = self.conn.cursor()
        
        # File count
        cursor.execute("SELECT COUNT(*) FROM file_info")
        file_count = cursor.fetchone()[0]
        
        # Class count
        cursor.execute("SELECT COUNT(*) FROM info_base WHERE info_type = 'ClassInfo'")
        class_count = cursor.fetchone()[0]
        
        # Function count
        cursor.execute("SELECT COUNT(*) FROM info_base WHERE info_type = 'FunctionInfo'")
        function_count = cursor.fetchone()[0]
        
        # Var count
        cursor.execute("SELECT COUNT(*) FROM info_base WHERE info_type = 'VarInfo'")
        var_count = cursor.fetchone()[0]
        
        # Reparse needed count
        stale_files = self.get_stale_files()
        reparse_needed = len(stale_files)
        
        return {
            'file_count': file_count,
            'class_count': class_count,
            'function_count': function_count,
            'var_count': var_count,
            'reparse_needed': reparse_needed
        }
    
    def delete(self, file_path: str):
        """Delete file and all associated info_base entries (CASCADE)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM file_info WHERE file_path = ?", (file_path,))
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
