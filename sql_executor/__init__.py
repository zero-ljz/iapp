from urllib.parse import urlparse
from bottle import Bottle, request, static_file, template
import pymysql  # 导入适当的数据库驱动

app = Bottle()


@app.route('/', method=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 从POST请求中获取SQL语句
        sql = request.forms.get('sql')
        conn_str = request.forms.get('conn_str')
        
        # 执行SQL语句
        result = execute_sql(sql, conn_str)
        
        # 渲染结果模板并返回
        return template('templates/result.html', result=result)
    
    return template('templates/index.html')


def execute_sql(sql, conn_str):

    # 解析连接字符串
    parsed_url = urlparse(conn_str)

    # 提取连接参数
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port
    database = parsed_url.path.strip('/')

    # 创建MySQL连接
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

    cursor = conn.cursor()
    
    try:
        # 执行SQL语句
        cursor.execute(sql)
        
        # 获取查询结果
        result = cursor.fetchall()
        
        # 提交事务
        conn.commit()
        
        return result
    except Exception as e:
        # 发生错误时回滚事务并抛出异常
        conn.rollback()
        raise e
    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()
