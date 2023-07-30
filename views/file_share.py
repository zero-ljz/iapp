import os
import base64
from bottle import Bottle, request, response, template, static_file, abort, HTTPError, HTTPResponse

app = Bottle()

# 设置静态文件目录
UPLOAD_FOLDER = "uploads/file_share"

# 检查文件夹是否存在，不存在则创建
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 假设这是保存在服务器端的用户名和密码信息
users = {
    'user1': '123123'
}

def check_auth(username, password):
    """检查用户名和密码是否有效"""
    return username in users and users[username] == password

def requires_auth(f):
    """装饰器函数，用于进行基本认证"""
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_type, credentials = auth_header.split(' ')
            if auth_type.lower() == 'basic':
                decoded_credentials = base64.b64decode(credentials).decode('utf-8')
                username, password = decoded_credentials.split(':', 1)
                if check_auth(username, password):
                    # 用户名和密码有效，继续执行被装饰的视图函数
                    return f(*args, **kwargs)
        
        # 认证失败，返回401 Unauthorized状态码，并添加WWW-Authenticate头
        response = HTTPResponse(status=401)
        response.headers['WWW-Authenticate'] = 'Basic realm="Restricted Area"'
        return response

    return wrapper


# 上传文件页面
@app.route('/')
@app.route('/<filename>')
@requires_auth
def upload_page(filename=None):
    if not filename:
        return template('templates/file_share.html')
    else: 
        return static_file(filename, root=UPLOAD_FOLDER)

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
    file_url = f"/s/{filename}"
    return f"File uploaded successfully! Link: <a href='{file_url}'>{file_url}</a>"

# 展示文件列表
@app.route('/files')
def show_files():
    files = os.listdir(UPLOAD_FOLDER)
    file_links = [f"<a href='/s/{file}'>{file}</a>" for file in files]
    return "<br>".join(file_links)