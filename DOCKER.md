# 🐳 Docker 사용 가이드

Shorts Factory를 Docker로 실행하는 방법입니다.

## 🚀 빠른 시작

### 1. 환경변수 설정

```bash
cp env.template .env
# .env 파일 편집해서 API 키 입력
```

### 2. Docker Compose로 실행

```bash
# 모든 서비스 실행 (MongoDB + Python 앱)
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f app
```

### 3. 중지

```bash
docker-compose down

# 데이터까지 삭제하려면
docker-compose down -v
```

## 📋 주요 명령어

### 서비스 관리

```bash
# 실행
docker-compose up -d

# 중지
docker-compose stop

# 재시작
docker-compose restart

# 상태 확인
docker-compose ps

# 로그 보기
docker-compose logs app
docker-compose logs mongodb
```

### 개발 모드 (코드 수정 즉시 반영)

```bash
# 개발용 compose 파일 사용
docker-compose -f docker-compose.dev.yml up
```

### 개별 서비스 실행

```bash
# MongoDB만 실행
docker-compose up mongodb

# 앱만 재시작
docker-compose restart app
```

## 🔍 문제 해결

### MongoDB 연결 확인

```bash
# MongoDB 컨테이너 접속
docker-compose exec mongodb mongosh

# 앱 컨테이너에서 MongoDB 연결 테스트
docker-compose exec app python tests/test_mongo.py
```

### 로그 확인

```bash
# 모든 로그
docker-compose logs

# 앱 로그만
docker-compose logs app

# 실시간 로그
docker-compose logs -f app
```

### 컨테이너 재빌드

```bash
# 코드 변경 후 재빌드
docker-compose build app
docker-compose up -d app
```

## 📊 구조

```
docker-compose.yml
├── mongodb (포트 27017)
│   └─ 데이터 영구 저장 (volume)
│
└── app (Python 애플리케이션)
    ├─ 코드 볼륨 마운트 (개발 편의)
    └─ MongoDB에 자동 연결
```

## 🔧 환경변수

`.env` 파일에서 설정:

```env
MONGO_URI=mongodb://mongodb:27017/  # 컨테이너 이름 사용!
MONGO_DB_NAME=shorts_factory
ANTHROPIC_API_KEY=your_key_here
CRAWL_PAGES=3
CRAWL_DELAY=2
```

## 💡 팁

### 개발 시

```bash
# 코드 수정 즉시 반영 (볼륨 마운트)
docker-compose -f docker-compose.dev.yml up
```

### 프로덕션 배포 시

```bash
# 표준 compose 사용
docker-compose up -d
```

## 🎯 vs 로컬 실행

| 항목 | 로컬 실행 | Docker 실행 |
|------|----------|------------|
| **환경 일관성** | 낮음 | 높음 ✅ |
| **설정 복잡도** | 낮음 | 중간 |
| **개발 속도** | 빠름 | 중간 (볼륨 마운트 시 빠름) |
| **배포** | 어려움 | 쉬움 ✅ |

