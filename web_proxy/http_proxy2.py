import socket
from bottle import Bottle, request, response

app = Bottle()

def forward_request(url):
    # 解析URL获取主机和路径
    url_parts = url.split('/')
    host = url_parts[2]
    path = '/' + '/'.join(url_parts[3:])

    # 创建一个新的Socket连接
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, 80))

    # 构建HTTP请求头部
    request_headers = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}",
        "Connection: close",
        "\r\n"
    ]

    # 发送请求
    request_data = '\r\n'.join(request_headers).encode('utf-8')
    s.sendall(request_data)

    # 接收响应
    response_data = b''
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response_data += chunk

    # 关闭Socket连接
    s.close()

    return response_data

@app.route('/')
def proxy():
    url = request.query.url
    if url:
        # 转发请求并获取响应
        response_data = forward_request(url)

        # 设置响应头部
        response.content_type = 'text/html'
        return response_data
    else:
        return "Missing 'url' parameter."
