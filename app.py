
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, route, run, template, request, response, static_file
from views import http_client, sql_executor, textio, short_url, http_proxy, data_converter, code_compress
import logging
import time

# 设置日志记录的配置
logging.basicConfig(filename='app.log', level=logging.INFO)

# 创建 Bottle 应用程序对象
app = Bottle()

# 注册视图
app.mount('/c', textio.app)
app.mount('/u', short_url.app)
app.mount('/proxy', http_proxy.app)
app.mount('/http-client', http_client.app)
app.mount('/sql-executor', sql_executor.app)
app.mount('/data-converter', data_converter.app)
app.mount('/code-compress', code_compress.app)

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

@app.route('/json-viewer')
def json_viewer():
    return template('templates/json_viewer.html')

@app.route('/code-formatter')
def code_formatter():
    return template('templates/code_formatter.html')

@app.route('/regex-tester')
def regex_tester():
    return template('templates/regex_tester.html')

@app.route('/unit-converter')
def unit_converter():
    return template('templates/unit_converter.html')

@app.route('/calculator')
def calculator():
    return template('templates/calculator.html')

@app.route('/html-runner')
def html_runner():
    return template('templates/html_runner.html')

@app.route('/js-runner')
def js_runner():
    return template('templates/js_runner.html')

@app.route('/log')
def applog():
    return static_file('app.log', root='.')

@app.route('/echo', method=['GET', 'POST'])
def echo():
    # client_ip = request.remote_addr
    client_ip = request.environ.get('REMOTE_ADDR') # 获取客户端IP地址

    # 获取原始请求标头
    headers = '\n'.join([f'{key}: {value}' for key, value in sorted(request.headers.items())])

    request_line = f'{request.method} {request.url} {request.environ.get("SERVER_PROTOCOL")}'

    response.headers['Content-Type'] = 'text/plain; charset=UTF-8' # 设置响应内容类型
    response.headers['Content-Language'] = 'zh-CN'
    response.headers['Server'] = 'nginx' # 伪造服务器标头
    response.headers['Access-Control-Allow-Origin'] = '*' # 允许跨域请求

    resp = f'IP Address: {client_ip}\n' + f'Date: {time.strftime("%Y-%m-%d %H:%M:%S")}\n' + f'Timestamp: {int(time.time())}\n\n' + '\n'.join([f"{key}: {value}" for key, value in response.headerlist]) + '\n\n' + f'{request_line}\n{headers}\n\n{request.body.read().decode("utf-8")}'

    logging.info('\n' + resp)

    return resp

@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='static')

# 运行应用程序
if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000, debug=True, reloader=True, server='gevent')