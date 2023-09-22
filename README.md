# iapp

``` bash
# 创建虚拟环境和安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# 启动程序
python3 -m gunicorn -w 2 -b 0.0.0.0:8000 -k gevent app:app
```

bash fast.sh create_supervisor iapp "./.venv/bin/python3 -m gunicorn -w 2 -b 0.0.0.0:8000 -k gevent app:app" "/root/repos/iapp/"