# SQLite-based Parsing Data Management System

This system provides a lightweight, SQLite-based solution for managing C++ parsing data with smart caching based on file modification times.

## Overview

The system consists of three main components:

1. **FileInfo** (`oms/dataset/file_info.py`) - Container for parsed file metadata and code elements
2. **LocalDB** (`oms/local_db.py`) - SQLite database for storing and retrieving FileInfo
3. **ParseManager** (`oms/parse_manager.py`) - High-level interface for parsing and caching

## Key Features

- **Smart Caching**: Automatically detects file changes and only reparses when needed
- **Relationship Preservation**: Maintains owner relationships between code elements (classes, functions, variables)
- **Efficient Storage**: Uses SQLite for lightweight, portable data storage
- **Project-wide Parsing**: Parse entire directories with progress tracking
- **Query Support**: Search code elements by name and get statistics

## Usage Examples

See `demo_file_info_system.py` and `test/test_file_info_system.py` for complete examples.

## Testing

Run the test suite:
```bash
python test/test_file_info_system.py
```

Run the demo:
```bash
python demo_file_info_system.py
```
