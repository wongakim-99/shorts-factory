"""
Shorts Factory - 실행 진입점

Usage:
    python3 main.py
"""

import sys
from pathlib import Path

# app 디렉토리를 Python 경로에 추가
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

# app/core.py의 main 함수 실행
from core import main

if __name__ == '__main__':
    main()

