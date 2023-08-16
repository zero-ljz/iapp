
from bottle import Bottle, request, response, run, template
import qrcode
import io

app = Bottle()

@app.route('/')
def index():
    return template('templates/qrcode.html')

@app.route('/generate')
@app.route('/generate/<text>/<version:int>/<error_correction>/<box_size:int>/<border:int>')
def generate_qrcode(text=None, version=1, error_correction='M', box_size=10, border=4):

    text = request.query.decode('utf-8').get('text', text)
    version = request.query.get('version', version)
    error_correction = request.query.get('error_correction', error_correction)
    box_size = request.query.get('box_size', box_size)
    border = request.query.get('border', border)

    error_correction_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction_map.get(error_correction),
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    output = io.BytesIO()
    img.save(output, format="PNG")
    response.set_header('Content-Type', 'image/png')
    return output.getvalue()
