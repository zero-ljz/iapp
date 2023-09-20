# iapp

``` bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 -m gunicorn -w 1 -b 0.0.0.0:8000 -k gevent app:app
```