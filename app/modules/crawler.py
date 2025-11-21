"""
DC인사이드 미국주식 갤러리 크롤러
- 개념글 위주로 제목/본문/추천수/댓글 수집
- MongoDB에 Upsert로 중복 방지
"""

import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 상수 설정
GALLERY_ID = "us_stocks"  # DC인사이드 미국주식 갤러리 ID
BASE_URL = f"https://gall.dcinside.com/mgallery/board/lists"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}


def get_mongo_client() -> MongoClient:
    """MongoDB 클라이언트 생성"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # 연결 테스트
        client.admin.command('ping')
        logger.info(f"✅ MongoDB 연결 성공: {mongo_uri}")
        return client
    except Exception as e:
        logger.error(f"❌ MongoDB 연결 실패: {e}")
        raise


def get_post_list(page: int = 1, recommend_only: bool = True) -> List[Dict]:
    """
    갤러리 게시글 목록 크롤링
    
    Args:
        page: 페이지 번호
        recommend_only: True면 개념글만, False면 전체글
    
    Returns:
        게시글 정보 리스트 [{'post_id', 'title', 'author', 'date', 'views', 'recommend'}]
    """
    params = {
        'id': GALLERY_ID,
        'page': page,
    }
    
    # 개념글만 보기 (추천수 기준)
    if recommend_only:
        params['recommend'] = '1'
    
    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        posts = []
        
        # 게시글 테이블에서 tr.ub-content 추출
        rows = soup.select('tr.ub-content')
        
        for row in rows:
            try:
                # 공지글 제외
                if 'notice' in row.get('class', []):
                    continue
                
                # 게시글 번호 추출
                num_cell = row.select_one('td.gall_num')
                if not num_cell or not num_cell.text.strip().isdigit():
                    continue
                
                post_id = num_cell.text.strip()
                
                # 제목 추출
                title_elem = row.select_one('td.gall_tit a')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                # 작성자
                author_elem = row.select_one('td.gall_writer')
                author = author_elem.get('data-nick', '익명') if author_elem else '익명'
                
                # 날짜
                date_elem = row.select_one('td.gall_date')
                date_str = date_elem.get('title', '') if date_elem else ''
                
                # 조회수
                views_elem = row.select_one('td.gall_count')
                views = int(views_elem.text.strip()) if views_elem and views_elem.text.strip().isdigit() else 0
                
                # 추천수
                recommend_elem = row.select_one('td.gall_recommend')
                recommend = int(recommend_elem.text.strip()) if recommend_elem and recommend_elem.text.strip().isdigit() else 0
                
                posts.append({
                    'post_id': post_id,
                    'title': title,
                    'author': author,
                    'date': date_str,
                    'views': views,
                    'recommend': recommend,
                })
                
            except Exception as e:
                logger.warning(f"게시글 파싱 실패: {e}")
                continue
        
        logger.info(f"📄 페이지 {page}: {len(posts)}개 게시글 수집")
        return posts
        
    except requests.RequestException as e:
        logger.error(f"❌ 페이지 {page} 요청 실패: {e}")
        return []


def get_post_detail(post_id: str) -> Optional[Dict]:
    """
    게시글 본문 크롤링
    
    Args:
        post_id: 게시글 번호
    
    Returns:
        {'post_id', 'title', 'author', 'content', 'images', 'comments'}
    """
    url = f"https://gall.dcinside.com/mgallery/board/view"
    params = {
        'id': GALLERY_ID,
        'no': post_id,
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 제목
        title_elem = soup.select_one('span.title_subject')
        title = title_elem.text.strip() if title_elem else ''
        
        # 작성자
        author_elem = soup.select_one('div.gall_writer')
        author = author_elem.get('data-nick', '익명') if author_elem else '익명'
        
        # 본문 (HTML 태그 제거)
        content_elem = soup.select_one('div.write_div')
        if content_elem:
            # 이미지 태그 제거하고 텍스트만 추출
            for img in content_elem.find_all('img'):
                img.decompose()
            content = content_elem.get_text(separator='\n', strip=True)
        else:
            content = ''
        
        # 이미지 URL 수집
        images = []
        if content_elem:
            for img in soup.select('div.write_div img'):
                src = img.get('src', '')
                if src and src.startswith('http'):
                    images.append(src)
        
        # 댓글 수집 (간단히 댓글 내용만)
        comments = []
        comment_elems = soup.select('li.ub-content')
        for comment in comment_elems[:10]:  # 최대 10개만
            comment_text_elem = comment.select_one('p.usertxt')
            if comment_text_elem:
                comments.append(comment_text_elem.text.strip())
        
        logger.info(f"📝 게시글 {post_id} 본문 수집 완료 (본문 {len(content)}자, 댓글 {len(comments)}개)")
        
        return {
            'post_id': post_id,
            'title': title,
            'author': author,
            'content': content,
            'images': images,
            'comments': comments,
        }
        
    except requests.RequestException as e:
        logger.error(f"❌ 게시글 {post_id} 요청 실패: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ 게시글 {post_id} 파싱 실패: {e}")
        return None


def save_to_mongodb(posts: List[Dict], db_name: str = None) -> int:
    """
    크롤링한 게시글을 MongoDB에 저장 (Upsert)
    
    Args:
        posts: 저장할 게시글 리스트
        db_name: 데이터베이스 이름
    
    Returns:
        저장된 게시글 수
    """
    if not posts:
        return 0
    
    db_name = db_name or os.getenv('MONGO_DB_NAME', 'shorts_factory')
    
    try:
        client = get_mongo_client()
        db = client[db_name]
        collection = db['posts']
        
        saved_count = 0
        for post in posts:
            # post_id를 기준으로 Upsert
            post['crawled_at'] = datetime.now()
            result = collection.update_one(
                {'post_id': post['post_id']},
                {'$set': post},
                upsert=True
            )
            if result.upserted_id or result.modified_count > 0:
                saved_count += 1
        
        logger.info(f"💾 MongoDB 저장 완료: {saved_count}개 (전체 {len(posts)}개)")
        return saved_count
        
    except Exception as e:
        logger.error(f"❌ MongoDB 저장 실패: {e}")
        return 0


def crawl_gallery(pages: int = 3, delay: float = 2.0, save_to_db: bool = True) -> List[Dict]:
    """
    갤러리 크롤링 메인 함수
    
    Args:
        pages: 크롤링할 페이지 수
        delay: 페이지 간 대기 시간 (초)
        save_to_db: MongoDB 저장 여부
    
    Returns:
        크롤링한 전체 게시글 리스트
    """
    logger.info(f"🚀 크롤링 시작: {pages}페이지, 지연 {delay}초")
    
    all_posts = []
    
    # 1단계: 게시글 목록 수집
    for page in range(1, pages + 1):
        posts = get_post_list(page=page, recommend_only=True)
        
        # 2단계: 각 게시글 본문 수집
        for post in posts:
            time.sleep(delay)  # 서버 부하 방지
            
            detail = get_post_detail(post['post_id'])
            if detail:
                # 목록 정보와 본문 정보 병합
                merged = {**post, **detail}
                all_posts.append(merged)
        
        time.sleep(delay)  # 페이지 간 대기
    
    logger.info(f"✅ 크롤링 완료: 총 {len(all_posts)}개 게시글")
    
    # MongoDB 저장
    if save_to_db:
        save_to_mongodb(all_posts)
    
    return all_posts


if __name__ == '__main__':
    # 테스트 실행
    crawl_gallery(pages=2, delay=1.5)

