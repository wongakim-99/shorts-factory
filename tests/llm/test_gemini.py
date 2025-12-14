"""
Gemini API 및 대본 생성 테스트

Usage:
    python3 tests/llm/test_gemini.py
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.modules.llm.llm_writer import (
    generate_scripts_batch
)
from app.modules.llm.client.gemini_client import init_gemini_api
from app.modules.llm.repository.script_repository import fetch_posts_without_script
from app.modules.llm.generator.script_generator import generate_script_with_gemini

def test_gemini_connection():
    """Gemini API 연결 테스트"""
    print("=" * 60)
    print("🔌 Gemini API 연결 테스트")
    print("=" * 60)
    
    try:
        model = init_gemini_api()
        
        # 간단한 테스트 메시지
        response = model.generate_content("안녕하세요. 간단히 '연결 성공'이라고만 답변해주세요.")
        print(f"✅ Gemini API 응답: {response.text}")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Gemini API 연결 실패: {e}")
        print("=" * 60)
        return False


def test_fetch_posts():
    """대본 미생성 게시글 조회 테스트"""
    print("\n" + "=" * 60)
    print("📚 대본 미생성 게시글 조회 테스트")
    print("=" * 60)
    
    try:
        posts = fetch_posts_without_script(limit=3)
        
        if posts:
            print(f"✅ {len(posts)}개 게시글 조회 성공")
            for idx, post in enumerate(posts, 1):
                print(f"\n[{idx}] {post.get('title', '')[:50]}...")
                print(f"    - 추천수: {post.get('recommend_count', 0)}")
                print(f"    - 댓글수: {post.get('comment_count', 0)}")
        else:
            print("⚠️ 대본 미생성 게시글이 없습니다.")
        
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ 게시글 조회 실패: {e}")
        print("=" * 60)
        return False


def test_single_script_generation():
    """단일 게시글 대본 생성 테스트"""
    print("\n" + "=" * 60)
    print("📝 단일 대본 생성 테스트")
    print("=" * 60)
    
    try:
        # Gemini 모델 초기화
        model = init_gemini_api()
        
        # 대본 미생성 게시글 가져오기
        posts = fetch_posts_without_script(limit=1)
        
        if not posts:
            print("⚠️ 테스트할 게시글이 없습니다.")
            print("   먼저 크롤링을 실행하세요: python3 main.py")
            print("=" * 60)
            return False
        
        post = posts[0]
        print(f"테스트 게시글: {post.get('title', '')[:50]}...")
        
        # 대본 생성
        script_data = generate_script_with_gemini(model, post)
        
        if script_data:
            print("\n✅ 대본 생성 성공!")
            
            # 새로운 JSON 구조 출력
            script_segments = script_data.get('script_segments', [])
            full_text_for_thumbnail = script_data.get('full_text_for_thumbnail', '')
            
            if script_segments:
                print("\n📝 대본 세그먼트:")
                print("=" * 60)
                for idx, segment in enumerate(script_segments, 1):
                    role = segment.get('role', 'unknown')
                    text = segment.get('text', '')
                    emotion = segment.get('emotion', '')
                    duration = segment.get('duration_estimate', 0)
                    
                    role_emoji = "🎙️" if role == "narrator" else "💬"
                    emotion_text = f" [{emotion}]" if emotion else ""
                    duration_text = f" ({duration}초)" if duration else ""
                    
                    print(f"\n[{idx}] {role_emoji} {role.upper()}{emotion_text}{duration_text}")
                    print(f"    {text[:100]}{'...' if len(text) > 100 else ''}")
                
                print("\n" + "=" * 60)
            
            if full_text_for_thumbnail:
                print(f"\n📌 썸네일용 텍스트: {full_text_for_thumbnail}")
            
            # 메타데이터 출력
            print(f"\n📊 메타데이터:")
            print(f"    - 생성 시간: {script_data.get('generated_at', 'N/A')}")
            print(f"    - 모델: {script_data.get('model', 'N/A')}")
            print(f"    - 게시글 ID: {script_data.get('post_id', 'N/A')}")
        else:
            print("❌ 대본 생성 실패")
        
        print("=" * 60)
        return script_data is not None
        
    except Exception as e:
        print(f"❌ 대본 생성 테스트 실패: {e}")
        print("=" * 60)
        return False


def main():
    """전체 테스트 실행"""
    print("\n🧪 Gemini API 통합 테스트 시작\n")
    
    results = []
    
    # 1. API 연결 테스트
    results.append(("API 연결", test_gemini_connection()))
    
    # 2. 게시글 조회 테스트
    results.append(("게시글 조회", test_fetch_posts()))
    
    # 3. 대본 생성 테스트 (실제 API 호출)
    print("\n⚠️  다음 테스트는 실제 Gemini API를 호출합니다.")
    print("   계속하시겠습니까? (y/n): ", end="")
    
    answer = input().strip().lower()
    if answer == 'y':
        results.append(("대본 생성", test_single_script_generation()))
    else:
        print("   대본 생성 테스트를 건너뜁니다.")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {test_name}: {status}")
    
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패")
    
    print("=" * 60)


if __name__ == '__main__':
    main()


