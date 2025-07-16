from flask import Flask, jsonify, request
import logging
import sys
sys.path.append('../')

import clangParser.clangParser as Parser

from clangParser.datas.Cursor import Cursor

app = Flask(__name__)

# 테스트 데이터
data = {
    "items": [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"}
    ]

}

import snResult.ClangAST as SNResult

snResult: [SNResult.TClangAST] = SNResult.get_all_table('../snResult/dataSet.db')

@app.route('/items', methods=['GET'])
def get_items():
    print("Get")
    return jsonify(data)



@app.route('/items', methods=['POST'])
def add_item():
    item = request.get_json()
    print("Post")
    data["items"].append(item)
    return jsonify(item), 201


@app.route('/stmt/<string:srcSig>', methods=['GET'])
def get_stmt(srcSig):
    try:
        print("get_stmt")
        target = None
        for table in snResult:
            if srcSig == table.srcSig:
                target = table
                break
        if target:
            print("find Target")
            tunit = Parser.parse_context(table.sourceCode)
            cursor = Cursor(tunit.cursor, table.sourceCode)
            stmtMap = cursor.get_visit_type_map()
            json_ready_stmtMap = {key: [c.to_dict() for c in cursor_list] for key, cursor_list in stmtMap.items()}
            return jsonify(json_ready_stmtMap)
        else:
            return "Item not found", 404
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/line/<string:srcSig>', methods=['GET'])
def get_line(srcSig:str):
    print("get_line")

    target = None
    for table in snResult:
        if srcSig == table.srcSig:
            target = table
            break
    if target:
        print("find Target")
        tunit = Parser.parse_context(table.sourceCode)

        cursor = Cursor(tunit.cursor, table.sourceCode)
        lineMap:{int, list[Cursor]}= cursor.get_visit_line_map()

        # Convert lineMap to be JSON serializable
        json_ready_lineMap = {key: [c.to_dict() for c in cursor_list] for key, cursor_list in lineMap.items()}

        # Return the line mappings as JSON
        return jsonify(json_ready_lineMap)
    else:
        return "Item not found", 404

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    print("route")
    item = next((item for item in data["items"] if item["id"] == item_id), None)
    if item is not None:
        return jsonify(item)
    else:
        return "Item not found", 404

if __name__ == '__main__':


    app.run(debug=True)    #True 실시간? 재 빌드
