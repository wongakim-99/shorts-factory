# Gemini API를 사용한 영상 대본 생성 모듈 (Orchestrator)

import logging
import time

from app.modules.llm.client.gemini_client import init_gemini_api
from app.modules.llm.generator.script_generator import generate_script_with_gemini
from app.modules.llm.repository.script_repository import fetch_posts_without_script, save_script_to_db

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_scripts_batch(limit: int = 5) -> int:
    """
    여러 게시글에 대해 대본을 일괄 생성
    
    Args:
        limit: 생성할 대본 수
        
    Returns:
        성공적으로 생성된 대본 수
    """
    logger.info("=" * 60)
    logger.info("🤖 Gemini 대본 생성 시작")
    logger.info("=" * 60)
    
    try:
        # Gemini API 초기화
        model = init_gemini_api()
        
        # 대본 미생성 게시글 가져오기
        posts = fetch_posts_without_script(limit=limit)
        
        if not posts:
            logger.info("📭 대본을 생성할 게시글이 없습니다.")
            return 0
        
        success_count = 0
        
        for idx, post in enumerate(posts, 1):
            logger.info(f"\n[{idx}/{len(posts)}] 처리 중...")
            
            # 대본 생성
            script_data = generate_script_with_gemini(model, post)
            
            if script_data:
                # MongoDB에 저장
                if save_script_to_db(post['post_id'], script_data):
                    success_count += 1
            
            # API 호출 제한 방지 (간단한 딜레이)
            if idx < len(posts):
                time.sleep(2)
        
        logger.info("=" * 60)
        logger.info("🎬 대본 생성 완료")
        logger.info(f"   성공: {success_count}/{len(posts)}")
        logger.info("=" * 60)
        
        return success_count
        
    except Exception as e:
        logger.error(f"❌ 대본 생성 중 오류 발생: {e}")
        return 0


if __name__ == '__main__':
    # 테스트 실행
    generate_scripts_batch(limit=5)


