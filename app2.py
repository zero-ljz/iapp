from bottle import Bottle, run, template, static_file
from bottle_websocket import websocket

app = Bottle()

# 存储连接的 WebSocket 客户端
clients = []

# 静态文件路由
@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./static')

# 主页路由
@app.route('/')
def index():
    return template('index')

# WebSocket 路由
@websocket('/websocket')
def handle_websocket(ws):
    # 将新连接的 WebSocket 客户端添加到列表中
    clients.append(ws)

    # 处理 WebSocket 消息循环
    while True:
        # 接收客户端发送的消息
        message = ws.receive()

        # 如果消息为空，表示客户端关闭了连接
        if message is None:
            break

        # 将接收到的消息发送给所有连接的客户端
        for client in clients:
            client.send(message)

    # 从列表中移除已关闭连接的 WebSocket 客户端
    clients.remove(ws)

if __name__ == '__main__':
    run(app, host='localhost', port=8080, server='gevent')
