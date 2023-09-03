FROM python:3.11.2-bullseye
ADD . /server
RUN python3 -m pip install --upgrade pip -i https://pypi.douban.com/simple/ 
RUN pip3 install -r /server/deploy/requirements.txt -i https://pypi.douban.com/simple/

#设置时区
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone

# 80 port
EXPOSE 80

# docker启动运行默认命令
WORKDIR /server
CMD ["uvicorn", "src.main:app","--host", "0.0.0.0", "--port", "80","--workers", "1", "--access-log", "--use-colors"]