from oms.info_set import InfoSet
import oms.Mapper as Mapper
import time

def test_parse():
    print()
    file_path = r'D:\dev\AutoPlanning\trunk\AP_trunk_pure\mod_APImplantSimulation\MeasureImplant.cpp'

    cursor_list = Mapper.get_target_cursor(file_path)

    st = time.time()
    info_set, clang_src = Mapper.parsing(file_path)
    ed = time.time()
    parse_time = ed - st


    functions = [f for f in info_set.functionInfos.values()]
    fun=functions[0]
    print(fun)

    node = clang_src[fun.src_name][0]
    info = Mapper.Cursor2InfoBase(node)

    c2info_set = InfoSet()
    st = time.time()
    for n in cursor_list:
        c2info_set.put_info(Mapper.Cursor2InfoBase(n))
    ed = time.time()
    c2info_time = ed-st
    print(info)
    print(f'parse/c2Info {parse_time:.2f}/{c2info_time}')

    print(info == fun)

    print()