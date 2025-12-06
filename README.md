# 🎬 Shorts Factory

> DC인사이드 주식 갤러리 데이터 기반 경제 쇼츠 자동 생성 시스템

## 1. 프로젝트 개요

주식 커뮤니티 여론을 분석하여 시청자의 공포와 호기심을 자극하는 **'나비효과 경제 분석'** 쇼츠 영상을 자동으로 생성합니다.

## 2. 주요 기능

-  **자동 크롤링**: DC인사이드 미국주식 갤러리 개념글 수집
-  **AI 대본 작성**: Gemini 1.5 Pro로 시니컬한 경제 분석 대본 생성
-  **자동 영상 편집**: MoviePy 기반 쇼츠 영상 생성 (자막, 배경음악, TTS)

## 3. 기술 스택

- **Language**: Python 3.10+
- **Database**: MongoDB (Docker)
- **Crawler**: BeautifulSoup4, Requests
- **LLM**: Google Gemini 1.5 Pro
- **Video**: MoviePy, ImageMagick

## 4. 빠른 시작

자세한 설치 및 실행 방법은 [SETUP.md](SETUP.md)를 참고하세요.

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. MongoDB 실행
docker run -d -p 27017:27017 --name mongodb-shorts mongo:7.0

# 3. 환경변수 설정
cp env.template .env  # 그리고 API 키 입력

# 4. MongoDB 연결 테스트
python3 tests/test_mongo.py

# 5. Gemini API 테스트
python3 tests/test_gemini.py

# 6. 실행
python3 main.py
```

## 📂 프로젝트 구조

```
shorts-factory/
├── app/              # 애플리케이션 코드
│   ├── modules/      # 핵심 모듈
│   │   ├── crawling/     # 1. 크롤링 모듈
│   │   ├── llm/          # 2. LLM 대본 생성
│   │   └── video/        # 3. 영상 제작 (예정)
│   ├── assets/       # 리소스 (배경 영상, 폰트, 음악)
│   │   ├── video/    # 배경 영상 (bull.mp4, bear.mp4)
│   │   ├── fonts/    # 폰트 파일
│   │   └── audio/    # 배경음악
│   ├── output/       # 출력 파일
│   │   ├── images/   # 크롤링 이미지 (날짜별 폴더)
│   │   └── videos/   # 생성된 영상 (추후 구현)
│   └── core.py       # 앱 핵심 로직
├── tests/            # 테스트 코드
│   └── test_mongo.py # MongoDB 연결 테스트
├── main.py           # 실행 진입점
└── requirements.txt  # 패키지 목록
```

## 📖 문서

- [프로젝트 청사진](PROJECT_BLUEPRINT.md)
- [설치 가이드](SETUP.md)
- [개발 규칙](.cursorrules)

## 📝 라이선스

MIT License
