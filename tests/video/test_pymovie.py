import sys
from pathlib import Path

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def create_test_video():
    print("🎬 영상 생성을 시작합니다...")

    # 출력 디렉토리 설정
    output_dir = Path("app/output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 배경 생성 (FHD 사이즈, 검은색, 5초)
    # size=(가로, 세로)
    bg_clip = ColorClip(size=(1080, 1920), color=[0, 0, 0], duration=5)

    # 2. 텍스트(자막) 생성
    # 맥북은 한글 폰트가 'AppleGothic'이 기본으로 있어서 이걸 쓰면 깨짐 방지 가능
    # 만약 에러나면 font='Arial'로 바꾸고 영어로 먼저 테스트하세요.
    txt_clip = TextClip(
        "쇼츠 공장 가동 테스트\n(Local Mac)",
        fontsize=70,
        color='white',
        font='AppleGothic'  # 맥북 기본 한글 폰트
    )

    # 텍스트 위치: 정중앙 (center)
    txt_clip = txt_clip.set_position('center').set_duration(5)

    # 3. 합성 (배경 위에 텍스트 얹기)
    video = CompositeVideoClip([bg_clip, txt_clip])

    # 4. 파일 저장 (코덱 libx264 중요)
    output_filename = output_dir / "mac_test_shorts.mp4"
    video.write_videofile(
        str(output_filename),
        fps=24,
        codec='libx264',  # 유튜브 업로드 표준 코덱
        audio_codec='aac'
    )
    print(f"✅ 완료! {output_filename} 파일이 생성되었습니다.")


if __name__ == "__main__":
    create_test_video()