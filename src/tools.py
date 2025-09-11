import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키는 여기에 직접 두거나, 더 안전하게는 별도의 설정 파일이나 환경 변수에서 불러옵니다.
GUARDIAN_API_URL = "https://content.guardianapis.com/search"

# 실제 '도구' 함수
def search_news(query: str, page_size: int = 5):
    """
    The Guardian API를 사용하여 특정 키워드에 대한 최신 뉴스를 검색합니다.

    :param query: 검색할 뉴스 키워드 (예: '인공지능', '경제')
    :param page_size: 가져올 기사의 수 (기본값: 5)
    """

    # 함수 호출 시점에 API 키를 다시 읽어옵니다
    api_key = os.getenv("GUARDIAN_API_KEY")
    
    if not api_key:
        return {"error": "GUARDIAN_API_KEY가 설정되지 않았습니다."}
    
    # API 호출
    api_params = {
        "q": query,
        "api-key": api_key,
        "page-size": page_size,
        "show-fields": "headline,trailText"
    }

    try:
        response = requests.get(GUARDIAN_API_URL, params=api_params)
        response.raise_for_status() # HTTP 오류 발생 시 예외 처리
        articles = response.json()["response"]["results"]

        # AI가 이해하기 쉬운 형태로 결과 데이터를 가공
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