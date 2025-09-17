# tools.py
import os
import requests
import collections
from bs4 import BeautifulSoup 
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cachetools import cached, TTLCache


GUARDIAN_API_URL = "https://content.guardianapis.com"

sections_cache = TTLCache(maxsize=1, ttl=86400)    # 24시간 유지, 최대 1개 저장
article_cache = TTLCache(maxsize=100, ttl=86400)   # 24시간 유지, 최대 100개 저장
trend_cache = TTLCache(maxsize=100, ttl=3600)  
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
        return {"error": "The GUARDIAN_API_KEY environment variable is not set."}

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


@cached(cache=sections_cache)
def get_available_sections():
    """
    The Guardian API에서 제공하는 모든 뉴스 섹션 목록을 가져옵니다.
    """
    api_key = os.getenv("GUARDIAN_API_KEY")
    if not api_key:
        return {"error": "The GUARDIAN_API_KEY environment variable is not set."}

    api_url = f"{GUARDIAN_API_URL}/sections"
    api_params = {"api-key": api_key}

    try:
        response = requests.get(api_url, params=api_params)
        response.raise_for_status()
        results = response.json()["response"]["results"]

        sections = [
            {"id": section.get("id"), "title": section.get("webTitle")}
            for section in results
        ]
        return {"sections": sections}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@cached(cache=article_cache)
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

        article_body = soup.find('div', attrs={'data-gu-name': 'body'})

        if not article_body:
            return {"error": "기사 본문을 찾을 수 없습니다. 페이지 구조가 다를 수 있습니다."}

        paragraphs = article_body.find_all('p')
        full_text = "\n".join([p.get_text() for p in paragraphs])

        return {"url": url, "text": full_text}

    except requests.exceptions.RequestException as e:
        return {"error": f"URL에 접근하는 중 오류가 발생했습니다: {str(e)}"}
    except Exception as e:
        return {"error": f"기사 본문을 파싱하는 중 오류가 발생했습니다: {str(e)}"}

@cached(cache=trend_cache)
def get_news_trend(query: str, start_date_str: str, end_date_str: str):
    """
    주어진 기간 동안 특정 키워드에 대한 월별 뉴스 기사 수를 집계하여 트렌드 데이터를 반환합니다.
    """
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        trend_data = []
        current_date = start_date

        while current_date <= end_date:
            # 해당 월의 시작일과 마지막일 계산
            month_start = current_date.strftime("%Y-%m-%d")
            month_end = (current_date + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")

            # search_news 함수를 재활용하되, 기사 내용은 필요 없으므로 page_size=1로 설정
            # 실제로는 total 숫자만 필요합니다.
            api_key = os.getenv("GUARDIAN_API_KEY")
            if not api_key:
                return {"error": "The GUARDIAN_API_KEY environment variable is not set."}

            api_params = {
                "q": query,
                "api-key": api_key,
                "from-date": month_start,
                "to-date": month_end,
                "page-size": 1 # 내용이 아닌 총 개수만 필요하므로 최소한으로 요청
            }
            api_url = f"{GUARDIAN_API_URL}/search"
            response = requests.get(api_url, params=api_params)
            response.raise_for_status()

            # 응답에서 총 기사 수('total')를 추출
            total_articles = response.json()["response"]["total"]
            
            trend_data.append({
                "period": current_date.strftime("%Y-%m"),
                "article_count": total_articles
            })

            # 다음 달로 이동
            current_date += relativedelta(months=1)

        return {"trend": trend_data}

    except Exception as e:
        return {"error": f"뉴스 트렌드 분석 중 오류가 발생했습니다: {str(e)}"}

def get_related_topics(query: str, page_size: int = 20):
    """
    특정 키워드와 관련된 기사들의 태그를 분석하여 가장 빈도가 높은 연관 토픽을 반환합니다.
    """
    try:
        api_key = os.getenv("GUARDIAN_API_KEY")
        if not api_key:
            return {"error": "The GUARDIAN_API_KEY environment variable is not set."}

        api_params = {
            "q": query,
            "api-key": api_key,
            "page-size": page_size,
            "show-tags": "keyword"  # 'keyword' 타입의 태그를 함께 요청
        }
        api_url = f"{GUARDIAN_API_URL}/search"
        response = requests.get(api_url, params=api_params)
        response.raise_for_status()

        articles = response.json()["response"]["results"]
        
        if not articles:
            return {"related_topics": []}

        # 모든 기사의 모든 태그를 하나의 리스트에 수집
        all_tags = []
        for article in articles:
            for tag in article.get("tags", []):
                all_tags.append(tag['webTitle'])

        # 태그의 빈도를 계산하여 가장 흔한 10개를 추출
        tag_counts = collections.Counter(all_tags)
        most_common_tags = tag_counts.most_common(10)

        # 결과를 보기 좋은 형태로 가공
        related_topics = [
            {"topic": tag, "count": count}
            for tag, count in most_common_tags
        ]

        return {"related_topics": related_topics}

    except Exception as e:
        return {"error": f"연관 토픽 분석 중 오류가 발생했습니다: {str(e)}"}