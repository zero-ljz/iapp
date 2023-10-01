# iapp

``` bash
# 创建、激活虚拟环境和安装依赖
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# 启动程序
python3 -m gunicorn -w 2 -b 0.0.0.0:8000 -k gevent app:app
```

bash fast.sh create_supervisor iapp "/root/repos/iapp/.venv/bin/python3 -m gunicorn -w 2 -b 0.0.0.0:8000 -k gevent app:app" "/root/repos/iapp/"