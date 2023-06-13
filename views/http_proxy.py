import requests
from bottle import Bottle, request, response, template

app = Bottle()

@app.route('/')
def home():
    url = request.query.get('url')
    if url:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
            }
            # 发起GET请求并获取响应
            resp = requests.get(url, headers=headers)

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

            # 根据响应内容类型返回不同的数据
            if 'text/html' in response.content_type:
                return resp.text
            else:
                return resp.content

        except requests.exceptions.RequestException as e:
            return f"Error occurred: {str(e)}"
    else:
        return template('templates/http_proxy.html')


