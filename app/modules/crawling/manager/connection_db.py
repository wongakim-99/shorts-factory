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
        logger.info(f"✅ MongoDB 연결 성공: {mongo_uri}")
        return client
    except Exception as e:
        logger.error(f"❌ MongoDB 연결 실패: {e}")
        raise