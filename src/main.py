#!/usr/bin/env python3
"""
Guardian News MCP Server using FastMCP
"""
import asyncio
import sys
from fastmcp import FastMCP
from pydantic import BaseModel, Field
# --- 👇 수정된 부분: get_available_sections를 import에 추가 ---
from .tools import search_news, get_available_sections, get_full_article_text
from typing import Optional

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# FastMCP 객체 생성
mcp = FastMCP()


class ArticleRequest(BaseModel):
    url: str = Field(..., description="본문을 가져올 기사의 URL")

class SearchRequest(BaseModel):
    query: str = Field(..., description="검색할 뉴스 키워드 (예: '인공지능', '기술', '정치')")
    page_size: int = Field(5, description="가져올 기사의 수 (기본값: 5, 최대: 50)", ge=1, le=50)
    section: Optional[str] = Field(None, description="검색할 뉴스 섹션 (예: 'technology')")
    from_date: Optional[str] = Field(None, description="검색 시작일 (YYYY-MM-DD 형식, 예: '2023-10-01')")
    to_date: Optional[str] = Field(None, description="검색 종료일 (YYYY-MM-DD 형식, 예: '2023-10-27')")

# 실제 함수들 (MCP 도구와 분리)
async def search_news_impl(req: SearchRequest):
    """실제 뉴스 검색 구현"""

    try:
        result = search_news(
            req.query,
            req.page_size,
            req.section,
            req.from_date,
            req.to_date
        )
        return result
    except Exception as e:
        return {"error": f"뉴스 검색 중 오류가 발생했습니다: {str(e)}"}

        
async def get_available_sections_impl():
    """실제 섹션 목록 조회 구현"""
    try:
        return get_available_sections()
    except Exception as e:
        return {"error": f"섹션 목록 조회 중 오류가 발생했습니다: {str(e)}"}

async def health_impl():
    """실제 서비스 상태 확인 구현"""
    api_key = os.environ.get("GUARDIAN_API_KEY", "")
    api_key_status = "설정됨" if api_key else "설정되지 않음"
    return {
        "status": "ok",
        "environment": {
            "guardian_api_key": api_key_status,
            "api_key_preview": api_key[:10] + "..." if api_key else "None"
        }
    }

async def get_full_article_text_impl(req: ArticleRequest):
    """실제 기사 본문 조회 구현"""
    try:
        # get_full_article_text는 동기 함수이므로, to_thread로 실행하여 비동기 루프를 막지 않도록 합니다.
        return await asyncio.to_thread(get_full_article_text, req.url)
    except Exception as e:
        return {"error": f"기사 본문 조회 중 오류가 발생했습니다: {str(e)}"}

async def get_tool_definitions_impl():
    """실제 도구 정의 구현"""
    tools = [
        {
            "name": "health",
            "description": "서비스 상태 확인",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "get_sections_tool",
            "description": "The Guardian API에서 제공하는 모든 뉴스 섹션 목록을 가져옵니다.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "search_news_tool",
            "description": "The Guardian API를 사용하여 특정 키워드에 대한 최신 뉴스를 검색합니다. 섹션 및 날짜 필터링을 지원합니다. 검색어는 반드시 영어(English)여야 합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색할 뉴스 키워드 (예: 'AI', 'technology', 'politics')"},
                    "page_size": {"type": "integer", "description": "가져올 기사의 수 (기본값: 5, 최대: 50)", "default": 5, "minimum": 1, "maximum": 50},
                    "section": {"type": "string", "description": "검색을 제한할 뉴스 섹션 (예: 'technology', 'world')"},
                    "from_date": {"type": "string", "description": "검색 시작일 (YYYY-MM-DD 형식)"},
                    "to_date": {"type": "string", "description": "검색 종료일 (YYYY-MM-DD 형식)"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_full_article_text_tool",
            "description": "기사 URL을 입력받아 해당 기사의 전체 본문 텍스트를 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "본문을 가져올 기사의 전체 URL"
                    }
                },
                "required": ["url"]
            }
        }
    ]
    return {"tools": tools}

@mcp.tool()
async def health():
    """서비스 상태 확인"""
    return await health_impl()

@mcp.tool()
async def get_sections_tool():
    """The Guardian에서 검색 가능한 모든 뉴스 섹션 목록을 제공합니다."""
    return await get_available_sections_impl()

@mcp.tool()
async def search_news_tool(
    query: str,
    page_size: int = 5,
    section: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """The Guardian API를 사용하여 특정 키워드에 대한 최신 뉴스를 검색합니다."""
    req = SearchRequest(
        query=query,
        page_size=page_size,
        section=section,
        from_date=from_date,
        to_date=to_date
    )
    return await search_news_impl(req)

@mcp.tool()
async def get_tool_definitions():
    """MCP 도구 정의를 JSON 형식으로 제공합니다."""
    return await get_tool_definitions_impl()

@mcp.tool()
async def get_full_article_text_tool(url: str):
    """기사 URL을 입력받아 해당 기사의 전체 본문 텍스트를 가져옵니다."""
    req = ArticleRequest(url=url)
    return await get_full_article_text_impl(req)

async def main():
    """MCP 서버를 실행합니다."""
    print("MCP Guardian News Server starting...", file=sys.stderr)
    print("Server: guardian-news-service", file=sys.stderr)
    print("Available tools: health,get_full_article_text_tool, search_news_tool, get_sections_tool, get_tool_definitions", file=sys.stderr)
    
    try:
        await mcp.run_stdio_async()
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server failed: {e}", file=sys.stderr)
        sys.exit(1)