"""
DC 인사이드 크롤링 로직만 담당
나중에 naver 뉴스, reddit 등등 추가 가능

해당 파일에서는 DC인사이드 상세 목록(detail)에 대한 크롤링 담당
"""

import os
import logging
import requests
import hashlib
import shutil
import time as time_module
from datetime import datetime, timedelta

from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# Selenium 관련
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from app.modules.crawling.dcinside.constants import GALLERY_ID, BASE_URL, HEADERS

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_old_images(keep_days: int = 7):
    """
    오래된 이미지 폴더 자동 삭제
    
    Args:
        keep_days: 보관 기간 (일). 이보다 오래된 폴더는 삭제
    """
    try:
        images_base_dir = Path("app/output/images")
        if not images_base_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        # 날짜 형식 폴더만 확인 (YYYY-MM-DD)
        for folder in images_base_dir.iterdir():
            if not folder.is_dir():
                continue
            
            try:
                # 폴더명이 날짜 형식인지 확인
                folder_date = datetime.strptime(folder.name, '%Y-%m-%d')
                
                # 오래된 폴더 삭제
                if folder_date < cutoff_date:
                    shutil.rmtree(folder)
                    deleted_count += 1
                    logger.info(f"🗑️ 오래된 이미지 폴더 삭제: {folder.name}")
            except ValueError:
                # 날짜 형식이 아닌 폴더는 무시
                continue
        
        if deleted_count > 0:
            logger.info(f"✅ 총 {deleted_count}개 폴더 정리 완료")
        else:
            logger.info(f"✅ 정리할 오래된 이미지 없음 (보관 기간: {keep_days}일)")
            
    except Exception as e:
        logger.warning(f"⚠️ 이미지 정리 실패: {e}")


def get_comments_with_selenium(post_id: str) -> List[str]:
    """
    Selenium을 사용하여 댓글 크롤링 (JavaScript 동적 로딩 대응)
    
    Args:
        post_id: 게시글 번호
    
    Returns:
        댓글 리스트
    """
    comments = []
    
    try:
        # Chrome/Chromium 옵션 설정 (headless 모드)
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 백그라운드 실행
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 로그 최소화
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Chromium 바이너리 경로 설정 (Docker 환경)
        # macOS에서는 자동으로 Chrome 찾음, Docker에서는 chromium 사용
        try:
            chrome_options.binary_location = '/usr/bin/chromium'
        except:
            pass  # macOS는 기본 경로 사용
        
        # WebDriver 생성
        driver = webdriver.Chrome(options=chrome_options)
        
        # 페이지 접속
        url = f"https://gall.dcinside.com/mgallery/board/view?id={GALLERY_ID}&no={post_id}"
        driver.get(url)
        
        # 댓글 영역 로딩 대기 (최대 10초)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "comment_wrap"))
            )
            
            # 추가 대기 (댓글 로딩 완료)
            time_module.sleep(2)
            
            # 댓글 수 확인
            comment_total_elem = driver.find_element(By.ID, f"comment_total_{post_id}")
            comment_count = int(comment_total_elem.text)
            
            if comment_count == 0:
                logger.info(f"  💬 댓글 없음")
                driver.quit()
                return []
            
            logger.info(f"  💬 댓글 {comment_count}개 발견")
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # 댓글 <li> 요소 찾기
            comment_list = soup.select('ul.cmt_list li')
            
            if not comment_list:
                comment_list = soup.select('.comment_wrap li')
            
            logger.info(f"  🔍 댓글 <li> 요소 {len(comment_list)}개 발견")
            
            for li in comment_list:
                # 광고성 댓글 제외
                li_classes = li.get('class', [])
                if 'dory' in li_classes or 'ad' in li_classes:
                    continue
                
                # 텍스트 댓글 찾기 (.usertxt 우선)
                comment_text_elem = li.select_one('.usertxt')
                
                if comment_text_elem:
                    comment_text = comment_text_elem.get_text(strip=True)
                    
                    # "디시콘 보기" 같은 버튼 텍스트 제외
                    if comment_text and len(comment_text) > 0 and comment_text != "디시콘 보기":
                        # 대댓글 여부 확인
                        is_reply = 'reply' in li_classes or li.find_parent('ul', class_='reply_list')
                        if is_reply:
                            comments.append(f"└ {comment_text}")
                        else:
                            comments.append(comment_text)
            
            # 중복 제거
            comments = list(dict.fromkeys(comments))
            
            logger.info(f"  ✅ Selenium 댓글 수집 완료: {len(comments)}개")
            
        except Exception as e:
            logger.warning(f"  ⚠️ 댓글 로딩 대기 실패: {e}")
        
        finally:
            driver.quit()
    
    except Exception as e:
        logger.error(f"  ❌ Selenium 댓글 크롤링 실패: {e}")
    
    return comments


def download_image(image_url: str, post_id: str, img_index: int) -> Optional[str]:
    """
    이미지 다운로드 (403 에러 방지를 위해 Referer 헤더 포함)
    
    Args:
        image_url: 이미지 URL
        post_id: 게시글 ID
        img_index: 이미지 순서
    
    Returns:
        저장된 이미지의 로컬 경로 (실패 시 None)
    """
    try:
        # 날짜별 이미지 저장 디렉토리 생성 (YYYY-MM-DD 형식)
        today = datetime.now().strftime('%Y-%m-%d')
        images_dir = Path(f"app/output/images/{today}")
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Referer 헤더 추가 (DCInside에서 오는 것처럼 위장)
        headers = HEADERS.copy()
        headers['Referer'] = f'https://gall.dcinside.com/mgallery/board/view/?id={GALLERY_ID}&no={post_id}'
        
        # 이미지 다운로드
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 파일 확장자 추출
        ext = image_url.split('.')[-1].split('?')[0]  # URL 파라미터 제거
        if ext.lower() not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            ext = 'jpg'  # 기본 확장자
        
        # 파일명 생성 (게시글ID_순서.확장자)
        filename = f"{post_id}_{img_index:02d}.{ext}"
        filepath = images_dir / filename
        
        # 이미지 저장
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"  📸 이미지 저장: {filename}")
        return str(filepath)
        
    except Exception as e:
        logger.warning(f"  ⚠️ 이미지 다운로드 실패 ({image_url}): {e}")
        return None


# 갤러리 게시글 디테일 크롤링
def get_post_detail(post_id: str, download_images: bool = True, debug: bool = False) -> Optional[Dict]:
    """
    게시글 본문 크롤링

    Args:
        post_id: 게시글 번호
        download_images: 이미지 다운로드 여부 (기본: True)
        debug: 디버그 모드 (HTML 저장 및 상세 로그)

    Returns:
        {'post_id', 'title', 'author', 'content', 'images', 'image_paths', 'comments'}
    """
    url = f"https://gall.dcinside.com/mgallery/board/view"
    params = {
        'id': GALLERY_ID,
        'no': post_id,
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # 디버그 모드: HTML 저장 및 댓글 영역 분석
        if debug:
            debug_dir = Path("app/output/debug")
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            # 전체 HTML 저장
            with open(debug_dir / f"post_{post_id}.html", 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"  🐛 DEBUG: HTML 저장됨 → app/output/debug/post_{post_id}.html")
            
            # 댓글 영역 분석
            comment_area = soup.find('div', class_='comment_wrap') or soup.find('div', class_='cmt_area')
            if comment_area:
                logger.info(f"  🐛 DEBUG: 댓글 영역 발견")
                logger.info(f"  🐛 DEBUG: ul.cmt_list 개수: {len(comment_area.select('ul.cmt_list'))}")
                logger.info(f"  🐛 DEBUG: li 개수: {len(comment_area.find_all('li'))}")
            else:
                logger.warning(f"  🐛 DEBUG: 댓글 영역을 찾을 수 없음!")

        # 제목
        title_elem = soup.select_one('span.title_subject')
        title = title_elem.text.strip() if title_elem else ''

        # 작성자
        author_elem = soup.select_one('div.gall_writer')
        author = author_elem.get('data-nick', '익명') if author_elem else '익명'

        # 본문 영역 찾기
        content_elem = soup.select_one('div.write_div')
        
        # 이미지 URL 먼저 수집 (decompose 전에!)
        images = []  # 원본 URL
        image_paths = []  # 다운로드된 로컬 경로
        
        if content_elem:
            img_index = 0
            for img in content_elem.find_all('img'):
                src = img.get('src', '')
                if src and src.startswith('http'):
                    images.append(src)
                    
                    # 이미지 다운로드
                    if download_images:
                        local_path = download_image(src, post_id, img_index)
                        if local_path:
                            image_paths.append(local_path)
                    img_index += 1
        
        # 본문 텍스트 추출 (이미지 태그 제거)
        if content_elem:
            # 이미지 태그 제거하고 텍스트만 추출
            for img in content_elem.find_all('img'):
                img.decompose()
            content = content_elem.get_text(separator='\n', strip=True)
        else:
            content = ''

        # 댓글 수집 (Selenium 사용 - JavaScript 동적 로딩 대응)
        comments = get_comments_with_selenium(post_id)

        logger.info(f"📝 게시글 {post_id} 본문 수집 완료 (본문 {len(content)}자, 이미지 {len(image_paths)}개, 댓글 {len(comments)}개)")

        return {
            'post_id': post_id,
            'title': title,
            'author': author,
            'content': content,
            'images': images,  # 원본 URL (참고용)
            'image_paths': image_paths,  # 다운로드된 로컬 경로
            'comments': comments,
        }

    except requests.RequestException as e:  # 게시글 요청에 대한 실패에 대한 예외처리
        logger.error(f"❌ 게시글 {post_id} 요청 실패: {e}")
        return None

    except Exception as e:  # 게시글 파싱 실패에 대한 예외처리
        logger.error(f"❌ 게시글 {post_id} 파싱 실패: {e}")
        return None