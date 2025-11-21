# 🧪 Tests

Shorts Factory 테스트 스크립트 모음

## 테스트 목록

### 1. MongoDB 연결 테스트

MongoDB가 정상적으로 작동하는지 확인합니다.

```bash
python3 tests/test_mongo.py
```

**확인 사항:**
- MongoDB 연결 가능 여부
- 데이터 CRUD 동작
- 기존 크롤링 데이터 확인

---

### 2. 크롤러 테스트 (예정)

```bash
python3 tests/test_crawler.py
```

---

### 3. LLM Writer 테스트 (예정)

```bash
python3 tests/test_llm_writer.py
```

---

### 4. Video Maker 테스트 (예정)

```bash
python3 tests/test_video_maker.py
```

---

## 전체 테스트 실행 (예정)

```bash
python3 -m pytest tests/
```

