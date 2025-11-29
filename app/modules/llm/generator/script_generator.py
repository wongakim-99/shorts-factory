"""
역할: 전체 대본 생성 프로세스
포함 내용:
- 프롬프트 생성 (prompt_builder.create_script_prompt()) 호출
- API 호출 (gemini_client.call_gemini_api()) 호출
- JSON 파싱 (코드블럭 제거 + 파싱)
- 메타데이터 추가 (generated_at, model, post_id)
"""

import logging
import json

from typing import Dict, Optional
from datetime import datetime

import google.generativeai as genai

from app.modules.llm.prompt.prompt_builder import create_script_prompt
from app.modules.llm.client.gemini_client import call_gemini_api


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_script_with_gemini(model: genai.GenerativeModel, post: Dict) -> Optional[Dict]:
    """
    Gemini API 를 사용하여 영상 대본 생성

    Args:
        model: Gemini GenerativeModel 객체
        post: 게시글 데이터

    Returns:
        생성된 대본 딕셔너리 또는 None
    """
    script_text = None  # 초기화 (에러 처리에서 참조 가능하도록)
    
    try:
        prompt = create_script_prompt(post)

        logger.info(f"📝 대본 생성 시작: {post.get('title', '')[:30]}...")

        # Gemini API 호출
        script_text = call_gemini_api(model, prompt)

        # JSON 파싱 (Gemini 가 코드블록드로 감쌀 수 있으므로 처리)
        if script_text.startswith('```json'):
            script_text = script_text[7:]
        if script_text.startswith('```'):
            script_text = script_text[3:]
        if script_text.endswith('```'):
            script_text = script_text[:-3]

        script_text = script_text.strip()

        # JSON 파싱
        script_data = json.loads(script_text)

        # 메타데이터 추가
        script_data['generated_at'] = datetime.now()
        script_data['model'] = 'gemini-2.5-pro'
        script_data['post_id'] = post.get('post_id')

        logger.info(f"✅ 대본 생성 완료: {post.get('title', '')[:30]}...")

        return script_data

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 파싱 실패: {e}")
        logger.error(f"   응답 내용: {script_text[:200] if script_text else 'N/A'}...")
        return None
    except Exception as e:
        logger.error(f"❌ 대본 생성 실패: {e}")
        return None
