
import clang.cindex

class DataBase:
    def __init__(self, name, relationship=None, comment=None):
        self.name = name
        self.relationship = relationship if relationship else []
        self.comment = comment

class ClassData(DataBase):
    def __init__(self, name, inheritance=None, methods=None, members=None):
        super().__init__(name)
        self.inheritance = inheritance if inheritance else []
        self.methods = methods if methods else []
        self.members = members if members else []

class MethodData(DataBase):
    def __init__(self, name, parameters=None, return_type=None):
        super().__init__(name)
        self.parameters = parameters if parameters else []
        self.return_type = return_type

class MemberData(DataBase):
    def __init__(self, name, data_type=None):
        super().__init__(name)
        self.data_type = data_type

class DataList:
    def __init__(self):
        self.classes = {}
        self.methods = {}
        self.members = {}

    def add_class(self, class_data):
        self.classes[class_data.name] = class_data

    def add_method(self, method_data):
        self.methods[method_data.name] = method_data

    def add_member(self, member_data):
        self.members[member_data.name] = member_data

def parse_node(node, data_list):
    if node.kind == clang.cindex.CursorKind.CLASS_DECL:
        class_data = ClassData(node.spelling)
        data_list.add_class(class_data)
        for c in node.get_children():
            parse_node(c, data_list)
    elif node.kind == clang.cindex.CursorKind.CXX_METHOD:
        method_data = MethodData(node.spelling)
        data_list.add_method(method_data)
    elif node.kind == clang.cindex.CursorKind.FIELD_DECL:
        member_data = MemberData(node.spelling, node.type.spelling)
        data_list.add_member(member_data)

def parse_file(filename):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(filename)
    data_list = DataList()
    for node in translation_unit.cursor.get_children():
        parse_node(node, data_list)
    return data_list

# Example usage
if __name__ == "__main__":
    filename = 'example.cpp'
    data_list = parse_file(filename)

    for class_name, class_data in data_list.classes.items():
        print(f"Class: {class_name}")
        for method in class_data.methods:
            print(f"  Method: {method.name}")
        for member in class_data.members:
            print(f"  Member: {member.name}, Type: {member.data_type}")
