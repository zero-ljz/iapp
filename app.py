
from gevent import monkey; monkey.patch_all()
from bottle import Bottle, request, response, template, static_file, redirect, abort
from views import http_client, smtp_client, sql_executor, textio, short_url, web_proxy, data_converter, code_compress, file_share, ftp_uploader, qrcode
import logging
import time
import datetime

# 设置日志记录的配置
logging.basicConfig(filename='app.log', level=logging.INFO)

# 创建 Bottle 应用程序对象
app = Bottle()

# 注册视图
# app.mount('/c', textio.app)
app.mount('/u', short_url.app)
app.mount('/p', web_proxy.app)
app.mount('/http-client', http_client.app)
app.mount('/smtp-client', smtp_client.app)
app.mount('/sql-executor', sql_executor.app)
app.mount('/data-converter', data_converter.app)
app.mount('/code-compress', code_compress.app)
app.mount('/s', file_share.app)
app.mount('/ftp-uploader', ftp_uploader.app)
app.mount('/qrcode', qrcode.app)

# 定义路由和处理函数
@app.route('/')
def index():
    return template('templates/index.html')

@app.route('/about')
def about():
    return template('templates/about.html')

@app.route('/html-gallery')
def html_gallery():
    return template('templates/html_gallery.html')

@app.route('/color-hex-value-list')
def color_hex_value_list():
    return template('templates/color_hex_value_list.html')

@app.route('/markdown-editor')
def markdown_editor():
    return template('templates/markdown_editor.html')

@app.route('/qr-code')
def qr_code():
    return template('templates/qr_code.html')

@app.route('/json-viewer')
def json_viewer():
    return template('templates/json_viewer.html')

@app.route('/vdata-generator')
def vdata_generator():
    return template('templates/vdata_generator.html')

@app.route('/code-formatter')
def code_formatter():
    return template('templates/code_formatter.html')

@app.route('/code-editor')
def code_editor():
    return template('templates/code_editor.html')

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

@app.route('/form-builder')
def form_builder():
    return template('templates/form_builder.html')

@app.route('/password-generator')
def password_generator():
    return template('templates/password_generator.html')

@app.route('/timer')
def timer():
    return template('templates/timer.html')

@app.route('/log')
def applog():
    return static_file('app.log', root='.')

@app.route('/echo', method=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/echo/<path:re:.*>', method=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def echo(path=None):
    client_ip = request.headers.get('X-Forwarded-For').split(',')[-1].strip() if request.headers.get('X-Forwarded-For') else request.headers.get('X-Real-IP') or request.environ.get('REMOTE_ADDR')

    request_line = f'{request.method} {request.path}{"?" + request.query_string if request.query_string else ""} {request.environ.get("SERVER_PROTOCOL")}'
    headers = '\n'.join([f'{key}: {value}' for key, value in sorted(request.headers.items())])
    body = request.body.read().decode("utf-8")

    response.headers['Date'] = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Cache-Control'] = 'no-store'
    response.body = f'IP Address: {client_ip}\n' + f'Time Zone: {datetime.datetime.now().astimezone().tzinfo}\n' + f'Date: {time.strftime("%Y-%m-%d %H:%M:%S")}\n' + f'Timestamp: {int(time.time())}\n\n' 
    response.body += f'{request.environ.get("SERVER_PROTOCOL")} 200 OK\n' + '\n'.join([f"{key}: {value}" for key, value in response.headerlist]) + '\n\n' + f'{request_line}\n{headers}\n\n{body}'

    print(response.body)

    logging.info('\n' + response.body)

    return response

@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='static')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the server.')
    parser.add_argument('--host', '-H', default='0.0.0.0', help='Host to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', '-p', type=int, default=8000, help='Port to listen on (default: 8000)')
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=True, reloader=True, server='gevent')