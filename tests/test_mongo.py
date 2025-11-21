"""
MongoDB 연결 테스트 스크립트
Docker MongoDB가 정상 작동하는지 확인

Usage:
    python3 tests/test_mongo.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def test_mongodb_connection():
    """MongoDB 연결 및 기본 동작 테스트"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB_NAME', 'shorts_factory')
    
    print("=" * 60)
    print("🔍 MongoDB 연결 테스트")
    print("=" * 60)
    print(f"URI: {mongo_uri}")
    print(f"Database: {db_name}")
    print()
    
    try:
        # 연결
        print("📡 MongoDB 연결 중...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Ping 테스트
        client.admin.command('ping')
        print("✅ 연결 성공!")
        print()
        
        # 데이터베이스 정보
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"📚 기존 컬렉션: {collections if collections else '(없음)'}")
        print()
        
        # 테스트 데이터 삽입
        print("💾 테스트 데이터 삽입 중...")
        test_collection = db['test']
        result = test_collection.insert_one({
            'test': True,
            'message': 'MongoDB 연결 테스트 성공!'
        })
        print(f"✅ 삽입 완료! ID: {result.inserted_id}")
        print()
        
        # 데이터 조회
        print("🔎 데이터 조회 중...")
        doc = test_collection.find_one({'test': True})
        print(f"✅ 조회 성공: {doc}")
        print()
        
        # 테스트 데이터 삭제
        print("🗑️  테스트 데이터 삭제 중...")
        test_collection.delete_many({'test': True})
        print("✅ 삭제 완료!")
        print()
        
        # posts 컬렉션 정보
        if 'posts' in collections:
            posts_count = db['posts'].count_documents({})
            print(f"📊 저장된 게시글 수: {posts_count}개")
            
            if posts_count > 0:
                latest = db['posts'].find_one(sort=[('crawled_at', -1)])
                print(f"📝 최근 게시글: {latest.get('title', 'N/A')}")
        else:
            print("ℹ️  아직 크롤링된 게시글이 없습니다.")
        
        print()
        print("=" * 60)
        print("🎉 모든 테스트 통과!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 테스트 실패!")
        print("=" * 60)
        print(f"오류: {e}")
        print()
        print("💡 해결 방법:")
        print("1. Docker가 실행 중인지 확인: docker ps")
        print("2. MongoDB 컨테이너 실행:")
        print("   docker run -d -p 27017:27017 --name mongodb-shorts mongo:7.0")
        print("3. .env 파일의 MONGO_URI 확인")
        print()


if __name__ == '__main__':
    test_mongodb_connection()

