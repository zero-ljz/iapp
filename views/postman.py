from bottle import Bottle, template

# 创建 Bottle 应用程序对象
app = Bottle()

# 定义路由和处理函数
@app.route('/')
def index():
    return template('templates/postman.html')