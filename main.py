from flask import Flask, request, jsonify
from flask_cors import CORS

from werkzeug.utils import secure_filename
import base64
import os
from datetime import datetime

from utils.chain import final
import config  # 注意这里用小写的 module 引入 config.py
import subprocess
import os

# 启动 server.py
def start_server_py():
    server_script = os.path.join(os.path.dirname(__file__), 'server.py')
    if os.path.exists(server_script):
        print("🔄 正在尝试启动 server.py ...")
        subprocess.Popen(['python', server_script])
    else:
        print("❌ server.py 文件不存在，跳过启动。")

start_server_py()


app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

folder ="input"

def save_text_to_file(text, folder=folder):
    """
    将给定的文本保存到指定文件夹下，并返回带有当前日期信息的文件名。
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{current_date}.txt"
    file_path = os.path.join(folder, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

    return file_name


def read_file_contents(file_path):
    """
    读取文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"错误：文件 '{file_path}' 未找到。"
    except IOError as e:
        return f"错误：无法读取文件 '{file_path}'，原因：{str(e)}"


@app.route('/process', methods=['POST'])
def process():
    # add read file 

    data = request.json
    #print(data)
    if 'entity_type' not in data or 'demos' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    if "text" not in data and "file" not in data:
        return jsonify({"error":"Missing required parameters"}),400
    entity_type = data['entity_type']
    print(type(entity_type))
    demos = data['demos']
    # 提取文件信息
    abs_input_path = os.path.abspath(folder)

    #text = data['text'] 
    # 获取脱敏模式
    patten = 1
    try:
        patten = data['patten']
    except:
        pass

    # 保存文本到文件
    # 给text搞个默认值
    text = ""
    filename = ""
    if "text" in data:
        text = data.get("text")
        doc_name = save_text_to_file(text)
        abs_input_path = os.path.abspath(folder)
        doc_path = os.path.join(abs_input_path, doc_name)
    else:
        # 提取文件信息
        file_info = data.get("file")
        if not file_info:
            return jsonify({"error": "Missing file data"}), 400

        # 解码Base64文件内容
        file_content = base64.b64decode(file_info.get("content", ""))
        filename = secure_filename(file_info.get("filename", "unknown.docx"))
        file_path = os.path.join(abs_input_path, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        doc_path = file_path

    # 动态设置 config 中的参数
    config.docPath = doc_path
    config.entities = entity_type
    config.demos = demos
    #print(config.docPath)
    #print(config.demos)
    #print(config.entities)
    # 执行链式处理
    output_file_path,word_dic = final(doc_path,entity_type,demos,patten=patten)

    # 读取结果
    res = read_file_contents(output_file_path)

    return jsonify({
        "result": res,
        "resource":text,
        "word_dic":word_dic,
        "file_name":filename
    })


if __name__ == '__main__':
    # 默认运行在 0.0.0.0:12345，方便局域网或远程访问
    app.run(host='0.0.0.0', port=12345, debug=True)
