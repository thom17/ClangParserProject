# Filter Configuration GUI Documentation

## 개요 (Overview)

프로젝트 구조를 기반으로 Skip/Include 리스트를 GUI를 통해 설정할 수 있는 시스템입니다.
폴더와 확장자를 선택하여 필터링 규칙을 구성하고, 여러 설정을 저장하여 관리할 수 있습니다.

A system for configuring Skip/Include lists through a GUI based on project structure.
Configure filtering rules by selecting folders and extensions, and manage multiple configurations.

## 주요 기능 (Key Features)

### 1. 다중 필터 설정 관리 (Multiple Filter Configurations)

- **설정 생성/저장/전환**: 여러 필터 설정을 만들고 관리
- **기본 설정**: 자동으로 생성되는 기본 설정 포함
- **활성 설정**: 현재 적용 중인 설정 선택

Example combinations:
- (Skip: build/test, Include: src/*.cpp)
- (Skip: default patterns, Include: specific folders)

### 2. 프로젝트 구조 기반 설정 (Project Structure-Based Configuration)

#### 2.1 폴더 선택 (Folder Selection)
- 프로젝트의 모든 폴더를 트리 형태로 표시
- 체크박스로 Skip/Include 선택
- 폴더별 파일 개수 표시
- 검색 기능 지원

#### 2.2 확장자 선택 (Extension Selection)
- 프로젝트에서 발견된 모든 확장자 나열
- 확장자별 파일 개수 표시
- 체크박스로 간편한 선택

#### 2.3 검색 및 다중 선택 (Search and Multi-select)
- 폴더 검색 기능
- Select All / Deselect All
- 다중 체크박스 지원

### 3. 실시간 미리보기 (Real-time Preview)

- 선택한 필터 적용 결과 미리보기
- 포함/제외 파일 목록 표시
- 통계 정보 (총 파일 수, 포함된 파일 수, 제외된 파일 수)

## 데이터베이스 스키마 (Database Schema)

### filter_config_sets 테이블

```sql
CREATE TABLE filter_config_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_default INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**설명:**
- 필터 설정의 이름과 설명 저장
- `is_default`: 기본 설정 여부
- 여러 설정을 만들어 상황에 따라 전환 가능

### filter_patterns 테이블 (Enhanced)

```sql
CREATE TABLE filter_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_set_id INTEGER,
    pattern TEXT NOT NULL,
    filter_type TEXT NOT NULL CHECK(filter_type IN ('include', 'exclude')),
    pattern_category TEXT CHECK(pattern_category IN ('folder', 'extension', 'custom')),
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (config_set_id) REFERENCES filter_config_sets(id) ON DELETE CASCADE
);
```

**변경 사항:**
- `config_set_id`: 어떤 설정에 속하는지 참조
- `pattern_category`: 패턴 종류 (folder, extension, custom)
- CASCADE DELETE: 설정 삭제 시 관련 패턴도 함께 삭제

## GUI 사용법 (GUI Usage)

### 기본 사용법

```python
from oms.parse_manager import ParseManager

# 프로젝트 초기화
manager = ParseManager('/path/to/project')

# GUI 열기
manager.open_filter_config_gui()
```

### GUI 구성 요소

#### 1. 상단 도구 모음 (Top Toolbar)
- **Configuration 선택**: 드롭다운에서 설정 선택
- **New Config**: 새 설정 생성
- **Load**: 선택한 설정 불러오기
- **Mode 선택**: Skip (Exclude) 또는 Include Only 모드

#### 2. Folders 탭
- 폴더 트리 뷰
- 검색창
- Select All / Deselect All 버튼
- 각 폴더의 파일 개수 표시

#### 3. Extensions 탭
- 확장자 목록
- 각 확장자의 파일 개수
- Select All / Deselect All 버튼

#### 4. Preview 탭
- Preview 버튼으로 결과 확인
- 포함/제외 파일 목록
- 통계 정보

#### 5. 하단 버튼 (Bottom Buttons)
- **Clear Selection**: 모든 선택 해제
- **Apply Filters**: 필터 적용 및 활성화
- **Save Configuration**: 현재 설정 저장

### 작업 흐름 (Workflow)

1. **설정 선택 또는 생성**
   - 기존 설정 선택 또는 "New Config" 클릭
   
2. **모드 선택**
   - Skip (Exclude): 선택한 항목 제외
   - Include Only: 선택한 항목만 포함

3. **폴더 선택**
   - Folders 탭에서 폴더 선택
   - 검색으로 원하는 폴더 찾기

4. **확장자 선택**
   - Extensions 탭에서 확장자 선택
   
5. **미리보기**
   - Preview 탭에서 결과 확인
   
6. **저장 및 적용**
   - Save Configuration으로 저장
   - Apply Filters로 적용

## 프로그래밍 방식 사용 (Programmatic Usage)

### 설정 생성 및 관리

```python
from oms.parse_manager import ParseManager

manager = ParseManager('/path/to/project')

# 새 설정 생성
config_id = manager.create_filter_config('my_config', 'My custom configuration')

# 패턴 추가
manager.db.add_pattern_to_config(config_id, '**/test/**', 'exclude', 'folder')
manager.db.add_pattern_to_config(config_id, '**/*.cpp', 'include', 'extension')

# 설정 전환
manager.switch_filter_config('my_config')

# 설정 목록 조회
configs = manager.list_filter_configs()
for config in configs:
    print(f"{config['name']}: {config['description']}")

# 현재 활성 설정의 패턴 조회
patterns = manager.db.get_patterns_for_active_config()
print(f"Include: {patterns['include']}")
print(f"Exclude: {patterns['exclude']}")
```

### 프로젝트 스캐너 직접 사용

```python
from oms.project_scanner import ProjectScanner

scanner = ProjectScanner('/path/to/project')
scanner.scan()

# 폴더 목록
folders = scanner.get_folders()
print(f"Folders: {folders}")

# 확장자 목록
extensions = scanner.get_extensions()
print(f"Extensions: {extensions}")

# 검색
results = scanner.get_folders('src')
print(f"Search results: {results}")

# 패턴 생성
folder_patterns = scanner.generate_folder_patterns(['test', 'build'], 'exclude')
ext_patterns = scanner.generate_extension_patterns(['.o', '.tmp'], 'exclude')

# 미리보기
preview = scanner.preview_filter([], folder_patterns + ext_patterns)
print(f"Total: {preview['total']}")
print(f"Included: {len(preview['included'])}")
print(f"Excluded: {len(preview['excluded'])}")
```

## 사용 예제 (Use Cases)

### 예제 1: 테스트 및 빌드 폴더 제외

```python
manager = ParseManager('/path/to/project')

# GUI를 통해:
# 1. Folders 탭에서 'test', 'build' 폴더 선택
# 2. Mode를 "Skip (Exclude)" 로 설정
# 3. Save Configuration

# 프로그래밍 방식:
config_id = manager.create_filter_config('no_test_build', 'Exclude test and build')
manager.db.add_pattern_to_config(config_id, '**/test/**', 'exclude', 'folder')
manager.db.add_pattern_to_config(config_id, '**/build/**', 'exclude', 'folder')
manager.switch_filter_config('no_test_build')
```

### 예제 2: C++ 소스 파일만 포함

```python
manager = ParseManager('/path/to/project')

# GUI를 통해:
# 1. Extensions 탭에서 '.cpp', '.h', '.hpp' 선택
# 2. Mode를 "Include Only" 로 설정
# 3. Save Configuration

# 프로그래밍 방식:
config_id = manager.create_filter_config('cpp_only', 'Only C++ source files')
manager.db.add_pattern_to_config(config_id, '**/*.cpp', 'include', 'extension')
manager.db.add_pattern_to_config(config_id, '**/*.h', 'include', 'extension')
manager.db.add_pattern_to_config(config_id, '**/*.hpp', 'include', 'extension')
manager.switch_filter_config('cpp_only')
```

### 예제 3: 복합 필터 (Exclude + Include)

```python
# 특정 폴더는 제외하고, 특정 확장자만 포함
manager = ParseManager('/path/to/project')

config_id = manager.create_filter_config('complex', 'Complex filtering')

# Exclude folders
manager.db.add_pattern_to_config(config_id, '**/test/**', 'exclude', 'folder')
manager.db.add_pattern_to_config(config_id, '**/build/**', 'exclude', 'folder')
manager.db.add_pattern_to_config(config_id, '**/third_party/**', 'exclude', 'folder')

# Exclude extensions
manager.db.add_pattern_to_config(config_id, '**/*.o', 'exclude', 'extension')
manager.db.add_pattern_to_config(config_id, '**/*.tmp', 'exclude', 'extension')

# Include extensions
manager.db.add_pattern_to_config(config_id, '**/*.cpp', 'include', 'extension')
manager.db.add_pattern_to_config(config_id, '**/*.h', 'include', 'extension')

manager.switch_filter_config('complex')
```

## API 참조 (API Reference)

### ParseManager

```python
# GUI 실행
manager.open_filter_config_gui()

# 설정 관리
manager.create_filter_config(name, description) -> int
manager.list_filter_configs() -> List[Dict]
manager.switch_filter_config(name)

# 패턴 관리 (기존 메서드)
manager.add_include_pattern(pattern, config_name=None)
manager.add_exclude_pattern(pattern, config_name=None)
manager.get_filter_patterns(config_name=None) -> Dict
```

### LocalDB (새로운 메서드)

```python
# 설정 관리
db.create_filter_config(name, description, set_as_default=False) -> int
db.get_filter_config_id(name) -> Optional[int]
db.get_active_filter_config_id() -> Optional[int]
db.set_active_filter_config(name)
db.list_filter_configs() -> List[Dict]

# 패턴 관리
db.add_pattern_to_config(config_id, pattern, filter_type, pattern_category)
db.get_patterns_for_config(config_id) -> Dict[str, List[str]]
db.get_patterns_for_active_config() -> Dict[str, List[str]]
```

### ProjectScanner

```python
scanner = ProjectScanner(project_root)
scanner.scan(max_depth=None)

# 조회
scanner.get_folders(search_term="") -> List[str]
scanner.get_extensions() -> List[str]
scanner.get_extension_stats() -> Dict[str, int]
scanner.get_folder_stats() -> Dict[str, int]

# 패턴 생성
scanner.generate_folder_patterns(folders, filter_type) -> List[str]
scanner.generate_extension_patterns(extensions, filter_type) -> List[str]

# 미리보기
scanner.preview_filter(include_patterns, exclude_patterns) -> Dict
```

## 문제 해결 (Troubleshooting)

### GUI가 열리지 않음

**원인:** tkinter가 설치되지 않았거나 디스플레이가 없는 환경 (SSH, CI/CD)

**해결:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (보통 기본 설치됨)
# Homebrew로 Python 설치 시 포함

# Windows (보통 기본 설치됨)
```

비대화형 환경에서는 프로그래밍 방식으로 설정:
```python
# GUI 대신 프로그래밍 방식 사용
config_id = manager.create_filter_config('auto', 'Auto configuration')
manager.db.add_pattern_to_config(config_id, '**/test/**', 'exclude', 'folder')
```

### 설정이 적용되지 않음

**확인 사항:**
1. 설정이 저장되었는지 확인
2. 활성 설정이 올바른지 확인
3. ParseManager를 다시 초기화하여 필터 재로드

```python
# 활성 설정 확인
active_config = manager.db.get_config('active_filter_config')
print(f"Active config: {active_config}")

# 필터 재초기화
manager._init_filters()
```

## 제한사항 (Limitations)

1. **깊이 제한**: 매우 큰 프로젝트의 경우 스캔 깊이 제한 권장
2. **GUI 성능**: 수천 개의 폴더가 있는 경우 성능 저하 가능
3. **패턴 복잡도**: 매우 복잡한 패턴은 프로그래밍 방식으로 직접 추가 권장

## 향후 개선 (Future Enhancements)

1. **설정 내보내기/가져오기**: JSON/YAML 형식으로 설정 공유
2. **정규표현식 지원**: 고급 패턴 매칭
3. **설정 비교**: 여러 설정 간 차이 비교
4. **템플릿**: 일반적인 프로젝트 타입별 템플릿 제공
5. **성능 최적화**: 대규모 프로젝트 지원 개선
