FROM python:3.11-slim

WORKDIR /app

# 安装 uv
RUN pip install uv --no-cache-dir

# 复制依赖文件并安装
COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml

# 复制应用代码
COPY . .

EXPOSE 8000 25

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
