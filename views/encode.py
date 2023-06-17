import base64
import hashlib
import binascii
import urllib

import datetime
import time
import subprocess
from bottle import Bottle, request, template, response

app = Bottle()

@app.route('/', method='GET')
def home():
    return template('templates/encode.html')

@app.route('/<option>', method='GET')
def convert(option):
    params = request.query.decode('utf-8')
    text = params.get('1')
    action = params.get('2')
    output = ''
    print(dict(params))

    if option == 'cmd':
        # 简单的命令执行
        command = " ".join(f'"{value}"' for index, (key, value) in enumerate(dict(params).items()))
        output = subprocess.check_output(command, shell=True).decode("utf-8", errors="ignore")
        
        # 灵活的命令执行
        # command_args = [value for index, (key, value) in enumerate(dict(params).items())]
        # output = subprocess.run(command_args, capture_output=True, text=True).stdout

    elif option == 'base64':
        if action == 'Decode':
            output = base64.b64decode(text).decode('utf-8')
        else:
            output = base64.b64encode(text.encode('utf-8')).decode('utf-8')
                
    elif option == 'md5':
        output = hashlib.md5(text.encode('utf-8')).hexdigest()

    elif option.startswith('sha'):
        hash_algorithm = hashlib.new(option)
        hash_algorithm.update(text.encode('utf-8'))
        output = hash_algorithm.hexdigest()

    elif option == 'hex': # to hex
        if action == 'Decode':  
            output = binascii.unhexlify(text).decode('utf-8')
        else:
            output = binascii.hexlify(text.encode('utf-8')).decode('utf-8')
        

    elif option == 'bin': # to bin
        if action == 'Decode':  
            output = binascii.unhexlify(hex(int(text, 2))[2:])
            if isinstance(output, bytes):
                output = output.decode('utf-8')
        else:
            output = bin(int(binascii.hexlify(text.encode('utf-8')), 16))[2:]
        

    elif option == 'hex_binary': # hex to bin
        if action == 'Decode':      
            output= hex(int(text, 2))[2:]
        else:
            output = bin(int(text, 16))[2:]

    elif option == 'ascii':
        if action == 'Decode':  
            output = ''.join(chr(int(char)) for char in text.split())
        else:
            output = ''
            for char in text:
                output += str(ord(char)) + ' '
        

    elif option == 'rgb_hex':
        if action == 'Decode':
            text = text.strip('#')
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
            output = f"{r},{g},{b}"
        else:
            output = '#'
            for value in text.split(','):
                hex_value = hex(int(value))[2:].zfill(2)
                output += hex_value
        
        # r, g, b = map(int, text.split(','))
        # output = f"#{r:02X}{g:02X}{b:02X}"

    elif option == 'datetime_timestamp':
        if action == 'Decode': 
            try:
                timestamp = int(text)
                output = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                output = 'Invalid timestamp'
        else:
            try:
                datetime_obj = datetime.datetime.strptime(text, "%Y-%m-%d %H:%M:%S") # 时间字符串转时间对象
                output = time.mktime(datetime_obj) # 时间对象转时间戳
            except ValueError: 
                output = 'Invalid datetime, valid example: 1970-01-01 08:00:00'
        
    elif option == 'unicode_escape':
        # 字符串转换为 Unicode 转义序列
        if action == 'Decode':
            output = bytes(text, "utf-8").decode("unicode_escape")
            # bytes(text, "utf-8") 使用 UTF-8 编码将字符串转换为字节序列。
            # text.encode("utf-8") 显式地指定使用 UTF-8 编码将字符串转换为字节序列。
        else:
            output = text.encode("unicode_escape").decode("utf-8")

    elif option == 'uri':
        if action == 'Decode':
            output = urllib.parse.unquote(text)
        else:
            output = urllib.parse.quote(text, safe=':/?#[]@!$&\'()*+,;=%')

    elif option == 'uri_component':
        if action == 'Decode':
            output = urllib.parse.unquote(text)
        else:
            output = urllib.parse.quote(text, safe='/')



    response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    return f'{output}'

