FROM python:3.10-slim
WORKDIR /app

# 使用国内 Debian 镜像源（兼容 deb822 新格式与旧 sources.list）
RUN (sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g; s|http://security.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/*.sources 2>/dev/null || true) \
 && (sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g; s|http://security.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true)

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（优先清华镜像，失败自动回退官方源）
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --retries 2 --timeout 30 \
    || pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.org/simple \
    --retries 5 --timeout 60

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 flaskuser && chown -R flaskuser:flaskuser /app
USER flaskuser

# 暴露端口
EXPOSE 5000

# 运行应用 - 使用新的main.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
