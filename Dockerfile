# Shorts Factory - Python 애플리케이션 Dockerfile
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 및 Chromium 설치 (ARM64/AMD64 모두 지원)
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 진입점 설정
CMD ["python", "main.py"]

