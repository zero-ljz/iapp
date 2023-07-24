import os
from bottle import Bottle, request, response, template, static_file

app = Bottle()

# 设置静态文件目录
UPLOAD_FOLDER = "uploads/file_share"

# 检查文件夹是否存在，不存在则创建
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 上传文件页面
@app.route('/')
def upload_page():
    return '''
        <a href="/share/files">View Uploaded Files</a>

        <form action="/share/upload" method="post" enctype="multipart/form-data">
        <fieldset>
          <legend>文件上传:</legend>
            <input type="file" name="file">
            <label>Custom Filename:</label>
            <input type="text" name="filename">
            <input type="submit" value="Upload">
            </fieldset>
        </form>

        <form action="/share/upload" method="post" enctype="application/x-www-form-urlencoded;charset=UTF-8">
        <fieldset>
          <legend>文件创建:</legend>
            <div style="margin-bottom:5px">
            <label>Filename: *</label>
            <input type="text" name="filename">
            </div>
            <textarea style="display:block;" name="file_content" rows="5" cols="40" placeholder="Enter file content..."></textarea>
            <input type="submit" value="Create">
        </fieldset>
        </form>
    '''

# 上传文件处理
@app.route('/upload', method='POST')
def do_upload():
    file = request.files.get('file')
    filename = request.forms.get('filename')
    file_content = request.forms.decode('utf-8').get('file_content')

    if file:
        # 获取原始文件名
        original_filename = file.filename

        # 确定保存的文件名（如果用户自定义了文件名，则使用自定义文件名，否则使用原始文件名）
        filename = filename if filename else original_filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

    elif file_content and filename:
        print(file_content)
        # 如果没有上传文件但有文本内容，保存文本内容为文件
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(file_content)
    else:
        return "Upload failed."
    
    # 生成链接
    file_url = f"/share/file/{filename}"
    return f"File uploaded successfully! Link: <a href='{file_url}'>{file_url}</a>"


# 提供静态文件服务
@app.route('/file/<filename>')
def serve_file(filename):
    return static_file(filename, root=UPLOAD_FOLDER)


# 展示文件列表
@app.route('/files')
def show_files():
    files = os.listdir(UPLOAD_FOLDER)
    file_links = [f"<a href='/share/file/{file}'>{file}</a>" for file in files]
    return "<br>".join(file_links)