from bottle import Bottle, request, response, template
import jsmin
import csscompressor
import htmlmin
import sys
#import pyminifier

app = Bottle()

@app.route('/')
def index():
    return template('templates/code_compress.html')

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

    # elif code_type == 'python':
    #     # Python code obfuscation
    #     compressed_code = pyminifier.pyminify(code, remove_literal_statements=True)
    #     return compressed_code

    else:
        return 'Invalid code type'




