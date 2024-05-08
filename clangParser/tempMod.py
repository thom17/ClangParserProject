from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = self.__driver.session(database=db) if db else self.__driver.session()
        try:
            response = session.run(query, parameters)
            return [record for record in response]  # 모든 레코드를 리스트로 저장
        finally:
            session.close()

# 데이터베이스 연결 설정
conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="123456789")

# 노드 생성 쿼리
conn.query("CREATE (p:Person {name: 'Bob'})")

# 노드 조회 쿼리
nodes = conn.query("MATCH (p:Person) RETURN p.name AS name")
for node in nodes:
    print(node['name'])  # 모든 노드 이름 출력

# 연결 종료
conn.close()
