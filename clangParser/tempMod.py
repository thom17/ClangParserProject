import clang.cindex

def load_database():
    try:
        # Ensure this is the directory containing the compile_commands.json file
        database_path = r'D:\dev\AutoPlanning\trunk\AP-6979-TimeTask'
        database = clang.cindex.CompilationDatabase.fromDirectory(database_path)
        print("Compilation database loaded successfully!")
        return database
    except clang.cindex.CompilationDatabaseError as e:
        print(f"Failed to load compilation database: {e}")

# Example usage
db = load_database()
if db is not None:
    # Proceed with using the database for further operations
    pass
