"""
Selenium 댓글 크롤링 테스트
"""

from app.modules.crawling.dcinside.detail_scraper import get_comments_with_selenium

# 댓글 많은 게시글로 테스트
POST_ID = "13267271"  # 실제 댓글 있는 게시글

print(f"🔍 게시글 {POST_ID} 댓글 크롤링 테스트 중...\n")

comments = get_comments_with_selenium(POST_ID)

print("\n" + "=" * 80)
print(f"✅ 댓글 수집 완료: {len(comments)}개")
print("=" * 80)

if comments:
    print("\n📋 수집된 댓글:")
    for i, comment in enumerate(comments[:5], 1):  # 처음 5개만 출력
        print(f"{i}. {comment[:100]}...")  # 100자까지만
    
    if len(comments) > 5:
        print(f"\n... 외 {len(comments) - 5}개 댓글")
else:
    print("\n⚠️ 댓글이 없습니다.")

