import smtplib
from email.mime.text import MIMEText
from email.header import Header

from bottle import Bottle, request, template

app = Bottle()

@app.route('/')
def index():
    return template('smtp_client/index.html', response='')

@app.route('/send_email', method='POST')
def send_email():
    host = request.forms.host
    port = int(request.forms.port)
    username = request.forms.username
    password = request.forms.password

    sender = username
    receiver = request.forms.receiver # 接收邮件的邮箱地址，可以是单个地址或多个地址，使用逗号分隔
    subject = request.forms.subject
    content = request.forms.content

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
        failed_recipients = smtp.sendmail(sender, receiver.split(','), msg.as_string())  # 发送邮件，receiver可以是多个邮箱地址
        smtp.quit()
        if not failed_recipients:
            out = "邮件发送成功！"
        else:
            out = "邮件发送失败，以下收件人发送失败：\n"
            for recipient, error in failed_recipients.items():
                out += f"{recipient}: {error}\n"
    except Exception as e:
        out = str(e)

    return out