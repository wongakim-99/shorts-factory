# 🧪 Tests

Shorts Factory 테스트 스크립트 모음

## 📂 디렉토리 구조

```
tests/
├── integration/           # 통합 테스트
│   └── test_mongo.py     # MongoDB 연결 테스트
├── crawling/             # 크롤링 모듈 테스트
│   └── test_selenium_comments.py  # Selenium 댓글 크롤링 테스트
├── llm/                  # LLM 모듈 테스트
│   └── test_gemini.py    # Gemini API 및 대본 생성 테스트
└── video/                # 영상 제작 모듈 테스트
    └── test_pymovie.py   # MoviePy 영상 생성 테스트
```

## 테스트 목록

### 1. MongoDB 연결 테스트 (통합)

MongoDB가 정상적으로 작동하는지 확인합니다.

```bash
python3 tests/integration/test_mongo.py
```

**확인 사항:**
- MongoDB 연결 가능 여부
- 데이터 CRUD 동작
- 기존 크롤링 데이터 확인

---

### 2. 크롤링 모듈 테스트

Selenium을 사용한 댓글 크롤링 기능을 테스트합니다.

```bash
python3 tests/crawling/test_selenium_comments.py
```

---

### 3. LLM 모듈 테스트

Gemini API를 사용한 대본 생성 기능을 테스트합니다.

```bash
python3 tests/llm/test_gemini.py
```

**확인 사항:**
- Gemini API 연결
- 대본 미생성 게시글 조회
- 대본 생성 (실제 API 호출)

---

### 4. 영상 제작 모듈 테스트

MoviePy를 사용한 영상 생성 기능을 테스트합니다.

```bash
python3 tests/video/test_pymovie.py
```

**확인 사항:**
- 영상 생성 (배경 + 자막)
- 출력 위치: `app/output/videos/`

---

## 전체 테스트 실행 (예정)

```bash
python3 -m pytest tests/
```
