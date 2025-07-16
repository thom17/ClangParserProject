import py2neo.data
from py2neo import Graph, Node, Relationship
from oms.info_set import InfoSet
from oms.dataset.info_base import InfoBase, CoreInfoData
from oms.dataset.class_info import ClassInfo
from oms.dataset.function_info import FunctionInfo
from oms.dataset.var_info import VarInfo
from dataclasses import asdict

class Neo4jHandler:
    def __init__(self, uri, user, password, database="neo4j"):
        self.graph = Graph(uri, auth=(user, password), name=database)

    def close(self):
        self.graph = None

    def save_info(self, info: InfoBase):
        info_type_name = info.__class__.__name__
        info_dict = info.to_dict()
        info_node = Node(info_type_name, **info_dict)
        self.graph.merge(info_node, info_type_name, "src_name")

    # def get_cursor_data(self, cursor_id):
    #     node = self.graph.nodes.match("Cursor", id=cursor_id).first()
    #     if node:
    #         return dict(node)neo
    #
    # def get_cursor(self, cursor_id):
    #     data = self.get_cursor_data(cursor_id)
    #     if data:
    #         return ClangCursor(**data)  # Assuming ClangCursor is also a dataclass
    #     return None
    #
    # def find_node_by_key_value(self, key, value):
    #     nodes = self.graph.nodes.match("Cursor", **{key: value})
    #     return [dict(node) for node in nodes]

    def delete_all_nodes(self):
        self.graph.delete_all()

    def add_relationship(self, host_info: InfoBase, client_info: InfoBase, rel_type: str, **properties):
        # 두 노드 찾기
        host_type_name = host_info.__class__.__name__
        client_type_name = client_info.__class__.__name__

        host_node = self.graph.nodes.match(host_type_name, src_name=host_info.src_name).first()
        client_node = self.graph.nodes.match(client_type_name, src_name=client_info.src_name).first()



        if not host_node or not client_node:
            raise ValueError(f"Source or destination node not found {host_info.src_name} / {client_info.src_name}")

        # 관계 생성
        relationship = Relationship(host_node, rel_type, client_node, **properties)
        self.graph.create(relationship)

    def make_db(self, dataset: InfoSet):
        multi_keys = {}



        src_map = dataset.get_src_map()
        size = len(src_map)
        end=0

        for src_name in src_map:
            if 1 < len(src_map[src_name]):
                multi_keys[src_name] = src_map[src_name]

            self.save_info(src_map[src_name][0])
            end+=1
            percent_complete = (end)/size * 100
            print(f"{src_name} saved. ({percent_complete:.2f})%\t\t\t\t\t", end='\r')

        print(f"Node input end.", end='\r\n')
        end= 0
        #먼저 노드 생성 후 연결 관계 추가
        for src_name in src_map:
            end += 1
            percent_complete = (end) / size * 100
            print(f"add connect. ({percent_complete:.2f})%\t\t\t\t\t\t\t", end='\r')

            info: InfoBase = src_map[src_name][0]
            if info.owner:
                self.add_relationship(info, info.owner, "owner")

            call_src_map = info.relationInfo.callInfoMap.get_src_map()
            for call_src in call_src_map:
                self.add_relationship(info, call_src_map[call_src][0], "call")

            call_by_src_map = info.relationInfo.callByInfoMap.get_src_map()
            for call_by_src in call_by_src_map:
                self.add_relationship(info, call_by_src_map[call_by_src][0], "callBy")

            has_src_map = info.relationInfo.hasInfoMap.get_src_map()
            for has_src in has_src_map:
                self.add_relationship(info, has_src_map[has_src][0], "owner")

        print(f"add connect end.\t\t\t\t\t", end='\r\n')

    def read_all_nodes(self):
        all_oms_infos = InfoSet()
        # 데이터베이스에서 모든 노드 검색
        all_nodes = self.graph.nodes.match()

        for data in [self.node_to_info(node, all_oms_infos) for node in all_nodes]:
            all_oms_infos.put_info(data)
        return all_oms_infos

    def read_update_call(self, data: InfoBase, info_set):
        try:
            query = f"MATCH (a)-[r]->(b) WHERE a.src_name CONTAINS '{data.src_name}' RETURN a, r, b"
            results = list(self.graph.run(query))
            size = len(results)
            step = 0
            # print(f"{data.src_name} : {size}" )
            for host, relation, client in results:
                percent_complete = (step + 1) / size * 100
                print(f"Progress {data.src_name}\t\t:\t\t{percent_complete:.2f}% completed\t\t", end='\r')
                self.relation_to_info(data, relation, client, info_set)
                step+=1


        except Exception as e:
            print(f"Error reading nodes: {e}")
            print(f"query : {query}")



    def relation_to_info(self, host: InfoBase, relation: py2neo.data.Relationship, client: Node, all_oms_infos: InfoSet):
        # 관계를 처리하는 함수, 관계에 대한 클래스가 필요할 수 있음
        client_data = None
        src_name = client['src_name']
        if "FunctionInfo" in client.labels:
            client_data = all_oms_infos.get_function_info(client['src_name'])
        elif "VarInfo" in client.labels:
            client_data = all_oms_infos.get_var_info(client['src_name'])
        elif "ClassInfo" in client.labels:
            client_data = all_oms_infos.get_class_info(client['src_name'])

        types = list(relation.types())
        type_name = types[0]
        if type_name == "owner":
            host.owner = client_data
        else:
            host.relationInfo.infoMap[type_name].put_info(client)
        #
        # name = relation.__name__
        # rs = relation.relationships
        # rstr = relation.__str__()
        # laberl = relation.labels()
        #
        #
        #
        #
        #
        # keys = [key for key in relation.keys()]
        #
        # start_node = relation.start_node
        # end_node = relation.end_node
        # nodes = relation.nodes
        #
        #
        # # print(rtype)
        #
        # return {
        #     "type": relation.type,
        #     "properties": dict(relation)
        # }

    def node_to_info(self, node, info_set: InfoSet):
        core_info = CoreInfoData(**node)
        # print(core_info.src_name)
        # return InfoBase(core_info)
        # 노드 레이블을 기반으로 적절한 파이썬 객체로 변환
        if "FunctionInfo" in node.labels:
            return FunctionInfo(core_info, node['owner'])
        elif "VarInfo" in node.labels:
            return VarInfo(core_info, node['owner'])
        elif "ClassInfo" in node.labels:
            return ClassInfo(core_info, node['owner'])
        # 여기에 더 많은 노드 타입을 추가할 수 있습니다.
        else:
            return InfoBase(core_info, node['owner'])  # 일반적인 InfoBase로 Fallback 처리

    # 사용 예
if __name__ == "__main__":
    import time


    start_time = time.time()
    neo4j_handler = Neo4jHandler("bolt://localhost:7687", "neo4j", "123456789")
    all_info_objects = neo4j_handler.read_all_nodes()
    src_map = all_info_objects.get_src_map()

    size = len(src_map)
    step = 0

    # for i in range(100):
    #     time.sleep(0.1)
    #     print(f"{'*' * (100-i)}", end='\r')

    for data in [src_map[src_name][0] for src_name in src_map]:
        if not 'CManipulatorOccPlane' in data.src_name:
            continue

        percent_complete = (step + 1) / size * 100
        print(f"Progress {data.src_name}\t\t:\t\t{percent_complete:.2f}% completed\t\t", end='\r')
        neo4j_handler.read_update_call(data, all_info_objects)
        step+=1

    end_time = time.time()
    db_gen_time = end_time - start_time
    print("Make DB Time :", db_gen_time, "seconds")

    data =all_info_objects.get_class_info('CManipulatorOccPlane')
    print("done")
