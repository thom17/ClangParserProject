import clang.cindex
import os


def load_database(database_path: str = None):
    """
    컴파일 데이터베이스를 로드합니다.
    
    :param database_path: compile_commands.json 파일이 있는 디렉토리 경로
    :return: CompilationDatabase 객체 또는 None
    """
    if database_path is None:
        # 현재 디렉토리나 상위 디렉토리에서 compile_commands.json 찾기
        search_paths = ['.', '..', '../..']
        for path in search_paths:
            if os.path.exists(os.path.join(path, 'compile_commands.json')):
                database_path = path
                break
        
        if database_path is None:
            print("compile_commands.json 파일을 찾을 수 없습니다.")
            return None
    
    try:
        database = clang.cindex.CompilationDatabase.fromDirectory(database_path)
        print(f"컴파일 데이터베이스 로드 성공: {database_path}")
        return database
    except clang.cindex.CompilationDatabaseError as e:
        print(f"컴파일 데이터베이스 로드 실패: {e}")
        return None


if __name__ == "__main__":
    # 사용 예제
    db = load_database()
    if db is not None:
        print("데이터베이스를 사용할 준비가 되었습니다.")
    else:
        print("데이터베이스 로드에 실패했습니다.")
