FROM python:3.12-slim

# 安装 ffmpeg（音频处理必需）
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建占位 .env 文件（应用要求 .env 文件必须存在；
# 实际配置通过 docker-compose environment 注入的环境变量覆盖）
RUN touch /app/.env

# 启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8010 8002 8003

ENTRYPOINT ["/entrypoint.sh"]
