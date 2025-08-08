# ClangParserProject

A comprehensive C/C++ static analysis tool that uses Clang's AST (Abstract Syntax Tree) to parse, analyze, and extract information from C++ source code.

## 🎯 What should I do now? (내가 지금 해야 할 게 뭘까?)

This project provides tools for:
- **Parsing C++ source code** into Abstract Syntax Trees using Clang
- **Storing analysis results** in SQLite database for persistent storage
- **Code analysis and metrics** extraction from C++ codebases
- **Machine learning integration** with CodeBERT for code embeddings
- **Interactive analysis** through Jupyter notebooks

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- LLVM/Clang installed on your system
- libclang shared library

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/thom17/ClangParserProject.git
   cd ClangParserProject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install LLVM/Clang** (if not already installed)
   - **Ubuntu/Debian**: `sudo apt-get install libclang-dev clang`
   - **macOS**: `brew install llvm`
   - **Windows**: Download from [LLVM releases](https://releases.llvm.org/)

### Basic Usage

1. **Parse a single C++ file**
   ```python
   from clangParser import clangParser
   
   # Parse a C++ file
   translation_unit = clangParser.parsing("your_file.cpp")
   
   # Visit AST nodes
   clangParser.simple_visit(translation_unit.cursor)
   ```

2. **Parse C++ code from string**
   ```python
   cpp_code = '''
   #include <iostream>
   int main() {
       std::cout << "Hello, World!" << std::endl;
       return 0;
   }
   '''
   
   tu = clangParser.parse_context(cpp_code)
   ```

3. **Run the main analysis script**
   ```bash
   python main_script.py
   ```

## 📁 Project Structure

```
ClangParserProject/
├── clangParser/           # Core Clang parsing functionality
│   ├── clangParser.py     # Main parsing logic
│   ├── datas/            # Data structures for AST representation
│   └── CursorVisitor.py   # AST traversal utilities
├── snResult/             # Database operations and storage
│   ├── ClangAST.py       # SQLAlchemy models for AST data
│   └── dataset.db        # SQLite database
├── codebert/             # CodeBERT integration for ML analysis
├── oms/                  # Object Management System
├── neo4jclang/           # Neo4j graph database integration
├── falskRESTAPI/         # Flask REST API endpoints
├── jupyter/              # Jupyter notebooks for analysis
├── test/                 # Test files and examples
└── main_script.py        # Main entry point
```

## 🔧 Main Components

### 1. ClangParser Module
The core parsing engine that:
- Configures Clang with appropriate compilation flags
- Parses C++ source files into Translation Units
- Provides AST traversal and analysis utilities

### 2. Database Storage (snResult)
- Stores parsed AST data in SQLite database
- Manages source code signatures and metadata
- Provides query interface for analysis results

### 3. Code Analysis Tools
- **CodeBERT Integration**: Extract semantic embeddings from code
- **OMS (Object Management System)**: Analyze code structure and relationships  
- **Neo4j Integration**: Store and query code relationships as graphs

### 4. Interactive Analysis
- Jupyter notebooks for exploratory data analysis
- Visualization tools for code metrics and patterns
- Machine learning pipelines for code analysis

## 📊 Usage Examples

### Analyze a C++ Project
```python
from clangParser.clangParser import parse_project

# Parse all C++ files in a directory
translation_units = parse_project("/path/to/your/cpp/project")

for tu in translation_units:
    print(f"{tu.spelling} contains {len(list(tu.cursor.get_children()))} top-level elements")
```

### Store Results in Database
```python
from snResult.ClangAST import TClangAST, get_all_table

# Get all stored analysis results
results = get_all_table('snResult/dataset.db')

for result in results:
    print(f"Source: {result.srcSig}")
    print(f"Class: {result.get_class_name()}")
```

### Extract Code Features
```python
from main_script import table2cursor, print_line

# Convert database entry to cursor and analyze
cursor = table2cursor(ast_result)
print_line(ast_result)  # Print line-by-line analysis
```

## 🛠 Development

### Running Tests
```bash
cd test/
python simpleTest.py
```

### Starting Jupyter Analysis
```bash
jupyter notebook jupyter/
```

### API Server
```bash
cd falskRESTAPI/
python app.py  # (if available)
```

## 🔍 Key Features

- **Multi-platform Support**: Works on Windows, macOS, and Linux
- **Flexible Parsing**: Handle both files and code strings
- **Database Integration**: Persistent storage of analysis results  
- **ML Ready**: CodeBERT embeddings for semantic code analysis
- **Graph Database**: Neo4j integration for relationship analysis
- **Interactive**: Jupyter notebooks for data exploration
- **Extensible**: Modular architecture for adding new analysis tools

## 📝 Configuration

The parser can be configured in `clangParser/clangParser.py`:
- Compilation flags and standards (C++14, C++17, etc.)
- Include paths for system headers
- Platform-specific settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source. Please check the repository for specific license terms.

## 🆘 Troubleshooting

### Common Issues

1. **"No module named 'clang'"**
   - Install libclang: `pip install libclang`
   - Ensure LLVM/Clang is installed on your system

2. **"libclang.dll not found"** (Windows)
   - Update the path in `clangParser.py` to point to your LLVM installation
   - Typically: `C:\Program Files\LLVM\bin\libclang.dll`

3. **"No module named 'sqlalchemy'"**
   - Install dependencies: `pip install -r requirements.txt`

4. **Parsing errors**
   - Check that your C++ code compiles with standard compilers
   - Verify include paths and compilation flags in the parser configuration

---

**Now you know what to do! (이제 뭘 해야 할지 알겠지!)** 🎉