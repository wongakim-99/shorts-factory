"""
크롤링 메인 오케스트레이터

DC인사이드 크롤링 + MongoDB 저장을 조율하는 메인 함수
"""

import time
import logging
from typing import List, Dict
from dotenv import load_dotenv

# 분리된 모듈들 import (동일 패키지 내 상대 경로)
from .dcinside.list_scraper import get_post_list
from .dcinside.detail_scraper import get_post_detail, cleanup_old_images
from .manager.save_db import save_posts

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def crawl_gallery(pages: int = 1, delay: float = 2.0, save_to_db: bool = True, max_posts: int = None, cleanup_days: int = 7) -> List[Dict]:
    """
    갤러리 크롤링 메인 함수
    
    Args:
        pages: 크롤링할 페이지 수
        delay: 페이지 간 대기 시간 (초)
        save_to_db: MongoDB 저장 여부
        max_posts: 최대 크롤링 게시글 수 (None이면 제한 없음)
        cleanup_days: 이미지 보관 기간 (일). 0이면 정리 안 함
    
    Returns:
        크롤링한 전체 게시글 리스트
    """
    logger.info(f"🚀 크롤링 시작: {pages}페이지, 지연 {delay}초" + (f", 최대 {max_posts}개" if max_posts else ""))
    
    # 오래된 이미지 자동 정리
    if cleanup_days > 0:
        cleanup_old_images(keep_days=cleanup_days)
    
    all_posts = []
    
    # 1단계: 게시글 목록 수집
    for page in range(1, pages + 1):
        posts = get_post_list(page=page, recommend_only=True)
        
        # 2단계: 각 게시글 본문 수집
        for post in posts:
            # 최대 게시글 수 체크
            if max_posts and len(all_posts) >= max_posts:
                logger.info(f"⏹️ 최대 게시글 수({max_posts}개) 도달, 크롤링 중단")
                break
            
            time.sleep(delay)  # 서버 부하 방지
            
            detail = get_post_detail(post['post_id'])
            if detail:
                # 목록 정보와 본문 정보 병합
                merged = {**post, **detail}
                all_posts.append(merged)
        
        # 최대 게시글 수 도달 시 페이지 루프도 중단
        if max_posts and len(all_posts) >= max_posts:
            break
        
        time.sleep(delay)  # 페이지 간 대기
    
    logger.info(f"✅ 크롤링 완료: 총 {len(all_posts)}개 게시글")
    
    # MongoDB 저장
    if save_to_db:
        save_posts(all_posts)
    
    return all_posts


if __name__ == '__main__':
    # 테스트 실행
    crawl_gallery(pages=2, delay=1.5)
