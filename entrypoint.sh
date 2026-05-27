#!/bin/bash
set -e

APP_MODULE=${APP_MODULE:-Base.main:app}
APP_HOST=${APP_HOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8010}

echo ">>> AEGIS 服务启动中..."
echo ">>> 模块: ${APP_MODULE}"
echo ">>> 监听: ${APP_HOST}:${APP_PORT}"

# 等待 MySQL 就绪
if [ -n "${DB_HOST}" ]; then
    echo ">>> 等待 MySQL 就绪 (${DB_HOST}:${DB_PORT:-3306})..."
    for i in $(seq 1 60); do
        if python -c "
import pymysql
try:
    conn = pymysql.connect(
        host='${DB_HOST}',
        port=${DB_PORT:-3306},
        user='${DB_USER:-root}',
        password='${DB_PASSWORD:-}',
        charset='utf8mb4'
    )
    conn.close()
    print('OK')
except Exception:
    exit(1)
" 2>/dev/null; then
            echo ">>> MySQL 已就绪"
            break
        fi
        echo "    等待 MySQL... (${i}/60)"
        sleep 3
    done
fi

# 等待 Redis 就绪
if [ -n "${REDIS_HOST}" ]; then
    echo ">>> 等待 Redis 就绪 (${REDIS_HOST}:${REDIS_PORT:-6379})..."
    for i in $(seq 1 30); do
        if python -c "
import redis
try:
    r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT:-6379}, socket_connect_timeout=3)
    r.ping()
    print('OK')
except Exception:
    exit(1)
" 2>/dev/null; then
            echo ">>> Redis 已就绪"
            break
        fi
        echo "    等待 Redis... (${i}/30)"
        sleep 2
    done
fi

# 等待 Milvus 就绪
if [ -n "${MILVUS_HOST}" ]; then
    echo ">>> 等待 Milvus 就绪 (${MILVUS_HOST}:${MILVUS_PORT:-19530})..."
    for i in $(seq 1 30); do
        if python -c "
from pymilvus import connections
try:
    connections.connect(host='${MILVUS_HOST}', port='${MILVUS_PORT:-19530}', timeout=5)
    connections.disconnect('default')
    print('OK')
except Exception:
    exit(1)
" 2>/dev/null; then
            echo ">>> Milvus 已就绪"
            break
        fi
        echo "    等待 Milvus... (${i}/30)"
        sleep 3
    done
fi

# 等待 Neo4j 就绪
if [ -n "${NEO4J_URI}" ]; then
    echo ">>> 等待 Neo4j 就绪..."
    for i in $(seq 1 30); do
        if python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('${NEO4J_URI}', auth=('${NEO4J_USER:-neo4j}', '${NEO4J_PASSWORD:-neo4j123}'))
    driver.verify_connectivity()
    driver.close()
    print('OK')
except Exception:
    exit(1)
" 2>/dev/null; then
            echo ">>> Neo4j 已就绪"
            break
        fi
        echo "    等待 Neo4j... (${i}/30)"
        sleep 3
    done
fi

echo ">>> 所有依赖服务已就绪，启动应用..."
exec python -m uvicorn ${APP_MODULE} --host ${APP_HOST} --port ${APP_PORT} --log-level info
