import base64
import hashlib
import binascii
import datetime
import time
from bottle import Bottle, request, template

app = Bottle()

@app.route('/', method='GET')
def home():
    text = request.query.get('text')

    if not text:
        return template('templates/encode.html')
    
    conversion = request.query.get('conversion')
    action = request.query.get('action')
    converted_text = ''

    if conversion == 'base64':
        if action == 'Decode':
            converted_text = base64.b64decode(text).decode('utf-8')
        else:
            converted_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
                
    elif conversion == 'md5':
        converted_text = hashlib.md5(text.encode('utf-8')).hexdigest()

    elif conversion.startswith('sha'):
        hash_algorithm = hashlib.new(conversion)
        hash_algorithm.update(text.encode('utf-8'))
        converted_text = hash_algorithm.hexdigest()

    elif conversion == 'hex': # to hex
        if action == 'Decode':  
            converted_text = binascii.unhexlify(text).decode('utf-8')
        else:
            converted_text = binascii.hexlify(text.encode('utf-8')).decode('utf-8')
        

    elif conversion == 'bin': # to bin
        if action == 'Decode':  
            converted_text = binascii.unhexlify(hex(int(text, 2))[2:])
            if isinstance(converted_text, bytes):
                converted_text = converted_text.decode('utf-8')
        else:
            converted_text = bin(int(binascii.hexlify(text.encode('utf-8')), 16))[2:]
        

    elif conversion == 'hex_binary': # hex to bin
        if action == 'Decode':      
            converted_text= hex(int(text, 2))[2:]
        else:
            converted_text = bin(int(text, 16))[2:]

    elif conversion == 'ascii':
        if action == 'Decode':  
            converted_text = ''.join(chr(int(char)) for char in text.split())
        else:
            converted_text = ''
            for char in text:
                converted_text += str(ord(char)) + ' '
        

    elif conversion == 'rgb_hex':
        if action == 'Decode':
            text = text.strip('#')
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
            converted_text = f"{r},{g},{b}"
        else:
            converted_text = '#'
            for value in text.split(','):
                hex_value = hex(int(value))[2:].zfill(2)
                converted_text += hex_value
        
        # r, g, b = map(int, text.split(','))
        # converted_text = f"#{r:02X}{g:02X}{b:02X}"

    elif conversion == 'datetime_timestamp':
        if action == 'Decode': 
            try:
                timestamp = int(text)
                converted_text = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                converted_text = 'Invalid timestamp'
        else:
            try:
                datetime_obj = datetime.datetime.strptime(text, "%Y-%m-%d %H:%M:%S") # 时间字符串转时间对象
                converted_text = time.mktime(datetime_obj) # 时间对象转时间戳
            except ValueError: 
                converted_text = 'Invalid datetime, valid example: 1970-01-01 08:00:00'
        



    return f'{converted_text}'

