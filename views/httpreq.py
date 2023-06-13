from bottle import Bottle, request, template
import requests

app = Bottle()

@app.route('/')
def index():
    return template('templates/httpreq.html', response='')

@app.route('/send', method='POST')
def send_request():
    url = request.forms.get('url')
    method = request.forms.get('method')
    headers = request.forms.get('headers')
    body = request.forms.get('body')

    # 将请求数据组装为字典
    data = {'url': url, 'method': method}
    if headers:
        data['headers'] = headers
    if body:
        data['body'] = body

    # 发送请求并获取响应
    try:
        response = requests.request(method, url, headers=headers, data=body)
        return template('templates/httpreq.html', response=response.text)
    except requests.exceptions.RequestException as e:
        return template('templates/httpreq.html', response=str(e))

