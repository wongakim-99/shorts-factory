"""
Shorts Factory - 애플리케이션 핵심 로직

실행은 프로젝트 루트의 main.py를 사용하세요:
    python3 main.py
"""

import os
import sys
import logging

from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.crawling.crawler_main import crawl_gallery
from modules.llm.llm_writer import generate_scripts_batch

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """메인 실행 함수"""
    logger.info("=" * 60)
    logger.info("🎬 Shorts Factory - 경제 쇼츠 자동 생성 시스템")
    logger.info("=" * 60)
    logger.info("")  # 빈 줄
    
    # Phase 1: 데이터 수집
    logger.info("📡 [Phase 1] 데이터 크롤링 시작...")
    try:
        # 환경변수에서 설정 읽기
        max_posts = os.getenv('MAX_POSTS')  # None이면 제한 없음
        max_posts = int(max_posts) if max_posts else None
        cleanup_days = int(os.getenv('IMAGE_CLEANUP_DAYS', 7))
        
        posts = crawl_gallery(
            pages=int(os.getenv('CRAWL_PAGES', 1)),
            delay=float(os.getenv('CRAWL_DELAY', 2.0)),
            save_to_db=True,
            max_posts=max_posts,
            cleanup_days=cleanup_days
        )
        logger.info(f"✅ 크롤링 완료: {len(posts)}개 게시글 수집")
    except Exception as e:
        logger.error(f"❌ 크롤링 실패: {e}")
        return
    
    # Phase 2: 대본 작성
    logger.info("")  # 빈 줄
    logger.info("✍️  [Phase 2] LLM 대본 작성 시작...")
    try:
        # 환경변수에서 생성할 대본 수 읽기 (기본값: 5)
        script_limit = int(os.getenv('SCRIPT_LIMIT', 5))
        
        script_count = generate_scripts_batch(limit=script_limit)
        logger.info(f"✅ 대본 생성 완료: {script_count}개 대본 생성")
    except Exception as e:
        logger.error(f"❌ 대본 생성 실패: {e}")
        # 대본 생성 실패해도 계속 진행
    
    # Phase 3: 영상 생성 (추후 구현)
    logger.info("")  # 빈 줄
    logger.info("🎥 [Phase 3] 영상 생성... (미구현)")
    
    logger.info("")  # 빈 줄
    logger.info("=" * 60)
    logger.info("🎉 프로세스 완료!")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
