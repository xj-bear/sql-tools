FROM python:3.9-slim-buster

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libsasl2-dev \
    libsasl2-modules \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip/*

# 创建必要的目录
RUN mkdir -p /app/data /app/swagger

# 复制应用代码
COPY app/database.py app/main.py app/utils.py ./

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# 创建非root用户
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]