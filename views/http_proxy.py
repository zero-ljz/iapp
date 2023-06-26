import urllib
import re
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
            response.content_length = resp.headers.get('Content-Length')

            # 获取原始文件名
            filename = None
            if 'Content-Disposition' in resp.headers:
                disposition = resp.headers['Content-Disposition']
                if 'filename' in disposition:
                    filename = disposition.split('filename=')[1].strip('"\'')

                # 如果未获取到文件名，从URL末尾自动判断
                if not filename:
                    url_path = urllib.parse.urlparse(resp.url).path
                    filename = url_path.split('/')[-1]

            # 设置文件下载的响应头部
            if filename:
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

            # 边收边传，通过生成器逐步返回响应内容
            def generate_content():
                for chunk in resp.iter_content(chunk_size=8192):
                    yield chunk

            # 返回生成器作为响应
            # return generate_content()

            # 如果响应内容是HTML页面，则进行正则替换
            if 'text/html' in resp.headers.get('Content-Type'):
                content = b''.join(list(generate_content())).decode('utf-8')

                # 使用正则表达式替换页面中的链接
                def replace_link(match):
                    # 获取属性名
                    attr_name = match.group(1)
                    # 获取匹配的链接
                    link = match.group(2)
                    # 使用 urllib.parse.urljoin() 函数拼接绝对链接
                    absolute_url = urllib.parse.urljoin(url, link)
                    # 进行链接替换，例如将 <a href="link"> 替换为 <a href="new_link">
                    return link.replace(link, attr_name + '' + absolute_url)

                # 对页面中的链接进行替换
                content = re.sub(
                    r'(href=["\'])(.*?)\1',
                    lambda match: replace_link(match),
                    content,
                    flags=re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.DOTALL
                )

                # 对页面中的链接进行替换
                content = re.sub(
                    r'(src=["\'])(.*?)\1',
                    lambda match: replace_link(match),
                    content,
                    flags=re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.DOTALL
                )



                return content.encode('utf-8')
            else:
                # 返回生成器作为响应
                return generate_content()

        except requests.exceptions.RequestException as e:
            return f"Error occurred: {str(e)}"
    else:
        return template('templates/http_proxy.html')
