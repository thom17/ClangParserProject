# Project-Based LocalDB with Filtering

## 개요 (Overview)

프로젝트 단위로 하나의 LocalDB를 사용하여 여러 파일의 파싱 결과를 관리하는 시스템입니다.
`.gitignore`와 유사한 필터링 기능을 제공하여 파싱 대상 파일을 제어할 수 있습니다.

One LocalDB per project manages multiple file parsing results with .gitignore-like filtering.

## 주요 변경사항 (Key Changes)

### 1. 프로젝트 기반 초기화 (Project-Based Initialization)

**이전 (Before):**
```python
# 파일마다 DB 경로 지정
manager = ParseManager('/path/to/database.db')
```

**이후 (After):**
```python
# 프로젝트 디렉토리 지정 - 자동으로 .clangparse/ 생성
manager = ParseManager('/path/to/project')
# DB는 /path/to/project/.clangparse/.clangparse.db에 생성됨
```

### 2. 필터 설정 (Filter Configuration)

#### 2.1 데이터베이스 저장 (Database Storage)

필터 패턴은 LocalDB의 `filter_patterns` 테이블에 저장됩니다.

```python
manager = ParseManager('/path/to/project')

# 포함 패턴 추가
manager.add_include_pattern('**/*.cpp')
manager.add_include_pattern('**/*.h')

# 제외 패턴 추가
manager.add_exclude_pattern('**/test/**')
manager.add_exclude_pattern('**/temp/**')

# 현재 패턴 확인
patterns = manager.get_filter_patterns()
print(patterns['include'])  # ['**/*.cpp', '**/*.h']
print(patterns['exclude'])  # ['**/test/**', '**/temp/**', ...]
```

#### 2.2 설정 파일 (Configuration File)

`.clangparse_ignore` 파일을 사용하여 필터를 정의할 수 있습니다.

**파일 형식 (.gitignore와 유사):**
```
# .clangparse_ignore
# 주석은 #으로 시작

# 제외 패턴 (한 줄에 하나씩)
**/build/**
**/dist/**
**/test/**
**/.git/**
**/*.o
**/*.obj

# 포함 패턴 (! 로 시작)
!**/*.cpp
!**/*.h
!**/*.hpp
```

**파일에서 로드:**
```python
manager = ParseManager('/path/to/project')
manager.load_filter_config()  # 프로젝트 루트의 .clangparse_ignore 로드

# 또는 특정 파일 지정
manager.load_filter_config('/path/to/custom_config')
```

### 3. 기본 제외 패턴 (Default Exclusions)

다음 패턴은 기본적으로 제외됩니다:
- `**/.git/**` - Git 디렉토리
- `**/.svn/**` - SVN 디렉토리
- `**/build/**` - 빌드 출력
- `**/dist/**` - 배포 출력
- `**/node_modules/**` - Node.js 패키지
- `**/__pycache__/**` - Python 캐시
- `**/*.pyc` - Python 컴파일 파일
- `**/CMakeFiles/**` - CMake 빌드 파일
- `**/out/**` - 출력 디렉토리
- `**/.vscode/**` - VSCode 설정
- `**/.idea/**` - IntelliJ IDEA 설정

## 사용 예제 (Usage Examples)

### 기본 사용법

```python
from oms.parse_manager import ParseManager

# 프로젝트 디렉토리로 초기화
manager = ParseManager('/path/to/my_project')

# 단일 파일 파싱
file_info = manager.smart_parse('/path/to/my_project/src/main.cpp')

# 프로젝트 전체 파싱 (필터 적용)
results = manager.smart_parse_project(add_h=True, use_filters=True)

manager.close()
```

### 필터 사용자 정의

```python
manager = ParseManager('/path/to/project')

# 특정 디렉토리만 포함
manager.add_include_pattern('**/src/**')
manager.add_include_pattern('**/include/**')

# 특정 파일 타입 제외
manager.add_exclude_pattern('**/*_test.cpp')
manager.add_exclude_pattern('**/*_mock.h')

# 프로젝트 파싱 (필터 적용)
results = manager.smart_parse_project()
```

### 설정 파일 사용

1. 프로젝트 루트에 `.clangparse_ignore` 생성:
```
# 테스트 파일 제외
**/test/**
**/*_test.cpp
**/*_unittest.cpp

# 외부 라이브러리 제외
**/third_party/**
**/external/**

# 빌드 결과물 제외
**/build/**
**/Debug/**
**/Release/**

# C++ 소스만 포함
!**/*.cpp
!**/*.h
!**/*.hpp
```

2. ParseManager로 로드:
```python
manager = ParseManager('/path/to/project')
manager.load_filter_config()  # .clangparse_ignore 자동 로드
```

## 데이터베이스 스키마 (Database Schema)

### project_config 테이블
```sql
CREATE TABLE project_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### filter_patterns 테이블
```sql
CREATE TABLE filter_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    filter_type TEXT NOT NULL CHECK(filter_type IN ('include', 'exclude')),
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);
```

## API 참조 (API Reference)

### ParseManager

```python
ParseManager(project_dir: str, db_name: str = '.clangparse.db')
```

**메서드:**
- `add_include_pattern(pattern: str)` - 포함 패턴 추가
- `add_exclude_pattern(pattern: str)` - 제외 패턴 추가
- `get_filter_patterns() -> dict` - 현재 필터 패턴 조회
- `load_filter_config(config_path: Optional[str] = None)` - 설정 파일에서 로드
- `smart_parse_project(add_h: bool = True, use_filters: bool = True)` - 프로젝트 파싱

### LocalDB

```python
LocalDB(db_path: str, project_root: Optional[str] = None)
```

**메서드:**
- `add_include_pattern(pattern: str)` - 포함 패턴 추가
- `add_exclude_pattern(pattern: str)` - 제외 패턴 추가
- `remove_pattern(pattern: str)` - 패턴 제거
- `get_include_patterns() -> List[str]` - 포함 패턴 조회
- `get_exclude_patterns() -> List[str]` - 제외 패턴 조회
- `get_all_patterns() -> Dict[str, List[str]]` - 모든 패턴 조회
- `clear_patterns(filter_type: Optional[str] = None)` - 패턴 초기화
- `set_config(key: str, value: str)` - 설정 저장
- `get_config(key: str, default: Optional[str] = None) -> Optional[str]` - 설정 조회
- `get_project_root() -> str` - 프로젝트 루트 조회

### FileFilter

```python
FileFilter(include_patterns: Optional[List[str]] = None,
           exclude_patterns: Optional[List[str]] = None,
           project_root: Optional[str] = None)
```

**메서드:**
- `should_include(file_path: str) -> bool` - 파일 포함 여부 확인
- `filter_files(file_paths: List[str]) -> List[str]` - 파일 목록 필터링
- `from_config_file(config_path: str, project_root: Optional[str] = None)` - 설정 파일에서 생성

## 패턴 문법 (Pattern Syntax)

- `*` - 단일 디렉토리 내 모든 파일/디렉토리
- `**` - 재귀적으로 모든 하위 디렉토리
- `?` - 단일 문자
- `[abc]` - 문자 집합
- `!pattern` - 포함 패턴 (설정 파일에서만)

**예제:**
- `**/*.cpp` - 모든 하위 디렉토리의 .cpp 파일
- `**/test/**` - test 디렉토리와 그 하위의 모든 것
- `src/**/*.h` - src 하위의 모든 .h 파일
- `**/*_test.cpp` - _test.cpp로 끝나는 모든 파일

## 마이그레이션 가이드 (Migration Guide)

### 기존 코드 업데이트

**이전:**
```python
import tempfile
from oms.parse_manager import ParseManager

with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
    manager = ParseManager(tmp.name)
    manager.smart_parse_project('/path/to/project')
```

**이후:**
```python
from oms.parse_manager import ParseManager

manager = ParseManager('/path/to/project')
manager.smart_parse_project()
manager.close()
```

### 필터 추가

```python
# 기본 제외 패턴에 추가
manager = ParseManager('/path/to/project')
manager.add_exclude_pattern('**/backup/**')
manager.add_exclude_pattern('**/old/**')

# 또는 설정 파일 사용
# .clangparse_ignore 파일 생성 후
manager.load_filter_config()
```

## 테스트 (Testing)

```bash
# 전체 테스트 실행
python test/test_project_based_db.py

# 데모 실행
python demo_project_based_db.py
```

## 주의사항 (Notes)

1. `.clangparse/` 디렉토리는 자동 생성되며 버전 관리에서 제외하는 것을 권장합니다.
2. `.clangparse_ignore` 파일은 프로젝트 루트에 위치하며 버전 관리에 포함할 수 있습니다.
3. 필터 패턴은 DB에 저장되므로 설정 파일 변경 시 `load_filter_config()`를 다시 호출해야 합니다.
4. 기본 제외 패턴은 첫 실행 시 자동으로 추가됩니다.
