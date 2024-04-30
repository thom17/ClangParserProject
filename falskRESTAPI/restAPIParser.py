from flask import Flask, jsonify, request
import logging
import sys
sys.path.append('../')
import urllib.parse #파일경로는 인코딩되서 온다


from clangParser.CUnit import CUnit
from clangParser.Cursor import Cursor

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
        stmtMap = cursor.get_visit_stmt_map()
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


if __name__ == '__main__':
    app.run(debug=True)    #True 실시간? 재 빌드
