"""
Shorts Factory - 애플리케이션 핵심 로직

실행은 프로젝트 루트의 main.py를 사용하세요:
    python3 main.py
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.crawling.crawler_main import crawl_gallery


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🎬 Shorts Factory - 경제 쇼츠 자동 생성 시스템")
    print("=" * 60)
    print()
    
    # Phase 1: 데이터 수집
    print("📡 [Phase 1] 데이터 크롤링 시작...")
    try:
        posts = crawl_gallery(
            pages=int(os.getenv('CRAWL_PAGES', 3)),
            delay=float(os.getenv('CRAWL_DELAY', 2.0)),
            save_to_db=True
        )
        print(f"✅ 크롤링 완료: {len(posts)}개 게시글 수집")
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        return
    
    # Phase 2: 대본 작성 (추후 구현)
    print()
    print("✍️  [Phase 2] LLM 대본 작성... (미구현)")
    
    # Phase 3: 영상 생성 (추후 구현)
    print()
    print("🎥 [Phase 3] 영상 생성... (미구현)")
    
    print()
    print("=" * 60)
    print("🎉 프로세스 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()
