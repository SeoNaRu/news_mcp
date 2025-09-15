# tools.py

import os
import requests
from bs4 import BeautifulSoup 


GUARDIAN_API_URL = "https://content.guardianapis.com"

# 실제 '도구' 함수
def search_news(query: str, page_size: int = 5, section: str = None, from_date: str = None, to_date: str = None):
    """
    The Guardian API를 사용하여 특정 키워드에 대한 최신 뉴스를 검색합니다.
    섹션 및 기간 필터링을 지원합니다.

    :param query: 검색할 뉴스 키워드
    :param page_size: 가져올 기사의 수
    :param section: 검색할 뉴스 섹션 (예: 'technology', 'politics')
    :param from_date: 검색 시작일 (예: '2023-01-01')
    :param to_date: 검색 종료일 (예: '2023-10-27')
    """

    api_url = f"{GUARDIAN_API_URL}/search"

    api_key = os.getenv("GUARDIAN_API_KEY")
    if not api_key:
        return {"error": "GUARDIAN_API_KEY가 설정되지 않았습니다."}

    # API 호출 파라미터 구성
    api_params = {
        "q": query,
        "api-key": api_key,
        "page-size": page_size,
        "show-fields": "headline,trailText"
    }

    # 조건부 파라미터 추가
    if section:
        api_params["section"] = section
    if from_date:
        api_params["from-date"] = from_date
    if to_date:
        api_params["to-date"] = to_date

    try:
        response = requests.get(api_url, params=api_params)
        response.raise_for_status()
        articles = response.json()["response"]["results"]

        formatted_results = [
            {
                "headline": article.get("fields", {}).get("headline"),
                "summary": article.get("fields", {}).get("trailText"),
                "url": article.get("webUrl")
            }
            for article in articles
        ]
        return {"articles": formatted_results}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_available_sections():
    """
    The Guardian API에서 제공하는 모든 뉴스 섹션 목록을 가져옵니다.
    """
    api_key = os.getenv("GUARDIAN_API_KEY")
    if not api_key:
        return {"error": "GUARDIAN_API_KEY가 설정되지 않았습니다."}

    api_url = f"{GUARDIAN_API_URL}/sections"
    api_params = {"api-key": api_key}

    try:
        response = requests.get(api_url, params=api_params)
        response.raise_for_status()
        results = response.json()["response"]["results"]

        # 각 섹션의 id와 webTitle을 함께 제공하여 사용자 편의성을 높입니다.
        sections = [
            {"id": section.get("id"), "title": section.get("webTitle")}
            for section in results
        ]
        return {"sections": sections}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_full_article_text(url: str):
    """
    주어진 URL의 웹 페이지에서 기사 본문을 스크래핑하여 반환합니다.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # The Guardian 기사 본문은 보통 data-gu-name="body" 속성을 가진 div 내부에 있습니다.
        article_body = soup.find('div', attrs={'data-gu-name': 'body'})

        if not article_body:
            return {"error": "기사 본문을 찾을 수 없습니다. 페이지 구조가 다를 수 있습니다."}

        # 본문 내의 모든 p (문단) 태그의 텍스트를 합칩니다.
        paragraphs = article_body.find_all('p')
        full_text = "\n".join([p.get_text() for p in paragraphs])

        return {"url": url, "text": full_text}

    except requests.exceptions.RequestException as e:
        return {"error": f"URL에 접근하는 중 오류가 발생했습니다: {str(e)}"}
    except Exception as e:
        return {"error": f"기사 본문을 파싱하는 중 오류가 발생했습니다: {str(e)}"}
