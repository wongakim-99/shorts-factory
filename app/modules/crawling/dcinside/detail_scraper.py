"""
DC 인사이드 크롤링 로직만 담당
나중에 naver 뉴스, reddit 등등 추가 가능

해당 파일에서는 DC인사이드 상세 목록(detail)에 대한 크롤링 담당
"""

import logging
import requests

from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from .constants import GALLERY_ID, BASE_URL, HEADERS

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 갤러리 게시글 디테일 크롤링
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

    except requests.RequestException as e:  # 게시글 요청에 대한 실패에 대한 예외처리
        logger.error(f"❌ 게시글 {post_id} 요청 실패: {e}")
        return None

    except Exception as e:  # 게시글 파싱 실패에 대한 예외처리
        logger.error(f"❌ 게시글 {post_id} 파싱 실패: {e}")
        return None