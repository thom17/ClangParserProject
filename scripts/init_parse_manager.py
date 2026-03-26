from oms.parse_manager import ParseManager
from filemanager.window_file_open import get_folder_path

'''
프로젝트 선택 및 ParseManager 초기화 예시 코드
'''
SKIP_NOT_SYSTEM =[
    '.vs', '.git', '.svn', '.vscode', 'x64',
    'DoitCtrlTest', 'google_test', 'example_crown_loader',
    'external_dlls', 'external_libs', 'internal_libs',
    'AutoCrown', 'childprocess', 'DeepYoloV2', 'docs',
    'FixtureAutoSimul', 'ImageProcCore', 'meshlibsCommon',
    'NerveAutoDetect', 'NerveChildProcessor', 'PythonInterface',
    'Morphing', 'ReadyAlgorithm', 'TcpClient', 'TensorCore',
    'VtkUtil'
]

path = get_folder_path()

manager = ParseManager(path)

#GUI 개선 필요 정상 동작 x
# # Open GUI to configure filters
# print('opening filter configuration GUI...')
# manager.open_filter_config_gui()
# print('opened filter configuration GUI')

# 필터 옵션 로드, 저장, 목록 출력 둥 확인 가능한 기능 필요 -> 무시하고 중복 생성시 crush
# Or programmatically
# config_id = manager.create_filter_config('ap', 'Planning 관련 필터링')
# for dir in SKIP_NOT_SYSTEM:
#     manager.db.add_pattern_to_config(config_id, '**/' + dir + '/**', 'exclude', 'folder')
# manager.switch_filter_config('ap')

# Parse with filters
results = manager.smart_parse_project(use_filters=True)

all_file_infos = manager.db.load_all()
print('Parsed Infos:')
for file_info in all_file_infos:
    print(file_info)


