FROM python:3.11-slim
LABEL authors="lhy"

# 设置工作目录
WORKDIR /app 



RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \          
    python3-dev \ 
    && rm -rf /var/lib/apt/lists/*   


# 安装依赖
COPY  requirement.txt . 
RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirement.txt

# 复制应用代码
COPY . .

EXPOSE 8000

RUN python manage.py makemigrations
RUN python manage.py migrate

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]