# Stock Research API Backend

A comprehensive FastAPI backend that combines real-time stock data with AI-powered research analysis.

## Features

- **Real Stock Data**: Fetches live financial data using yfinance
- **AI Research**: Generates comprehensive company analysis using Google Gemini AI
- **Structured Reports**: Returns data in the exact format expected by the frontend
- **Async Processing**: Handles multiple research branches concurrently
- **CORS Enabled**: Ready for frontend integration

## Architecture

```
backend/
├── api/                    # API route handlers
│   ├── __init__.py
│   └── research.py        # Research endpoints
├── models/                # Data models and schemas
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
├── services/              # Business logic
│   ├── __init__.py
│   ├── constructor.py     # Report construction
│   ├── generate.py        # AI research generation
│   ├── prompt.py          # AI prompts
│   ├── research_service.py # Main orchestration service
│   └── stock_data.py      # Stock data fetching
├── main.py               # FastAPI application
├── start.py              # Startup script
├── requirements.txt      # Dependencies
└── .env                  # Environment variables
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your Google Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Start the Server

```bash
python start.py
```

Or directly:

```bash
python main.py
```

The API will be available at:
- **Server**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### POST /api/research
Generate a comprehensive research report for a company.

**Request Body:**
```json
{
  "prompt": "Apple Inc.",
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "companyName": "Apple Inc.",
  "timestamp": "2023-03-15T12:00:00Z",
  "data": {
    "overview": {
      "name": "Apple Inc.",
      "ticker": "AAPL",
      "sector": "Technology",
      "marketCap": "$2.6T",
      "price": "$165.23",
      "change": "+1.21%"
    },
    "financials": {
      "revenue": "$394.3B",
      "netIncome": "$99.8B",
      "eps": "$6.16",
      "peRatio": "26.8"
    },
    "analysis": "Comprehensive AI-generated analysis..."
  }
}
```

### GET /api/research
Get research history (last 10 reports by default).

### GET /api/research/{report_id}
Get a specific research report by ID.

### DELETE /api/research/{report_id}
Delete a research report.

## How It Works

1. **Request Processing**: Frontend sends company name and ticker
2. **Stock Data Fetching**: Real financial data retrieved via yfinance
3. **AI Research Generation**:
   - Generate research branches using Gemini AI
   - Analyze each branch with web search grounding
   - Synthesize findings into comprehensive report
4. **Report Construction**: Combine stock data with AI analysis
5. **Response**: Return structured report to frontend

## Services

### ResearchService
Main orchestration service that coordinates:
- Stock data fetching
- AI analysis generation
- Report construction

### Stock Data Service
- Fetches real-time stock data using yfinance
- Formats data for frontend consumption
- Handles missing or invalid tickers gracefully

### AI Generation Service
- Uses Google Gemini AI with web search grounding
- Generates research branches for comprehensive analysis
- Processes multiple research areas concurrently
- Synthesizes findings into final report

## Error Handling

The backend includes comprehensive error handling:
- Graceful fallbacks when stock data is unavailable
- Mock data generation when real data fails
- AI analysis fallbacks for API issues
- Detailed error logging for debugging

## Development

### Running in Development Mode

```bash
python start.py
```

This enables:
- Auto-reload on file changes
- Detailed logging
- CORS for frontend development

### Testing

Test the API using the interactive documentation at http://localhost:8000/docs

### Adding New Features

1. **New Endpoints**: Add to `api/research.py`
2. **Data Models**: Update `models/schemas.py`
3. **Business Logic**: Add to appropriate service in `services/`
4. **AI Prompts**: Update `services/prompt.py`

## Environment Variables

- `GEMINI_API_KEY`: Required for AI research generation
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

## Dependencies

- **FastAPI**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **yfinance**: Stock data
- **google-genai**: AI research
- **python-dotenv**: Environment management

## Production Deployment

For production deployment:

1. Set up proper database instead of in-memory storage
2. Configure environment variables securely
3. Set up proper logging and monitoring
4. Use production ASGI server configuration
5. Implement rate limiting and authentication as needed