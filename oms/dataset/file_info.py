from dataclasses import dataclass
from typing import Optional
from oms.dataset.info_base import InfoBase

@dataclass
class FileInfo(InfoBase):
    """파일 정보를 담는 클래스"""
    file_type: str
    pair_file: Optional['FileInfo'] = None  # h - cpp 파일 쌍



@dataclass
class ProjectInfo(InfoBase):
    """프로젝트 정보를 담는 클래스"""
    pass
