"""
DC 인사이드 크롤링 로직만 담당
나중에 naver 뉴스, reddit 등등 추가 가능

해당 파일에서는 DC인사이드 목록에 대한 크롤링 담당
"""

import requests
import logging

from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from .constants import GALLERY_ID, BASE_URL, HEADERS

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 갤러리 게시글 목록 크롤링
def get_post_list(page: int=1, recommend_only: bool = True) -> List[Dict]:
    """

    Args:
        page: 페이지 번호
        recommend_only: True면 개념글만, False면 전체글

    Returns:
        게시글 정보 리스트 [{'post_id', 'title', 'author', 'date', 'views', 'recommend'}]
    """

    params = {
        'id' : GALLERY_ID,
        'page' : page,
    }

    # 개념글만 확인 (추천수 기준)
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
