#!/usr/bin/env python3
"""
Example usage of ClangParserProject
This demonstrates the main functionality of the parser
"""

from clangParser.clangParser import parse_context, simple_visit
from snResult.ClangAST import TClangAST, get_all_table
from clangParser.datas.Cursor import Cursor
import os

def example_basic_parsing():
    """Example 1: Basic parsing of C++ code"""
    print("=== Example 1: Basic C++ Code Parsing ===")
    
    cpp_code = """
    #include <iostream>
    #include <vector>
    
    class Calculator {
    private:
        std::vector<double> history;
        
    public:
        double add(double a, double b) {
            double result = a + b;
            history.push_back(result);
            return result;
        }
        
        void printHistory() {
            std::cout << "History: ";
            for (auto value : history) {
                std::cout << value << " ";
            }
            std::cout << std::endl;
        }
    };
    
    int main() {
        Calculator calc;
        double result = calc.add(5.0, 3.0);
        calc.printHistory();
        std::cout << "Result: " << result << std::endl;
        return 0;
    }
    """
    
    # Parse the code
    translation_unit = parse_context(cpp_code)
    print(f"✓ Successfully parsed code into translation unit: {translation_unit.spelling}")
    
    # Visit AST nodes
    print("\n--- AST Structure ---")
    simple_visit(translation_unit.cursor)
    
    return translation_unit

def example_cursor_analysis():
    """Example 2: Advanced cursor analysis"""
    print("\n=== Example 2: Advanced Cursor Analysis ===")
    
    cpp_code = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    int main() {
        int result = factorial(5);
        return 0;
    }
    """
    
    # Parse and analyze
    tu = parse_context(cpp_code, file_remove=False)
    cursor = Cursor(tu.cursor)
    
    # Get line mapping
    line_map = cursor.get_visit_line_map()
    
    print("--- Line-by-line Analysis ---")
    for line_num in sorted(line_map.keys()):
        print(f"Line {line_num:2d}: ", end="")
        for c in line_map[line_num]:
            print(f"<{c.kind} '{c.spelling}' {c.get_range()}>", end=" ")
        print()
    
    return cursor

def example_database_operations():
    """Example 3: Database operations"""
    print("\n=== Example 3: Database Operations ===")
    
    # Check if database exists
    db_path = 'snResult/dataset.db'
    
    try:
        results = get_all_table(db_path)
        if results:
            print(f"✓ Found {len(results)} entries in database:")
            for i, result in enumerate(results[:3]):  # Show first 3 entries
                print(f"  {i+1}. {result.srcSig} -> {result.get_class_name()}")
            if len(results) > 3:
                print(f"  ... and {len(results) - 3} more entries")
        else:
            print("ℹ Database is empty or no entries found")
    except Exception as e:
        print(f"⚠ Database access error: {e}")
        print("Creating empty database for future use...")

def example_project_parsing():
    """Example 4: Parse test files in the project"""
    print("\n=== Example 4: Parse Test Files ===")
    
    test_dir = "test"
    cpp_files = []
    
    # Find C++ files in test directory
    if os.path.exists(test_dir):
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith(('.cpp', '.c', '.cxx')):
                    cpp_files.append(os.path.join(root, file))
    
    if cpp_files:
        print(f"Found {len(cpp_files)} C++ files:")
        for file_path in cpp_files[:3]:  # Parse first 3 files
            print(f"  Parsing: {file_path}")
            try:
                from clangParser.clangParser import parsing
                tu = parsing(file_path)
                child_count = len(list(tu.cursor.get_children()))
                print(f"  ✓ Success: {child_count} top-level elements")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    else:
        print("No C++ files found in test directory")

def main():
    """Run all examples"""
    print("🚀 ClangParserProject - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_parsing()
        example_cursor_analysis()
        example_database_operations()
        example_project_parsing()
        
        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("\nNext steps:")
        print("- Explore Jupyter notebooks in jupyter/ directory")
        print("- Check out the codebert/ module for ML integration")
        print("- Try parsing your own C++ projects")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()