"""
역할 : Gemini API 클라이언트 초기화
포함내용
- API KEY 검증
- genai.configure(api_key=api_key)
- 모델 생성 (GenerativeModel)
- 로깅
"""

import logging
import os

import google.generativeai as genai

from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_gemini_api() -> genai.GenerativeModel:
    """
    Gemini API 클라이언트 초기화

    Returns:
        Gemini GenerativeModel 객체
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == 'your_api_key_here':
        raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')

    logger.info("✅ Gemini API 초기화 완료")
    return model


def call_gemini_api(model: genai.GenerativeModel, prompt: str) -> str:
    """
    Gemini API 를 호출하여 응답 텍스트를 반환

    Args:
        model: 초기화된 GenerativeModel 객체
        prompt: 전달할 프롬프트 문자열

    Returns:
        API 응답 텍스트 (str)

    Raises:
        Exception: API 호출 실패 시
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"❌ Gemini API 호출 실패 : {e}")
        raise