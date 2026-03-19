from oms.parse_manager import ParseManager
from filemanager.window_file_open import get_folder_path

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
#
# # Open GUI to configure filters
# print('opening filter configuration GUI...')
# manager.open_filter_config_gui()
# print('opened filter configuration GUI')


# Or programmatically
config_id = manager.create_filter_config('ap', 'Planning 관련 필터링')
for dir in SKIP_NOT_SYSTEM:
    manager.db.add_pattern_to_config(config_id, '**/' + dir + '/**', 'exclude', 'folder')
manager.switch_filter_config('ap')

# Parse with filters
results = manager.smart_parse_project(use_filters=True)

