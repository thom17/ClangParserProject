import clang.cindex as ClangIndex

from typing import List, Union, Optional, Tuple

from enum import Enum

from dataclasses import dataclass

@dataclass
class SourceLocation:
    '''
    clang.cindex.SourceLocation를 대체
    '''
    
    line: int
    column: int

    def from_source(clang_location: ClangIndex.SourceLocation):
        return SourceLocation(
            line=clang_location.line,
            column=clang_location.column
        )

    def __str__(self):
        return f"{self.file.name if self.file else ''}:{self.line}:{self.column}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column and self.file == other.file
    
    def __float__(self):
        return float(self.line) + self.column/10000.0
    
    def __lt__(self, other):
        return float(self) < float(other)


class ClangRange:
    '''
    source_range를 다양하게 활용하기 위해 정의
    입력된 데이터에서 범위를 추출하여 생성함.
    즉 Location은 한점이 되고 그외는 SourceRange를 접근하여 할당
    '''

    def __init__(self, source: Union[ClangIndex.Cursor, ClangIndex.SourceLocation, SourceLocation, Tuple[SourceLocation, SourceLocation]]):
        self.start: SourceLocation
        self.end: SourceLocation    

        #입력된 타입에 따라 처리
        if isinstance(source, ClangIndex.Cursor):
            self.start = SourceLocation.from_source(source.extent.start)
            self.end = SourceLocation.from_source(source.extent.end)
        
        #range 입력시
        elif isinstance(source, ClangIndex.SourceRange) or isinstance(source, ClangRange):
            self.start = SourceLocation.from_source(source.start)
            self.end = SourceLocation.from_source(source.end)

        #Location이 들어오면 시작과 끝점을 동일하게 처리
        elif isinstance(source, ClangIndex.SourceLocation) or isinstance(source, SourceLocation):
            self.start = SourceLocation.from_source(source)
            self.end = SourceLocation.from_source(source)

        else:
            self.start = SourceLocation.from_source(source[0])
            self.end = SourceLocation.from_source(source[1])

        @property
        def column(self):
            return self.start.column
        
        @property
        def line(self):
            return self.start.line

    def get_relation(self, other_range: 'ClangRange') -> 'RangeRelation':
        return RangeRelation.get_relation(self, other_range)

    def __str__(self):
        if self.start == self.end:
            return str(self.start)
        else:
            return f"{self.start.line}:{self.start.column}~{self.end.line}:{self.end.column}"



class RangeRelation(str, Enum):
    NO_INTERSECTION = "⊄"        # A와 B는 서로 겹치지 않음
    IDENTICAL = "≡"              # A와 B는 완전히 동일한 범위
    PARTIALLY_OVERLAPPING = "⊗"  # A와 B는 부분적으로 겹침 (A ⊂ B, B ⊂ A 둘 다 아닌 경우)
    A_CONTAINED_IN_B = "⊂"       # A는 B에 포함됨
    B_CONTAINED_IN_A = "⊃"       # B는 A에 포함됨

    @staticmethod
    def get_relation(a: ClangRange, b: ClangRange):
        # 파일이 다른 경우: 서로 겹치지 않음

        a_start = float(a.start)
        a_end = float(a.end)
        b_start = float(b.start)
        b_end = float(b.end)


        # a와 b의 시작과 끝이 모두 동일한 경우: 완전히 동일한 범위
        if a_start == b_start and a_end == b_end:
            return RangeRelation.IDENTICAL

        # A가 B에 포함되는 경우
        if b_start <= a_start and a_end <= b_end:
            return RangeRelation.A_CONTAINED_IN_B

        # B가 A에 포함되는 경우
        if a_start <= b_start and b_end <= a_end:
            return RangeRelation.B_CONTAINED_IN_A

        # 부분적으로 겹치는 경우 (위의 포함 관계가 아닌 경우)
        if a_end > b_start and a_start < b_end:
            return RangeRelation.PARTIALLY_OVERLAPPING

        # 나머지 경우: 서로 겹치지 않음
        return RangeRelation.NO_INTERSECTION

    def get_swap(self):
        if self.value == self.A_CONTAINED_IN_B:
            return self.B_CONTAINED_IN_A
        elif self.value == self.B_CONTAINED_IN_A:
            return self.A_CONTAINED_IN_B
        else:
            return self.value

