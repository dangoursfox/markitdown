# 使用轻量级 Python 镜像
FROM python:3.13-slim

# 设置环境变量，减少交互和缓存
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安装必要的系统运行时依赖 (ffmpeg 用于音频，exiftool 用于元数据)
# 清理缓存以缩小镜像体积
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    exiftool \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制 markitdown 源代码
# 注意：在构建时需要选择项目根目录作为上下文
COPY packages /app/packages

# 安装 markitdown 及所有扩展依赖
RUN pip install --no-cache-dir /app/packages/markitdown[all]

# 安装 Web 服务相关依赖
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# 复制 Web 包装代码
COPY web_app /app/web_app

# 创建并使用非 root 用户以增强安全性 (NAS 部署推荐)
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# 设置临时目录环境变量，确保临时文件有据可查
ENV TMPDIR=/tmp

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 启动命令：使用主程序运行，内部已配置 uvicorn 优化参数
CMD ["python", "web_app/main.py"]
