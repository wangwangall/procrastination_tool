FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip setuptools_rust && pip install -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p data/reports

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "app:app"]