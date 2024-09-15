# 使用官方的 Python 镜像作为基础镜像
FROM python:3.10.13

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录
COPY . /app

# 设置清华镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 启动 FastAPI 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]