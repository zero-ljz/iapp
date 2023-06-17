
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, route, run, template, request, response, static_file
from views import textio, short_url, http_proxy, httpreq

# 创建 Bottle 应用程序对象
app = Bottle()

# 注册视图
app.mount('/textio', textio.app)
app.mount('/u', short_url.app)
app.mount('/http_proxy', http_proxy.app)
app.mount('/httpreq', httpreq.app)

# 定义路由和处理函数
@app.route('/')
def index():
    return template('templates/index.html')

@app.route('/about')
def about():
    return template('templates/about.html')

@app.route('/html5gallery')
def html5gallery():
    return template('templates/html5gallery.html')

@app.route('/color_hex_value_list')
def color_hex_value_list():
    return template('templates/color_hex_value_list.html')

@app.route('/json_viewer')
def json_viewer():
    return template('templates/json_viewer.html')

@app.route('/code_formatter')
def code_formatter():
    return template('templates/code_formatter.html')



@app.route('/htmlrun')
def htmlrun():
    return template('templates/htmlrun.html')

@app.route('/jsrun')
def jsrun():
    return template('templates/jsrun.html')

@app.route('/echo', method=['GET', 'POST'])
def echo():
    # client_ip = request.remote_addr
    client_ip = request.environ.get('REMOTE_ADDR')

    # 获取原始请求标头
    headers = '\n'.join([f'{key}: {value}' for key, value in sorted(request.headers.items())])

    request_line = f'{request.method} {request.url} {request.environ.get("SERVER_PROTOCOL")}'

    response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    response.headers['Content-Language'] = 'zh-CN'
    response.headers['Server'] = 'nginx'

    return f'IP Address: {client_ip}\n\n' + '\n'.join([f"{key}: {value}" for key, value in response.headerlist]) + '\n\n' + f'{request_line}\n{headers}\n\n{request.body.read().decode("utf-8")}'

@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='static')

# 运行应用程序
if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000, debug=True, reloader=True, server='gevent')