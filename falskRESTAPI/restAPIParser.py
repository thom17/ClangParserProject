from flask import Flask, jsonify
import logging
import sys
sys.path.append('../')
import urllib.parse #파일경로는 인코딩되서 온다


from clang.cindex import Cursor as clangCursor

from clangParser.datas.CUnit import CUnit
from clangParser.datas.Cursor import Cursor
from clangParser.datas.CursorOMS import CursorOMS

app = Flask(__name__)

@app.route('/stmt/<string:file_path>/<int:line_num>', methods=['GET'])
def get_stmt(file_path:str, line_num:int):
    try:
        print("recv get_stmt")
        decoded_path = urllib.parse.unquote(file_path)
        print(file_path, "->", decoded_path)
        unit = CUnit.parse(decoded_path)
        print("parse Done")

        cursor: Cursor = Cursor(unit.get_method_body(line_num))
        stmtMap = cursor.get_visit_type_map()
        json_ready_stmtMap = {key: [c.to_dict() for c in cursor_list] for key, cursor_list in stmtMap.items()}
        return jsonify(json_ready_stmtMap)

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/line/<string:file_path>/<int:line_num>', methods=['GET'])
def get_line(file_path:str, line_num:int):
    try:
        print("recv get_line")
        decoded_path = urllib.parse.unquote(file_path)
        print(file_path, "->", decoded_path)
        unit = CUnit.parse(decoded_path)
        print("parse Done")
        cursor: Cursor = Cursor(unit.get_method_body(line_num))
        lineMap:{int, list[Cursor]}= cursor.get_visit_line_map()

        # Convert lineMap to be JSON serializable
        json_ready_lineMap = {key: [c.to_dict() for c in cursor_list] for key, cursor_list in lineMap.items()}

        # Return the line mappings as JSON
        return jsonify(json_ready_lineMap)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/call/<string:file_path>/<int:line_num>', methods=['GET'])
def get_call(file_path:str, line_num:int):
    try:
        print("recv get call")
        decoded_path = urllib.parse.unquote(file_path)
        print(file_path, "->", decoded_path)
        unit = CUnit.parse(decoded_path)
        print("parse Done")
        cursor: Cursor = Cursor(unit.get_method_body(line_num))
        def_map: [clangCursor, clangCursor] = cursor.get_call_definition_map()

        json_call_map = {}

        for call_node in def_map:
            def_cursor = Cursor(def_map[call_node])
            json_call_map[def_cursor.get_src_name()] = def_cursor.to_dict()

        # Return the line mappings as JSON
        return jsonify(json_call_map)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/oms/<string:file_path>', methods=['GET'])
def get_oms(file_path:str):
    try:
        print("recv get oms")
        decoded_path = urllib.parse.unquote(file_path)
        print(file_path, "->", decoded_path)
        unit = CUnit.parse(decoded_path)
        print("parse Done")

        json_oms_map = {}

        for node in unit.this_file_nodes:
            oms: CursorOMS = CursorOMS.GetCursorOMS(node)
            json_oms_map[oms.get_src_name()] = oms.to_dict()

        # Return the line mappings as JSON
        return jsonify(json_oms_map)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)    #True 실시간? 재 빌드
