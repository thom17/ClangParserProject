import difflib
from typing import List

def find_most_similar(str_list: List[str], data: str) -> str:
    # get_close_matches는 리스트에서 가장 유사한 문자열을 찾습니다.
    # n=1은 가장 유사한 하나의 결과만 반환하도록 설정
    # cutoff=0은 모든 유사도 수준을 허용
    matches = difflib.get_close_matches(data, str_list, n=1, cutoff=0)
    if matches:
        return matches[0]
    else:
        return None  # 유사한 문자열이 없는 경우

# 사용 예시
str_list = ["apple", "apply", "apricot", "banana", "grape"]
data = '#include "../DataAccessor/DAutoGenTester.h"'

most_similar = find_most_similar(str_list, data)
print(f"'{data}'와(과) 가장 유사한 문자열은 '{most_similar}'입니다.")
