# ClangParserProject

A Python project for parsing and analyzing C/C++ code using Clang.

## Features

- **Code Parsing**: Parse C/C++ source code using libclang
- **AST Analysis**: Analyze Abstract Syntax Trees 
- **Code Embedding**: Generate code embeddings using transformers
- **Database Storage**: Store parsing results in SQLite database
- **Neo4j Integration**: Graph database support for code relationships
- **Web API**: Flask-based REST API for parsing services

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install LLVM/Clang (required for libclang):
   - **Windows**: Download from [LLVM releases](https://github.com/llvm/llvm-project/releases)
   - **Linux**: `sudo apt-get install libclang-dev`
   - **macOS**: `brew install llvm`

## Usage

### Basic Parsing

```python
import clangParser.clangParser as Parser

# Parse C++ code from string
cpp_code = """
#include <iostream>
int main() {
    std::cout << "Hello World!" << std::endl;
    return 0;
}
"""

translation_unit = Parser.parse_context(cpp_code)
```

### Database Operations

```python
# Run main script to process database
python main_script.py
```

## Project Structure

- `clangParser/` - Core parsing functionality
- `oms/` - Object Management System
- `codebert/` - Code embedding with transformers
- `snResult/` - Results storage and database operations
- `test/` - Test files and examples
- `jupyter/` - Jupyter notebook experiments

## Dependencies

- libclang - C/C++ parsing
- torch - Machine learning framework
- transformers - NLP models
- flask - Web framework
- sqlalchemy - Database ORM
- py2neo - Neo4j driver

## Notes

This project includes Korean documentation and comments alongside English.