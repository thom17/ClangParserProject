from dataclasses import dataclass
from oms.dataset.info_base import InfoBase

@dataclass
class FileInfo(InfoBase):
    # ClassInfo에 필요한 추가 필드를 정의합니다.
    file_type: str
    pair_file: 'FileInfo'# h - cpp



@dataclass
class ProjectInfo(InfoBase):
