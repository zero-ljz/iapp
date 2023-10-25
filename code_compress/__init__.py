from bottle import Bottle, request, response, template
import jsmin
import csscompressor
import htmlmin

app = Bottle()

@app.route('/')
def index():
    return template('code_compress/index.html')

@app.route('/', method='POST')
def compress_code():
    
    code = request.body.read().decode('utf-8')
    code_type = request.headers.get('Operation')

    if code_type == 'js':
        # JavaScript code compression and obfuscation
        compressed_code = jsmin.jsmin(code)
        return compressed_code

    elif code_type == 'css':
        # CSS code compression
        compressed_code = csscompressor.compress(code)
        return compressed_code

    elif code_type == 'html':
        # HTML code compression
        compressed_code = htmlmin.minify(code, remove_comments=True, remove_empty_space=True)
        return compressed_code

    else:
        return 'Invalid code type'




