import requests
from bottle import Bottle, request, response, template

app = Bottle()

@app.route('/')
def home():
    url = request.query.get('url')
    if url:
        try:
            headers = {
                "User-Agent": request.headers.get('User-Agent'),
            }
            # 发起GET请求并获取响应
            resp = requests.get(url, headers=headers, stream=True)

            # 设置响应头部
            response.content_type = resp.headers.get('Content-Type')

            # 获取原始文件名
            filename = None
            if 'Content-Disposition' in resp.headers:
                disposition = resp.headers['Content-Disposition']
                if 'filename' in disposition:
                    filename = disposition.split('filename=')[1].strip('"\'')

            # 设置文件下载的响应头部
            if filename:
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

            # 边收边传，通过生成器逐步返回响应内容
            def generate_content():
                for chunk in resp.iter_content(chunk_size=8192):
                    yield chunk

            # 返回生成器作为响应
            return generate_content()

        except requests.exceptions.RequestException as e:
            return f"Error occurred: {str(e)}"
    else:
        return template('templates/http_proxy.html')
