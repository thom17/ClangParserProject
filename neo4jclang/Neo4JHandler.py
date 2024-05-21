from py2neo import Graph, Node, Relationship
from .ClangCursor import ClangCursor
from dataclasses import asdict

class Neo4jHandler:
    def __init__(self, uri, user, password, database="neo4j"):
        self.graph = Graph(uri, auth=(user, password), name=database)

    def close(self):
        self.graph = None

    def save_cursor(self, cursor: ClangCursor):
        cursor_dict = asdict(cursor)
        cursor_node = Node("Cursor", **cursor_dict)
        self.graph.merge(cursor_node, "Cursor", "src_name")

    def get_cursor_data(self, cursor_id):
        node = self.graph.nodes.match("Cursor", id=cursor_id).first()
        if node:
            return dict(node)

    def get_cursor(self, cursor_id):
        data = self.get_cursor_data(cursor_id)
        if data:
            return ClangCursor(**data)  # Assuming ClangCursor is also a dataclass
        return None

    def find_node_by_key_value(self, key, value):
        nodes = self.graph.nodes.match("Cursor", **{key: value})
        return [dict(node) for node in nodes]

    def delete_all_nodes(self):
        self.graph.delete_all()

    def add_relationship(self, src_cursor_name, dst_cursor_name, rel_type, **properties):
        # 두 노드 찾기
        src_node = self.graph.nodes.match("Cursor", src_name=src_cursor_name).first()
        dst_node = self.graph.nodes.match("Cursor", src_name=dst_cursor_name).first()



        if not src_node or not dst_node:
            raise ValueError(f"Source or destination node not found {src_node} / {dst_node}")

        # 관계 생성
        relationship = Relationship(src_node, rel_type, dst_node, **properties)
        self.graph.create(relationship)