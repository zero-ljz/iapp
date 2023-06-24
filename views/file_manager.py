import os
import shutil
import urllib.request
import zipfile
import subprocess
import mimetypes
from bottle import Bottle, request, response, static_file, template, abort

app = Bottle()


@app.route('/')
def index():
    return static_file('templates/file_manager.html', root='.')
    return template('templates/file_manager.html')


# 获取文件列表
@app.get("/files")
def get_file_list():
    directory = request.query.get("directory", "/")
    directory_path = os.path.abspath(directory)
    file_list = []
    
    for name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, name)
        file_stat = os.stat(file_path)
        
        file_info = {
            "name": name,
            "path": file_path,
            "size": file_stat.st_size,
            "is_directory": os.path.isdir(file_path),
            "created_at": int(file_stat.st_ctime),
            "modified_at": int(file_stat.st_mtime)
        }
        
        file_list.append(file_info)
    
    return {"files": file_list}


# 创建目录
@app.post("/directories")
def create_directory():
    directory = request.json.get("directory")
    directory_path = os.path.abspath(directory)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return {"message": "Directory created successfully."}
    else:
        response.status = 400
        return {"error": "Directory already exists."}


# 删除文件或目录
@app.delete("/files/<filename:path>")
def delete_file(filename):
    file_path = os.path.abspath(filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        return {"message": "File deleted successfully."}
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
        return {"message": "Directory deleted successfully."}
    else:
        response.status = 404
        return {"error": "File or directory not found."}

# 批量删除文件或目录
@app.post("/files/delete")
def delete_files():
    files = request.json.get("files")

    for filename in files:
        file_path = os.path.abspath(filename)

        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    return {"message": "Files deleted successfully."}


# 复制、移动、重命名文件或目录
@app.post("/files/<filename:path>/actions")
def file_action(filename):
    action = request.json.get("action")
    destination = request.json.get("destination")

    source_path = os.path.abspath(filename)
    destination_path = os.path.abspath(destination)

    if os.path.exists(source_path):
        if action == "copy":
            if os.path.isfile(source_path):
                shutil.copy2(source_path, destination_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, destination_path)
            return {"message": "File or directory copied successfully."}
        elif action == "move":
            shutil.move(source_path, destination_path)
            return {"message": "File or directory moved successfully."}
        elif action == "rename":
            new_name = os.path.basename(destination_path)
            new_path = os.path.join(os.path.dirname(source_path), new_name)
            os.rename(source_path, new_path)
            return {"message": "File or directory renamed successfully."}

    response.status = 404
    return {"error": "File or directory not found."}


# 批量复制文件或目录
@app.post("/files/copy")
def copy_files():
    files = request.json.get("files")
    destination = request.json.get("destination")

    destination_path = os.path.abspath(destination)

    for filename in files:
        source_path = os.path.abspath(filename)

        if os.path.exists(source_path):
            if os.path.isfile(source_path):
                shutil.copy2(source_path, destination_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, os.path.join(destination_path, os.path.basename(source_path)))

    return {"message": "Files copied successfully."}


# 批量移动文件或目录
@app.post("/files/move")
def move_files():
    files = request.json.get("files")
    destination = request.json.get("destination")

    destination_path = os.path.abspath(destination)

    for filename in files:
        source_path = os.path.abspath(filename)

        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)

    return {"message": "Files moved successfully."}


# 打包文件或目录
@app.post("/files/pack")
def pack_files():
    files_to_pack = request.json.get("files")  # 获取要打包的文件列表
    zip_filename = request.json.get("zip_filename")  # 获取目标 ZIP 文件名

    # command_args = ["zip", "-r", "-q", zip_filename] + files_to_pack  # 构造命令行参数
    # print(command_args)
    # stdout = subprocess.run(command_args, capture_output=True, text=True, encoding='utf-8', errors='ignore').stdout
    # return {"message": stdout}

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zip_file:  # 创建 ZIP 文件对象
        for file_path in files_to_pack:
            file_name = os.path.basename(file_path)  # 获取文件名
            if os.path.isfile(file_path):  # 如果是文件
                zip_file.write(file_path, arcname=file_name)  # 将文件写入 ZIP，使用文件名作为目标路径
            elif os.path.isdir(file_path):  # 如果是目录
                base_dir = os.path.basename(file_path)  # 获取目录的基本名称
                for root, dirs, files in os.walk(file_path):  # 遍历目录中的文件和子目录
                    for file in files:
                        zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(file_path, '..')))

    return {"message": "Files packed successfully."}  # 返回成功消息


# 解压文件
@app.post("/files/unpack")
def unpack_files():
    zip_filename = request.json.get("zip_filename")
    extract_directory = request.json.get("extract_directory")

    with zipfile.ZipFile(zip_filename, "r") as zip_file:
        zip_file.extractall(extract_directory)

    return {"message": "Files unpacked successfully."}


# 上传文件
@app.post("/files/upload")
def upload_file():
    directory = request.forms.get("directory", "/")
    upload_path = os.path.abspath(directory)

    file = request.files.get("file")
    filename = file.raw_filename # 使用 raw_filename 来获取原始的文件名
    print(filename)
    file_path = os.path.join(upload_path, filename)

    file.save(file_path)
    return {"message": "File uploaded successfully."}


# 从远程URL上传文件
@app.post("/files/upload/remote")
def upload_remote_file():
    directory = request.json.get("directory", "/")
    upload_path = os.path.abspath(directory)

    url = request.json.get("url")
    print(url)
    filename = os.path.basename(url)
    file_path = os.path.join(upload_path, filename)

    urllib.request.urlretrieve(url, file_path)
    return {"message": "File uploaded successfully."}


# 下载文件
@app.get("/files/download/<filename:path>")
def download_file(filename):
    file_path = os.path.abspath(filename)

    if os.path.exists(file_path):
        return static_file(filename, root="/", download=filename)
    else:
        response.status = 404
        return {"error": "File not found."}


# 获取文件内容
@app.get("/files/content/<filename:path>")
def get_file_content(filename):
    file_path = os.path.abspath(filename)

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        abort(404, "File not found.")

    # 使用 mimetypes 模块获取文件的 MIME 类型
    mime_type, encoding = mimetypes.guess_type(file_path)

    # 判断文件是否为文本文件
    if not mime_type or not mime_type.startswith("text/"):
        abort(400, "Only text files can be accessed.")

    # 读取文件内容
    with open(file_path, "r", encoding='utf-8') as file:
        content = file.read()

    return {"content": content}


# 编辑文本文件
@app.post("/files/edit")
def edit_text_file():
    file_path = request.forms.get("file_path")
    content = request.forms.get("content")

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        abort(404, "File not found.")

    # 使用 mimetypes 模块获取文件的 MIME 类型
    mime_type, encoding = mimetypes.guess_type(file_path)

    # 判断文件是否为文本文件
    if not mime_type or not mime_type.startswith("text/"):
        abort(400, "Only text files can be accessed.")

    # 写入新的文件内容
    with open(file_path, "w") as file:
        file.write(content)

    return {"message": "File edited successfully."}



# if __name__ == "__main__":
#     app.run(host="localhost", port=8080)
