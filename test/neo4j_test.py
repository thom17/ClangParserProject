import sys
sys.path.append('/')

from py2neo import Graph
from neo4jOMS.neo_data_service import NeoDataService
from neo4jOMS.neo_data_repository import NeoDataRepository
from unittest.mock import MagicMock

def test_load_all_data():
    # Graph 객체를 생성합니다.
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))
    service = NeoDataService(graph)
    result = service.get_all_neo_data()

    assert len(result) == 2, "Returned data count does not match"  # 반환된 데이터 개수를 검증합니다.

    print("test_load_all_data passed")

def test_search_data_by_name():
    # Graph 객체를 생성합니다.
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))
    repo = NeoDataRepository(graph)
    service = NeoDataService(repo)

    # 이름으로 데이터를 검색하는 기능을 테스트합니다.
    name_to_search = "Node1"
    mock_data = [{'n': {'name': 'Node1'}}]
    repo.find_by_name = MagicMock(return_value=mock_data)  # find_by_name 메소드를 모의합니다.

    result = service.get_neo_data_by_name(name_to_search)
    assert repo.find_by_name.called, "find_by_name method was not called"  # 메소드 호출 확인
    assert repo.find_by_name.call_args[0][0] == name_to_search, "find_by_name was called with wrong arguments"  # 메소드 호출 파라미터 검증
    assert result == mock_data, "Returned data does not match"  # 반환된 데이터 내용을 검증합니다.
    print("test_search_data_by_name passed")

if __name__ == '__main__':
    test_load_all_data()
    test_search_data_by_name()
