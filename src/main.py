#!/usr/bin/env python3
"""
Guardian News MCP Server using FastMCP
"""
import asyncio
import sys
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from .tools import search_news

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# FastMCP 객체 생성
mcp = FastMCP()

# 입력 모델 정의
class SearchRequest(BaseModel):
    query: str = Field(..., description="검색할 뉴스 키워드 (예: '인공지능', '기술', '정치')")
    page_size: int = Field(5, description="가져올 기사의 수 (기본값: 5, 최대: 50)", ge=1, le=50)

# 실제 함수들 (MCP 도구와 분리)
async def search_news_impl(req: SearchRequest):
    """실제 뉴스 검색 구현"""
    try:
        result = search_news(req.query, req.page_size)
        return result
    except Exception as e:
        return {"error": f"뉴스 검색 중 오류가 발생했습니다: {str(e)}"}

async def health_impl():
    """실제 서비스 상태 확인 구현"""
    
    # 환경 변수 키 확인
    api_key = os.environ.get("GUARDIAN_API_KEY", "")
    api_key_status = "설정됨" if api_key else "설정되지 않음"
    
    return {
        "status": "ok",
        "environment": {
            "guardian_api_key": api_key_status,
            "api_key_preview": api_key[:10] + "..." if api_key else "None"
        }
    }

async def get_tool_definitions_impl():
    """실제 도구 정의 구현"""
    tools = [
        {
            "name": "health",
            "description": "서비스 상태 확인",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "search_news_tool",
            "description": "The Guardian API를 사용하여 특정 키워드에 대한 최신 뉴스를 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 뉴스 키워드 (예: '인공지능', '기술', '정치')"
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "가져올 기사의 수 (기본값: 5, 최대: 50)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["query"]
            }
        }
    ]
    
    return {"tools": tools}

@mcp.tool()
async def health():
    """서비스 상태 확인"""
    return await health_impl()

@mcp.tool()
async def search_news_tool(query: str, page_size: int = 5):
    """The Guardian API를 사용하여 특정 키워드에 대한 최신 뉴스를 검색합니다.
    
    Args:
        query: 검색할 뉴스 키워드 (예: '인공지능', '기술', '정치')
        page_size: 가져올 기사의 수 (기본값: 5, 최대: 50)
        
    Returns:
        뉴스 검색 결과
    """
    req = SearchRequest(query=query, page_size=page_size)
    return await search_news_impl(req)

@mcp.tool()
async def get_tool_definitions():
    """MCP 도구 정의를 JSON 형식으로 제공합니다."""
    return await get_tool_definitions_impl()

async def main():
    """MCP 서버를 실행합니다."""
    print("MCP Guardian News Server starting...", file=sys.stderr)
    print("Server: guardian-news-service", file=sys.stderr)
    print("Available tools: health, search_news_tool, get_tool_definitions", file=sys.stderr)
    
    try:
        # FastMCP stdio 서버 실행
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