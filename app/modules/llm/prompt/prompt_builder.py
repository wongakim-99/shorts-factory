"""
역할: 게시글 데이터를 프롬프트 문자열로 변환
포함 내용:
- 게시글 정보 (제목, 본문, 댓글) + 대본 작성 규칙 템플릿
"""

import logging

from typing import Dict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_script_prompt(post: Dict) -> str:
    """
    게시글 정보를 기반으로 Gemini 에게 전달할 프롬프트 생성

    Args:
        post: MongoDB 에서 가져온 게시글 데이터

    Returns:
        프롬프트 문자열
    """
    title = post.get('title', '')
    content = post.get('content', '')
    recommend_count = post.get('recommend_count', 0)
    comment_count = post.get('comment_count', 0)

    # 댓글이 있을경우 일부 포함
    comments_text = ""
    if post.get('comments'):
        top_comments = post['comments'][:5]  # 상위 5개 댓글만
        comments_text = "\n".join([f"- {c.get('content', '')}" for c in top_comments])

    prompt = f"""
당신은 '시니컬한 경제 분석 유튜버'입니다.
DC인사이드 주식 갤러리의 다음 게시글을 기반으로 50초 분량의 쇼츠 영상 대본을 작성하세요.

# 게시글 정보
- 제목: {title}
- 추천수: {recommend_count}
- 댓글수: {comment_count}

## 본문
{content}

## 주요 댓글
{comments_text if comments_text else "(댓글 없음)"}

---

# 대본 작성 규칙
1. **어조**: 구어체, 시니컬, 음모론적, ~했다체 금지
2. **구조**:
   - [후킹] (5초): 시청자의 공포와 호기심을 자극하는 첫 문장
   - [메인] (35초): 팩트 + 뇌피셜 분석. 커뮤니티 여론을 녹여내되, 과장되고 자극적으로
   - [결론] (10초): 팩폭 결론. 희망고문 또는 절망 강조
3. **톤**: "여러분 이거 알아요?", "근데 진짜 문제는...", "결국 우리만 당하는 거지" 같은 표현 사용
4. **금지**: 존댓말 과다, 딱딱한 문어체, 중립적 태도

# 출력 형식 (JSON)
반드시 아래 JSON 형식으로만 출력하세요. 다른 설명 없이 JSON만 출력하세요.

{{
  "hook": "후킹 문장 (5초 분량)",
  "main": "메인 대본 (35초 분량)",
  "conclusion": "결론 (10초 분량)",
  "full_script": "전체 대본을 하나로 이은 텍스트"
}}
"""
    
    return prompt