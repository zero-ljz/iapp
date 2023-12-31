import os
import io
from bottle import Bottle, request, run, template
from ftplib import FTP
from urllib.parse import urlparse

app = Bottle()

def upload_to_ftp(ftp_url, file_content, filename):
    try:
        parsed_url = urlparse(ftp_url)
        ftp = FTP()
        # 指定FTP服务器欢迎消息的编码为'latin-1'，这是一种支持更广泛字符范围的编码格式，可以处理包含非UTF-8编码字符的情况。但不支持中文
        #ftp.encoding = 'latin-1'
        ftp.connect(parsed_url.hostname, int(parsed_url.port if parsed_url.port else 21))
        ftp.login(parsed_url.username, parsed_url.password)

        remote_file_path = os.path.join(parsed_url.path, filename)
        print(remote_file_path)
        ftp.storbinary('STOR ' + remote_file_path, io.BytesIO(file_content))

        print("文件上传成功！")
        return True
    
    except Exception as e:
        print("文件上传失败：", str(e))
        return False
    finally:
        if ftp:
            # 关闭FTP连接
            ftp.quit()
        pass

@app.route('/')
def upload_form():
    return template('ftp_uploader/index.html')

@app.route('/upload', method='POST')
def do_upload():
    upload = request.files.get('file')
    ftp_address = request.forms.get('ftp_address')

    if upload and ftp_address:
        file_content = upload.file.read()
        filename = upload.filename

        success = upload_to_ftp(ftp_address, file_content, filename)
        if success:
            return "文件上传成功！"
        else:
            return "文件上传失败！"
    else:
        return "请选择文件和填写FTP地址！"


