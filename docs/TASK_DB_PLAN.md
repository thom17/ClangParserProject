# CP_Agent Task DB 구현 계획서

## 1. 개요

### 1.1 목적
- Agent에게 코드 전체 대신 **FunctionInfo(메서드) 단위**로 필요한 코드만 검색/필터링하여 제공 
- 필요한 작업 및 결과를 DB를 통해 제공 및 수집 (mcp_tool)
- Agent 작업 결과를 메서드 단위로 수집한 뒤, **FileInfo 단위로 일괄 처리**
- `file_modified_at` + 코드 내용 비교로 결과 적용 전 **변경 여부 검증**

### 1.2 참조 프로젝트
- `D:\dev\python_pure_projects\SVNTrace\mcp_tool` 의 Task DB 구조를 기반으로 설계
- SVNTrace는 Neo4j의 RvFunctionInfo를 태스크 단위로 사용
- CP_Agent는 ParserManager의 FunctionInfo를 태스크 단위로 사용

### 1.3 SVNTrace 대비 변경점
| 구분 | SVNTrace | CP_Agent |
|------|----------|----------|
| 데이터 소스 | Neo4j → RvFunctionInfo | ParserManager → FunctionInfo |
| 버전 식별 | `revision` (SVN 리비전) | `file_modified_at` (파일 수정 시각) |
| 원본 코드 | `rv_src` (리비전 소스) | 불필요 (code 자체가 현재 버전) |
| 파일 컨텍스트 | `file_path`만 | `file_path` + `file_modified_at` |
| 동기화 검증 | 없음 | SyncChecker로 적용 전 검증 |
| 결과 조인 | 없음 | InfoMatcher + ResultHandler |

---

## 2. 아키텍처

### 2.1 전체 구조
```
ParserManager (OMS)                    TaskDB (mcp_tool)
┌──────────────────┐                  ┌──────────────────┐
│ FileInfo         │                  │ MainTask         │
│  └─ InfoSet      │   src_name 조인  │  └─ SubTask      │
│     └─ FuncInfo  │ ◄──────────────► │    (pending/done)│
└──────────────────┘                  └──────────────────┘
         ▲                                     ▲
         │                                     │
         └──────── TaskManager ────────────────┘
                   ├── InfoMatcher    (대응 조회)
                   ├── SyncChecker    (동기화 체크)
                   └── ResultHandler  (결과 처리 인터페이스)
```

### 2.2 데이터 연결 방식
- **방안 (src_name 기반 조인)** 채택
- InfoBase/CoreInfoData Task DB와 관련된 직접적인 수정 없음
- TaskManager가 양쪽 데이터를 브릿지
- SubTask의 `src_name`과 FunctionInfo의 `src_name`으로 대응


### 2.3 결과 저장 방식
- **방안 (SubTask.result에 JSON 저장)** 채택
- 스키마 변경 없이 태스크 유형별 유연한 구조
- 예시: `{"hash": "sha256:abc...", "message": "완료"}`

---

## 3. DB 스키마

### 3.1 MainTask (SVNTrace 동일)
```sql
MainTask (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    request     TEXT,                              -- 태스크 설명
    status      TEXT,                              -- pending / done
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 3.2 SubTask (CP_Agent 전용)
```sql
SubTask (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    main_task_id     INTEGER,                      -- FK → MainTask
    src_name         TEXT,                          -- "MyClass::doWork(int)"
    file_path        TEXT,                          -- 소스 파일 경로
    file_modified_at REAL,                          -- 버전 식별 (파일 수정 시각)
    code             TEXT,                          -- FunctionInfo.code
    status           TEXT,                          -- pending / done
    result           TEXT,                          -- Agent 작업 결과 (JSON)
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(main_task_id) REFERENCES MainTask(id)
)
```

---

## 4. 모듈 설계

### 4.1 파일 구조
```
CP_Agent/
├── oms/                            # 기존 (수정 없음)
│   ├── parse_manager.py
│   ├── local_db.py
│   ├── info_set.py
│   └── dataset/
│       ├── info_base.py
│       ├── file_info.py
│       ├── function_info.py
│       ├── class_info.py
│       └── var_info.py
├── mcp_tool/                       # 신규 패키지
│   ├── __init__.py
│   ├── cp_task.py                  # MCP Tool 서버 (진입점)
│   ├── task_manager.py             # 통합 관리 메인 클래스
│   │
│   ├── db/                         # DB 레이어 (순수 SQLite, OMS 무관)
│   │   ├── __init__.py
│   │   ├── main_task_db.py         # MainTask 테이블 CRUD
│   │   ├── sub_task_db.py          # SubTask 테이블 CRUD + FunctionInfo 변환
│   │   └── task_db.py              # DB Facade (MainTaskDB + SubTaskDB)
│   │
│   └── handler/                    # 브릿지 레이어 (ParserManager ↔ TaskDB)
│       ├── __init__.py
│       ├── info_matcher.py         # 대응 조회 (FunctionInfo ↔ SubTask)
│       ├── sync_checker.py         # 동기화 체크 (file_modified_at + code)
│       └── result_handler.py       # 결과 처리 인터페이스 (ABC + 구현체)
```

### 4.1.1 패키지 분리 기준
| 패키지 | 관심사 | 의존 대상 |
|--------|--------|-----------|
| `db/` | SQLite CRUD, 스키마 | `sqlite3`만 (OMS 무관) |
| `handler/` | 대응/동기화/결과 처리 | `ParserManager` + `TaskDB` 양쪽 |
| 루트 (`mcp_tool/`) | 진입점, 통합 관리 | 전체 조합 |

- `db/`는 OMS를 전혀 모르는 순수 DB 레이어 (다른 프로젝트에서 재사용 가능)
- `handler/`는 OMS와 DB를 연결하는 브릿지 레이어

### 4.2 main_task_db.py — MainTask CRUD
SVNTrace의 `main_task_db.py`와 동일 구조.

| 메서드 | 설명 |
|--------|------|
| `init_schema()` | MainTask 테이블 생성 |
| `create(request)` | 태스크 생성, id 반환 |
| `get_all()` | 전체 조회 |
| `get_by_id(id)` | 단건 조회 |
| `update_status(id, status)` | 상태 변경 |

### 4.3 sub_task_db.py — SubTask CRUD + FunctionInfo 변환
SVNTrace의 `sub_task_db.py` 기반, RvFunctionInfo → FunctionInfo로 변환.

| 메서드 | 설명 |
|--------|------|
| `init_schema()` | SubTask 테이블 생성 |
| `create_from_function_info(main_task_id, func_info, file_info)` | FunctionInfo 1개 → SubTask |
| `create_batch_from_file_info(main_task_id, file_info)` | FileInfo의 전체 FunctionInfo → SubTask 벌크 |
| `create_batch_from_parse_results(main_task_id, results)` | smart_parse_project() 결과 직접 투입 |
| `fetch_pending()` | 미해결 전체 조회 |
| `fetch_pending_by_main_id(main_task_id)` | MainTask별 미해결 조회 |
| `get_all()` | 전체 조회 |
| `get_by_id(sub_task_id)` | 단건 조회 |
| `update(sub_task_id, result)` | done 처리 + 결과 저장 |
| `get_results_by_file(main_task_id)` | file_path별 done 결과 그룹핑 |
| `count_pending_by_main_id(main_task_id)` | 미해결 개수 |

### 4.4 task_db.py — DB Facade
SVNTrace의 `task_db.py`와 동일 패턴. MainTaskDB + SubTaskDB 조합.

### 4.5 info_matcher.py — 대응 조회
ParserManager의 FunctionInfo와 TaskDB의 SubTask를 `src_name`으로 대응.

| 메서드 | 설명 |
|--------|------|
| `find_function(src_name)` | ParserManager에서 FunctionInfo 조회 |
| `find_sub_task(src_name, main_task_id)` | TaskDB에서 SubTask 조회 |
| `match(main_task_id)` | 전체 대응 결과 (matched / task_only / info_only) |
| `match_by_file(main_task_id, file_path)` | 파일 단위 대응 조회 |

### 4.6 sync_checker.py — 동기화 체크
SubTask 생성 시점과 현재 파일 상태를 비교하여 결과 적용 가능 여부 판단.

| 메서드 | 설명 |
|--------|------|
| `check(main_task_id)` | 전체 동기화 리포트 (synced / stale / missing) |
| `check_file(file_path, task_modified_at)` | 파일 수정 시간 비교 |
| `check_code(src_name, task_code)` | 코드 내용 일치 여부 |
| `is_applicable(main_task_id)` | 결과 적용 가능 여부 (stale 없으면 True) |

확장 가능성:
- src_name 변경 감지 (메서드 시그니처 변경)
- 부분 stale 처리 (파일은 변경됐지만 해당 메서드는 변경 안됨)
- reparse 후 재매칭

### 4.7 result_handler.py — 결과 처리 인터페이스
ABC로 정의하여 태스크 유형별 구현체를 교체 가능하게 설계.

```python
class ResultHandler(ABC):
    @abstractmethod
    def handle(self, func_info: FunctionInfo, result: dict) -> Any: ...

    @abstractmethod
    def handle_batch(self, matched_results: List[MatchPair]) -> Any: ...
```

첫 번째 구현체: `HashResultHandler` (테스트용 해시 태그 생성)

### 4.8 task_manager.py — 통합 관리 메인 클래스
InfoMatcher, SyncChecker를 합성(composition)하고, ResultHandler를 주입받아 사용.

| 메서드 | 설명 |
|--------|------|
| `create_task(request, search_key)` | FunctionInfo 식별 → SubTask 생성 |
| `create_task_from_file(request, file_path)` | 특정 파일만 태스크 생성 |
| `apply(main_task_id, handler)` | 동기화 체크 → 대응 조회 → 핸들러 적용 |

apply() 내부 흐름:
```
TaskManager.apply(main_task_id, handler)
    ├─ SyncChecker.is_applicable()     ── 동기화 OK?
    │   ├─ check_file()                     파일 수정 시간
    │   └─ check_code()                     코드 내용
    ├─ InfoMatcher.match()             ── src_name 기준 대응 조회
    └─ ResultHandler.handle_batch()    ── 구현체에 따른 결과 처리
```

### 4.9 cp_task.py — MCP Tool 서버
SVNTrace의 `neo4j_task.py` 대응. FastMCP로 태스크 도구 노출.

| MCP Tool | 설명 |
|----------|------|
| `get_task()` | pending SubTask 1개 + MainTask request 반환 |
| `solve_sub_task(task_id, result)` | SubTask 완료 처리 |
| `print_path_info()` | DB 경로 및 상태 출력 |

---

## 5. 데이터 흐름

### 5.1 태스크 생성
```
ParserManager.smart_parse_project()
    ↓ List[(file_path, FileInfo)]
TaskManager.create_task("코드 해시 생성")
    ↓ 각 FileInfo → functionInfos 추출
    ↓ SubTask 벌크 생성 (src_name, file_path, code, file_modified_at)
TaskDB에 저장
```

### 5.2 태스크 처리 (Agent)
```
MCP: get_task()
    ↓ pending SubTask 1개 + MainTask.request
Agent가 작업 수행
    ↓
MCP: solve_sub_task(id, result_json)
    ↓ SubTask.status = done, SubTask.result = JSON
```

### 5.3 결과 적용
```
TaskManager.apply(main_task_id, HashResultHandler())
    ├─ SyncChecker: file_modified_at + code 비교 → 적용 가능?
    ├─ InfoMatcher: src_name으로 FunctionInfo ↔ SubTask 조인
    └─ ResultHandler: 조인된 결과에 핸들러 적용
        ↓
    file_path별 그룹핑된 처리 결과 반환
```

---

## 6. 테스트 계획 — 해시 태그 생성

첫 번째 테스트로 각 메서드의 해시 태그를 생성하는 태스크를 수행.

### 6.1 목적
- Task DB 전체 파이프라인 검증 (생성 → 처리 → 동기화 체크 → 결과 적용)
- FunctionInfo ↔ SubTask 대응이 정확한지 확인
- file_modified_at 기반 변경 감지 동작 확인
- 추후 메서드 필터링 및 검색에 활용

### 6.2 테스트 코드 (스케치)
```python
# scripts/mcp_hash_task.py

import hashlib, json
from oms.parse_manager import ParseManager
from mcp_tool.task_db import TaskDB
from mcp_tool.task_manager import TaskManager
from mcp_tool.result_handler import HashResultHandler

# 준비
manager = ParseManager(project_path)
task_db = TaskDB(db_path)
tm = TaskManager(manager, task_db)

# 1. 태스크 생성
main_id = tm.create_task("각 메서드의 코드 해시 생성")

# 2. Agent 시뮬레이션 — pending 태스크를 하나씩 처리
for task in task_db.fetch_pending_sub_tasks():
    code_hash = hashlib.sha256(task["code"].encode()).hexdigest()[:16]
    result = json.dumps({"hash": f"sha256:{code_hash}"})
    task_db.update_sub_task(task["id"], result)

# 3. 동기화 체크
sync_report = tm.sync.check(main_id)
print(sync_report)

# 4. 결과 적용
output = tm.apply(main_id, HashResultHandler())
for file_path, results in output.items():
    print(f"\n{file_path}")
    for r in results:
        print(f"  {r['src_name']} → {r['hash']}")
```

### 6.3 검증 항목
| 단계 | 검증 사항 |
|------|-----------|
| 태스크 생성 | FunctionInfo가 SubTask로 정확히 변환되는가 |
| 태스크 처리 | result JSON 저장/파싱이 정상인가 |
| 동기화 체크 | file_modified_at 비교가 정확한가 |
| 코드 비교 | 동일 코드를 stale로 오판하지 않는가 |
| 결과 대응 | src_name 조인이 정확한가 |
| 결과 그룹핑 | file_path별 그룹핑이 정확한가 |

---

## 7. 구현 순서

### Phase 1: DB 레이어 (`mcp_tool/db/`)
1. `mcp_tool/__init__.py`, `mcp_tool/db/__init__.py` — 패키지 초기화
2. `mcp_tool/db/main_task_db.py` — MainTask CRUD (SVNTrace 기반)
3. `mcp_tool/db/sub_task_db.py` — SubTask CRUD + FunctionInfo 변환
4. `mcp_tool/db/task_db.py` — Facade

### Phase 2: 브릿지 레이어 (`mcp_tool/handler/`)
5. `mcp_tool/handler/__init__.py` — 패키지 초기화
6. `mcp_tool/handler/info_matcher.py` — 대응 조회
7. `mcp_tool/handler/sync_checker.py` — 동기화 체크
8. `mcp_tool/handler/result_handler.py` — ABC + HashResultHandler

### Phase 3: 통합 및 서비스
9. `mcp_tool/task_manager.py` — 통합 관리
10. `mcp_tool/cp_task.py` — MCP Tool 서버

### Phase 4: 테스트
11. `scripts/test_hash_task.py` — 해시 태그 테스트
