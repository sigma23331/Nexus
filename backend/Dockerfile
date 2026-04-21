FROM python:3.10-slim
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 flaskuser && chown -R flaskuser:flaskuser /app
USER flaskuser

# 暴露端口
EXPOSE 5000

# 运行应用 - 使用新的main.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]