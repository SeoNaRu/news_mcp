# Guardian News MCP Server

The Guardian API를 사용하여 최신 뉴스를 검색할 수 있는 MCP (Model Context Protocol) 서버입니다.

## 기능

- **뉴스 검색**: 특정 키워드로 Guardian API에서 최신 뉴스 검색
- **서비스 상태 확인**: API 키 설정 상태 및 서비스 상태 확인
- **도구 정의 제공**: MCP 도구 정의를 JSON 형식으로 제공

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

또는 uv를 사용하는 경우:

```bash
uv sync
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Guardian API 키를 설정하세요:

```env
GUARDIAN_API_KEY=your_guardian_api_key_here
```

Guardian API 키는 [The Guardian Open Platform](https://open-platform.theguardian.com/)에서 무료로 발급받을 수 있습니다.

### 3. 서버 실행

```bash
python -m src.main
```

## 사용 가능한 도구

### 1. `health`
서비스 상태를 확인합니다.

**매개변수**: 없음

**반환값**:
```json
{
  "status": "ok",
  "environment": {
    "guardian_api_key": "설정됨",
    "api_key_preview": "e8bf1e48-7..."
  }
}
```

### 2. `search_news_tool`
특정 키워드로 뉴스를 검색합니다.

**매개변수**:
- `query` (필수): 검색할 뉴스 키워드
- `page_size` (선택): 가져올 기사의 수 (기본값: 5, 최대: 50)

**반환값**:
```json
{
  "articles": [
    {
      "headline": "뉴스 제목",
      "summary": "뉴스 요약",
      "url": "https://www.theguardian.com/..."
    }
  ]
}
```

### 3. `get_tool_definitions`
MCP 도구 정의를 JSON 형식으로 제공합니다.

**매개변수**: 없음

## 프로젝트 구조

```
mcp-guardian-news/
├── src/
│   ├── main.py          # MCP 서버 메인 파일
│   └── tools.py         # Guardian API 호출 도구
├── requirements.txt     # Python 의존성
├── pyproject.toml       # 프로젝트 설정
├── tool_definitions.json # MCP 도구 정의
├── .gitignore          # Git 무시 파일
└── README.md           # 프로젝트 문서
```

## 기술 스택

- **FastMCP**: MCP 서버 구현
- **Pydantic**: 데이터 검증 및 직렬화
- **Requests**: HTTP API 호출
- **Python-dotenv**: 환경 변수 관리

## 라이선스

MIT License
