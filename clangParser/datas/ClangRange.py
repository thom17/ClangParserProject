from clang.cindex import SourceLocation, SourceRange
from clang.cindex import Cursor as ClangCursor


from typing import List, Union, Optional

from enum import Enum
class RangeRelation(str, Enum):
    NO_INTERSECTION = "⊄"        # A와 B는 서로 겹치지 않음
    IDENTICAL = "≡"              # A와 B는 완전히 동일한 범위
    PARTIALLY_OVERLAPPING = "⊗"  # A와 B는 부분적으로 겹침 (A ⊂ B, B ⊂ A 둘 다 아닌 경우)
    A_CONTAINED_IN_B = "⊂"       # A는 B에 포함됨
    B_CONTAINED_IN_A = "⊃"       # B는 A에 포함됨

    @staticmethod
    def get_relation(a: SourceRange, b: SourceRange):
        def location_to_float(location):
            """
            SourceLocation을 float으로 변환합니다.
            라인 번호는 정수 부분, 컬럼 번호는 소수 부분에 해당합니다.
            """
            return float(location.line) + (location.column / 1000.0)

        # 파일이 다른 경우: 서로 겹치지 않음
        if a.file != b.file:
            return RangeRelation.NO_INTERSECTION

        a_start = location_to_float(a.start)
        a_end = location_to_float(a.end)
        b_start = location_to_float(b.start)
        b_end = location_to_float(b.end)


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

class ClangRange:
    '''
    source_range를 다양하게 활용하기 위해 정의
    입력된 데이터에서 범위를 추출하여 생성함.
    즉 Location은 한점이 되고 그외는 SourceRange를 접근하여 할당
    '''

    def __init__(self, source: Union[ClangCursor, 'Cursor', SourceLocation, SourceRange]):
        #MyCursor의 경우 clangCursor로 변경
        self.file:Optional[str] = None

        if hasattr(source, 'node'):
            source = source.node

        #입력된 타입에 따라 처리
        if isinstance(source, ClangCursor):
            self.source: Optional[ClangCursor] = source
            if source.location.file:
                self.file = source.location.file.name


            self.start: SourceLocation = source.extent.start
            self.end: SourceLocation = source.extent.end
            self.f_start: float = self.start.line + self.start.column / 1000.0
            self.f_end: float = self.end.line + self.end.column / 1000.0

        elif isinstance(source, SourceRange):
            if source.start.file:
                self.file = source.start.file.name

            self.source: Optional[ClangCursor] = None
            self.start: SourceLocation = source.start
            self.end: SourceLocation = source.end
            self.f_start: float = self.start.line + self.start.column/1000.0
            self.f_end: float = self.end.line + self.end.column/1000.0

        #Location이 들어오면 시작과 끝점을 동일하게 처리
        elif isinstance(source, SourceLocation):
            if source.file:
                self.file = source.file.name

            self.source: Optional[ClangCursor] = None
            self.start: SourceLocation = source
            self.end: SourceLocation = source
            self.f_start: float = self.start.line + self.start.column/1000.0
            self.f_end: float = self.end.line + self.end.column/1000.0

        self.size = int(self.f_end) - int(self.f_start)

    def get_relation(self, other_range: 'ClangRange') -> RangeRelation:
        return RangeRelation.get_relation(self, other_range)



