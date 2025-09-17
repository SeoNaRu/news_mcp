## Guardian News MCP Server
High-performance MCP (Model Context Protocol) server for advanced news analysis using The Guardian API.

This project provides advanced features such as detailed news searches, trend analysis over time, related topic discovery, and full article text extraction. It's designed for speed and efficiency through strategic caching.

### ✨ Key Features
- **Detailed News Search**: Perform sophisticated news searches by combining keywords, specific sections, and date ranges.
- **News Trend Analysis**: Track the volume of news coverage for any topic over time with time-series data.
- **Related Topic Analysis**: Discover related keywords and context by analyzing the most frequent tags in search results.
- **Full Article Text Extraction**: Scrape the full text content from any article URL.
- **High-Performance Caching**: Minimizes API calls and improves response speed with data-specific caches.

### 🛠️ Tech Stack
- **MCP Framework**: FastMCP
- **Data Validation**: Pydantic
- **HTTP Client**: Requests
- **Web Scraping**: BeautifulSoup4, lxml
- **Caching**: cachetools
- **Date Utilities**: python-dateutil
- **Environment**: Python-dotenv

### 🚀 Installation & Setup
1) Install Dependencies

```bash
pip install -r requirements.txt
```

> Note: If you use uv, you can install dependencies with `uv sync`.

2) Set Up Environment Variables

Create a `.env` file in the project's root directory and set your Guardian API key.

```env
GUARDIAN_API_KEY=your_guardian_api_key_here
```

You can get a free API key from The Guardian Open Platform.

3) Run the Server

```bash
python -m src.main
```

### 🧰 Available Tools (API Reference)

#### health
- **Description**: Checks the current status of the service and API key configuration.
- **Parameters**: None
- **Returns**: Service status object

#### search_news_tool
- **Description**: Searches for news articles using various conditions.
- **Parameters**:
  - `query` (string, required): The keyword to search for.
  - `page_size` (integer, optional): Number of articles (Default: 5, Max: 50).
  - `section` (string, optional): Section to search within (e.g., `technology`).
  - `from_date` (string, optional): Start date (YYYY-MM-DD).
  - `to_date` (string, optional): End date (YYYY-MM-DD).
- **Returns**: Array of article objects

#### get_sections_tool
- **Description**: Retrieves a list of all available news sections for searching.
- **Parameters**: None
- **Returns**: Array of section objects

#### get_full_article_text_tool
- **Description**: Extracts the full body text from a given article URL.
- **Parameters**:
  - `url` (string, required): Full URL of the article to scrape.
- **Returns**: Object containing the article URL and its full text

#### get_news_trend_tool
- **Description**: Analyzes the monthly news coverage trend for a specific keyword.
- **Parameters**:
  - `query` (string, required): Keyword to analyze.
  - `start_date` (string, required): Start date (YYYY-MM-DD).
  - `end_date` (string, required): End date (YYYY-MM-DD).
- **Returns**: Array of objects `{ period: YYYY-MM, article_count: number }`

#### get_related_topics_tool
- **Description**: Analyzes and returns the most frequent related topics (tags) for a given keyword.
- **Parameters**:
  - `query` (string, required): Keyword to analyze.
  - `page_size` (integer, optional): Number of recent articles to analyze (Default: 20).
- **Returns**: Array of `{ topic, count }`

#### get_tool_definitions
- **Description**: Provides the JSON definitions for all tools currently available on the server.
- **Parameters**: None

### 📁 Project Structure

```text
mcp-guardian-news/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main MCP server file
│   └── tools.py         # Tools for calling the Guardian API
├── .env                 # Environment variables file (API Key, etc.)
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── .gitignore           # Git ignore file
└── README.md            # Project documentation
```

### 📄 License
This project is licensed under the MIT License.