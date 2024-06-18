# 如需更多资料，请参阅 https://aka.ms/vscode-docker-python
FROM python:3.10.11-alpine

EXPOSE 8000

# 防止Python在容器中生成.pyc文件
# ENV PYTHONDONTWRITEBYTECODE=1

# 关闭缓冲以便更容易地记录容器日志
# ENV PYTHONUNBUFFERED=1

# 安装 pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
# RUN apt update && apt -y install nano curl nodejs npm tree zip unzip
# 设置时区
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache tzdata bash && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata && \
    rm -rf /var/cache/apk/*

WORKDIR /app
COPY . /app

# 创建具有显式 UID 的非root用户并添加访问 /app 文件夹的权限
# 如需更多资料，请参阅 https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# 在调试期间，这个入口点将被覆盖。 如需更多资料，请参阅 https://aka.ms/vscode-docker-python-debug
CMD ["bash", "-c", "python -m gunicorn -w 2 -b 0.0.0.0:8000 -k gevent app:app"]