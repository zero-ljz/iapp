import urllib
import re
import requests
import sys
from urllib.parse import urlparse
from bottle import Bottle, request, response, template

app = Bottle()

@app.route('/<url:re:.*>', method=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def home(url):
    query_string = request.query_string
    if query_string:
        url += '?' + query_string

    if url:
        try:
            # 转发请求头
            headers = dict(request.headers)

            print('客户端发送的请求头', headers)

            # 要删除的请求头字段列表
            headers_to_remove = [
                'Host',
                # 'Connection',
                # 'Cache-Control',
                # 'Sec-Ch-Ua',
                # 'Sec-Ch-Ua-Mobile',
                # 'Sec-Ch-Ua-Platform',
                # 'Upgrade-Insecure-Requests',
                # 'User-Agent',
                # 'Accept',
                # 'Sec-Fetch-Site',
                # 'Sec-Fetch-Mode',
                # 'Sec-Fetch-User',
                # 'Sec-Fetch-Dest',
                # 'Accept-Encoding',
                # 'Accept-Language',
                # 'Cookie'
            ]

            # 使用 pop() 方法删除指定的请求头字段
            for header in headers_to_remove:
                headers.pop(header, None)

            #headers['Host'] = urlparse(url).netloc
            #headers['Accept'] = '*/*'
            #headers['User-Agent'] = 'curl/7.85.0'

            headers['Cache-Control'] = 'no-cache'

            print('转发给目标服务器的请求头', headers)

            # 发起代理请求
            proxy_response = requests.request(request.method, url, headers=headers, data=request.body.read(), stream=True, allow_redirects=True, verify=False, timeout=600)
            print(url)
            print(proxy_response.status_code)
            

            print('目标服务器的响应头', proxy_response.headers)

            # 将代理响应的头部字段复制到响应对象
            for key, value in proxy_response.headers.items():
                print(key, value)
                if key not in ('Content-Encoding', 'Transfer-Encoding', 'Cache-Control'):  # 'Connection'
                    response.headers[key] = value

            # 设置允许的请求来源
            response.headers['Access-Control-Allow-Origin'] = '*'  # 允许所有来源访问，可以根据需求进行修改
            # 设置允许的请求方法
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            # 设置允许的请求头部
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With'

            response.status = proxy_response.status_code

            print('响应头', dict(response.headers))

            if "Content-Length" in proxy_response.headers and int(proxy_response.headers["Content-Length"]) > 8192:
                print('大于8192')
                # 边收边传，通过生成器逐步返回响应内容
                def generate_content():
                    for chunk in proxy_response.iter_content(chunk_size=8192):
                        yield chunk

                # 返回生成器作为响应
                return generate_content()
            else:
                # 直接返回响应内容
                return proxy_response.content

        except requests.exceptions.RequestException as e:
            return f"Error occurred: {str(e)}"
    else:
        return template('templates/http_proxy.html')









# @app.route('/<url:re:.*>', method=['GET', 'POST'])
# def home(url):
#     if url:
#         try:
#             headers = {
#                 "User-Agent": request.headers.get('User-Agent'),
#             }
#             # 发起GET请求并获取响应
#             resp = requests.request(url=url, method='GET', headers=headers, data=request.body.read(), stream=True)
#             #resp = requests.get(url, headers=headers, stream=True)
#             print(resp.status_code)

#             # 设置响应头部
#             response.content_type = resp.headers.get('Content-Type')
#             # response.content_type = 'application/octet-stream' # 二进制流数据（常见的文件下载）
#             #response.content_length = resp.headers.get('Content-Length')

#             # 获取原始文件名
#             filename = None
#             if 'Content-Disposition' in resp.headers:
#                 disposition = resp.headers['Content-Disposition']
#                 if 'filename' in disposition:
#                     print('*'*50 + f'\n【f_name】: {sys._getframe().f_code.co_name}' + f'\n【f_lineno】: {sys._getframe().f_lineno}' + f'\n【var type】: {type(disposition)}' + f'\n【var dir】: {dir(disposition)}' + '\n'+'*'*50 )
#                     filename = disposition.split('filename=')[1].strip('"\'')

#             # 如果未获取到文件名，从URL末尾自动判断
#             # if not filename:
#             #     print('*'*50 + f'\n【f_name】: {sys._getframe().f_code.co_name}' + f'\n【f_lineno】: {sys._getframe().f_lineno}' + f'\n【var type】: {type(filename)}' + f'\n【var dir】: {dir(filename)}' + '\n'+'*'*50 )
#             #     url_path = urllib.parse.urlparse(resp.url).path
#             #     filename = url_path.split('/')[-1]

#             print(filename)
#             # 设置文件下载的响应头部
#             if filename:
#                 response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

#             # 边收边传，通过生成器逐步返回响应内容
#             def generate_content():
#                 for chunk in resp.iter_content(chunk_size=8192):
#                     yield chunk

#             # 返回生成器作为响应
#             return generate_content()

#             # 如果响应内容是HTML页面，则进行正则替换
#             # if 'text/html' in resp.headers.get('Content-Type'):
#             #     content = b''.join(list(generate_content())).decode('utf-8')

#             #     # 使用正则表达式替换页面中的链接
#             #     def replace_link(match):
#             #         # 获取属性名
#             #         attr_name = match.group(1)
#             #         # 获取匹配的链接
#             #         link = match.group(2)
#             #         # 使用 urllib.parse.urljoin() 函数拼接绝对链接
#             #         absolute_url = urllib.parse.urljoin(url, link)
#             #         # 进行链接替换，例如将 <a href="link"> 替换为 <a href="new_link">
#             #         return link.replace(link, attr_name + '' + absolute_url)

#             #     # 对页面中的链接进行替换
#             #     content = re.sub(
#             #         r'(href=["\'])(.*?)\1',
#             #         lambda match: replace_link(match),
#             #         content,
#             #         flags=re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.DOTALL
#             #     )

#             #     # 对页面中的链接进行替换
#             #     content = re.sub(
#             #         r'(src=["\'])(.*?)\1',
#             #         lambda match: replace_link(match),
#             #         content,
#             #         flags=re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.DOTALL
#             #     )



#             #     return content.encode('utf-8')
#             # else:
#             #     # 返回生成器作为响应
#             #     return generate_content()

#         except requests.exceptions.RequestException as e:
#             return f"Error occurred: {str(e)}"
#     else:
#         return template('templates/http_proxy.html')

