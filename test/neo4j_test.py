import sys

from neo4jclang.Visitor import visit_unit_to_db, CUnit

if __name__ == '__main__':
    unit = CUnit.parse(r'D:\dev\AutoPlanning\trunk\AP_trunk_Task\AppUICore\ActuatorHybrid.cpp')
    visit_unit_to_db(unit)
    print('done')
