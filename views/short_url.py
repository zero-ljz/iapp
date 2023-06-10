from bottle import Bottle, redirect, request, response, template
import sqlite3
import string
import random

app = Bottle()

DATABASE = 'urls.db'


def generate_short_url():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))


def create_short_url(long_url):
    short_url = generate_short_url()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO urls (short_url, long_url) VALUES (?, ?)", (short_url, long_url))
    conn.commit()
    conn.close()
    return short_url


def get_long_url(short_url):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT long_url FROM urls WHERE short_url=?", (short_url,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

@app.route('/init')
def init_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS urls (short_url TEXT PRIMARY KEY, long_url TEXT)")
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return template('templates/short_url.html')


@app.route('/shorten', method='GET')
def shorten():
    long_url = request.query.get('url')
    if long_url:
        short_url = create_short_url(long_url)
        return 'http://' + request.headers.get('Host') + '/short_url/' + short_url
    else:
        return "Invalid URL"


@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    long_url = get_long_url(short_url)
    if long_url:
        redirect(long_url)
    else:
        response.status = 404
        return "Short URL not found"
