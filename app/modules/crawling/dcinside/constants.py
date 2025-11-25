"""
크롤링 관련 상수 정의
"""

# 상수 설정
GALLERY_ID = "us_stocks"  # DC인사이드 미국주식 갤러리 ID
BASE_URL = f"https://gall.dcinside.com/mgallery/board/lists"

# 헤더 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

# 크롤링 설정
DEFAULT_DELAY = 2.0
MAX_RETRY = 3
TIMEOUT = 10