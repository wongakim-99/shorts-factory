# 몽고 DB 연결

import os
import logging

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


def get_mongo_client() -> MongoClient:
    """MongoDB 클라이언트 생성"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # 연결 테스트
        client.admin.command('ping')
        logger.info("=" * 60)
        logger.info("🔌  MongoDB Connection Status")
        logger.info(f"   URI: {mongo_uri}")
        logger.info(f"   Status: ✅ MongoDB Connected Successfully")
        logger.info("=" * 60)
        return client
    except Exception as e:
        logger.error("=" * 60)
        logger.error("🔌  MongoDB Connection Status")
        logger.error(f"   URI: {mongo_uri}")
        logger.error(f"   Status: ❌ MongoDB Connection Failed")
        logger.error(f"   Error: {e}")
        logger.error("=" * 60)
        raise