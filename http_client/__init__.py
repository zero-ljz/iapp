import codecs
from bottle import Bottle, request, template
import requests
from requests.utils import parse_dict_header

app = Bottle()

@app.route('/')
def index():
    #return template('templates/http_request/index.html', response='')
    return template('http_client/index.html', response='')

@app.route('/send', method='POST')
def send_request():
    url = request.forms.url
    method = request.forms.method
    headers = request.forms.headers
    body = request.forms.body

    # 将请求数据组装为字典
    data = {'url': url, 'method': method}
    if headers:
        data['headers'] = headers
    if body:
        data['body'] = body

    # 发送请求并获取响应
    try:
        response = requests.request(method, url, headers=parse_dict_header(headers), data=body)
        content = response.content.decode(response.encoding, errors='ignore')
        return template('templates/http_request/result.html', response=content)
    except requests.exceptions.RequestException as e:
        return template('templates/http_request/index.html', response=str(e))


