from py2neo import Graph, Node, Relationship
from oms.info_set import InfoSet
from oms.dataset.info_base import InfoBase
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
        for src_name in src_map:
            if 1 < len(src_map[src_name]):
                multi_keys[src_name] = src_map[src_name]

            self.save_info(src_map[src_name][0])

        #먼저 노드 생성 후 연결 관계 추가
        for src_name in src_map:
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

