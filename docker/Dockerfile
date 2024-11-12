FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libsasl2-dev \
    libsasl2-modules \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码和测试文件
COPY app/ .
COPY tests/ ./tests/
COPY run_tests.sh .

# 给测试脚本添加执行权限
RUN chmod +x run_tests.sh

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 使用环境变量启动服务
CMD gunicorn main:app \
    --workers ${WORKERS:-4} \
    --threads ${THREADS:-2} \
    --timeout ${TIMEOUT:-120} \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 