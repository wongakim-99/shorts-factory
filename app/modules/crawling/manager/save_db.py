# 크롤링한 게시글 저장 로직
import os
import logging

from typing import List, Dict
from datetime import datetime

from app.modules.crawling.manager.connection_db import get_mongo_client

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_posts(posts: List[Dict], db_name: str = None) -> int:
    """
    크롤링한 게시글을 MongoDB 에 저장 (Upsert)

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

        logger.info("=" * 60)
        logger.info("💾 MongoDB Save Status")
        logger.info(f"   Saved Count: {saved_count}")
        logger.info(f"   Total Count: {len(posts)}")
        logger.info(f"   Database: {db_name}")
        logger.info(f"   Collection: posts")
        logger.info("=" * 60)
        return saved_count

    except Exception as e:
        logger.error(f"❌ MongoDB 저장 실패: {e}")
        return 0
