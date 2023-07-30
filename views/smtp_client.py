import smtplib
from email.mime.text import MIMEText
from email.header import Header

from bottle import Bottle, request, template

app = Bottle()

@app.route('/')
def index():
    return template('templates/smtp_client.html', response='')

@app.route('/send_email', method='POST')
def send_email():
    host = request.forms.get('host')
    port = int(request.forms.get('port'))
    username = request.forms.get('username')
    password = request.forms.get('password')

    sender = username
    receiver = request.forms.get('receiver') # 接收邮件的邮箱地址，可以是单个地址或多个地址，使用逗号分隔
    subject = request.forms.get('subject')
    content = request.forms.get('content')

    # 创建一个MIMEText对象，设置邮件内容
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')  # 设置邮件主题
    msg['From'] = sender  # 设置发件人
    msg['To'] = receiver  # 设置收件人

    # 连接邮件服务器并发送邮件
    try:
        smtp = smtplib.SMTP(host, port)
        smtp.starttls()  # 使用TLS加密传输
        smtp.login(username, password)  # 登录邮箱
        smtp.sendmail(sender, receiver.split(','), msg.as_string())  # 发送邮件，receiver可以是多个邮箱地址
        smtp.quit()
        out = "邮件发送成功"
    except Exception as e:
        out = str(e)

    return out