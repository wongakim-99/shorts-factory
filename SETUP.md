# 🚀 Shorts Factory 설치 및 실행 가이드

## 1. 환경 요구사항

- **OS:** macOS (Apple Silicon / Intel)
- **Python:** 3.10 이상
- **Docker:** MongoDB 실행용
- **Homebrew:** ImageMagick 설치용

---

## 2. 설치 단계

### 2-1. Python 가상환경 생성 및 활성화

```bash
cd shorts-factory
python3 -m venv venv
source venv/bin/activate
```

### 2-2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2-3. ImageMagick 설치 (영상 생성용)

```bash
brew install imagemagick
```

### 2-4. MongoDB Docker 실행

```bash
# MongoDB 컨테이너 실행
docker run -d \
  --name mongodb-shorts \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0

# 실행 확인
docker ps | grep mongodb-shorts
```

---

## 3. 환경변수 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
# MongoDB 설정
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=shorts_factory

# Anthropic API Key (Claude)
ANTHROPIC_API_KEY=sk-ant-...여기에_실제_키_입력

# 크롤링 설정
CRAWL_PAGES=3
CRAWL_DELAY=2
```

---

## 4. 실행

### 전체 파이프라인 실행

```bash
python3 main.py
```

### 개별 모듈 테스트

```bash
# 크롤러만 실행
cd app && python3 modules/crawler_main.py
```

---

## 5. 테스트 실행

### MongoDB 연결 테스트

```bash
python3 tests/test_mongo.py
```

### MongoDB 데이터 직접 확인

```bash
# MongoDB Shell 접속
docker exec -it mongodb-shorts mongosh

# 데이터베이스 선택
use shorts_factory

# 수집된 게시글 확인
db.posts.find().limit(5)
```

---

## 6. 문제 해결

### MongoDB 연결 실패

```bash
# MongoDB 컨테이너 재시작
docker restart mongodb-shorts
```

### 크롤링 차단

- DC인사이드가 차단할 경우, `CRAWL_DELAY`를 늘려보세요 (예: 5초)
- User-Agent를 변경해보세요

### ImageMagick 오류

```bash
# 설치 확인
which convert

# 환경변수 확인
export IMAGEMAGICK_BINARY=$(which convert)
```

---

## 7. 디렉토리 구조

```
shorts-factory/
├── app/              # 애플리케이션 코드
│   ├── modules/      # 핵심 로직
│   │   ├── crawler.py    # 크롤러
│   │   ├── llm_writer.py # 대본 작성 (예정)
│   │   └── video_maker.py # 영상 생성 (예정)
│   ├── assets/       # 리소스
│   │   ├── video/    # 배경 영상
│   │   ├── fonts/    # 폰트 파일
│   │   └── audio/    # 배경음악
│   ├── output/       # 생성된 영상
│   └── core.py       # 앱 핵심 로직
├── tests/            # 테스트 코드
│   └── test_mongo.py # MongoDB 연결 테스트
├── main.py           # 🚀 실행 진입점
├── requirements.txt  # 패키지 목록
└── .env              # 환경변수 (직접 생성)
```

