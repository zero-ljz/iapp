
from bottle import Bottle, route, run, template, request, response
from views import encode, postman, short_url, http_proxy, httpreq

# 创建 Bottle 应用程序对象
app = Bottle()

config = {
    'debug': True,
    'host': '0.0.0.0',
    'port': 12312
}

# 注册视图
app.mount('/encode', encode.app)
app.mount('/postman', postman.app)
app.mount('/short_url', short_url.app)
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




@app.route('/htmlrun')
def htmlrun():
    return template('templates/htmlrun.html')

@app.route('/jsrun')
def jsrun():
    return template('templates/jsrun.html')

@app.route('/echo', method=['GET', 'POST'])
def echo():
    # 获取原始请求标头
    headers = '\n'.join([f'{key}: {value}' for key, value in sorted(request.headers.items())])

    request_line = f'{request.method} {request.url} {request.environ.get("SERVER_PROTOCOL")}'

    return '\n'.join([f"{key}: {value}" for key, value in response.headerlist]) + '\n\n' + f'{request_line}\n{headers}\n\n{request.body.read()}'


# 运行应用程序
if __name__ == '__main__':
    run(app, host=config['host'], port=config['port'], debug=config['debug'])