"""
역할: 대본 미생성 게시글 조회 및 생성된 대본을 MongoDB 에 저장
포함 내용:
- MongoDB에서 script 필드가 없는 게시글 조회
- posts 컬렉션의 해당 게시글에 script 필드 업데이트
"""

import logging
import os

from typing import List, Dict
from datetime import datetime

from app.modules.crawling.manager.connection_db import get_mongo_client

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_posts_without_script(db_name: str = None, limit: int = 10) -> List[Dict]:
    """
    아직 대본이 생성되지 않은 게시글을 MongoDB에서 가져오기

    Args:
        db_name: 데이터베이스 이름
        limit: 가져올 최대 게시글 수

    Returns:
        게시글 리스트
    """
    db_name = db_name or os.getenv('MONGO_DB_NAME', 'shorts_factory')

    try:
        client = get_mongo_client()
        db = client[db_name]
        collection = db['posts']

        # script 필드가 없는 게시글만 가져오기 (추천수 높은 순)
        posts = list(collection.find(
            {'script': {'$exists': False}},
            limit=limit
        ).sort('recommend_count', -1))

        logger.info("=" * 60)
        logger.info("📚 대본 미생성 게시글 조회")
        logger.info(f"   조회된 게시글 수: {len(posts)}")
        logger.info(f"   Database: {db_name}")
        logger.info("=" * 60)

        return posts

    except Exception as e:
        logger.error(f"❌ 게시글 조회 실패: {e}")
        return []


def save_script_to_db(post_id: str, script_data: Dict, db_name: str = None) -> bool:
    """
    생성된 대본을 MongoDB 에 저장

    Args:
        post_id: 게시글 ID
        script_data: 생성된 대본 데이터
        db_name: 데이터베이스 이름

    Returns:
        성공 여부
    """
    db_name = db_name or os.getenv('MONGO_DB_NAME', 'shorts_factory')

    try:
        client = get_mongo_client()
        db = client[db_name]
        collection = db['posts']

        # post_id로 해당 게시글을 찾아서 script 필드 업데이트
        result = collection.update_one(
            {'post_id': post_id},
            {'$set': {
                'script': script_data,
                'script_generated_at': datetime.now()
            }}
        )

        if result.modified_count > 0:
            logger.info(f"✅ 대본 저장 완료: {post_id}")
            return True
        else:
            logger.warning(f"⚠️ 대본 저장 실패 (게시글을 찾을 수 없음): {post_id}")
            return False

    except Exception as e:
        logger.error(f"❌ 대본 저장 실패: {e}")
        return False