# Stock Research API Backend

A comprehensive FastAPI backend that combines real-time stock data with AI-powered research analysis. For detailed setup and deployment instructions, please see the root `README.md` and other documentation files.

## Architecture

```
backend/
├── api/                    # API route handlers
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   └── research.py        # Research endpoints
├── models/                # Data models and schemas
│   ├── __init__.py
│   ├── schemas.py         # Pydantic models
│   └── user_models.py     # User and token models
├── services/              # Business logic
│   ├── __init__.py
│   ├── generate.py        # AI research generation
│   ├── prompt.py          # AI prompts
│   ├── research_service.py # Main orchestration service
│   └── stock_data.py      # Stock data fetching
├── main.py               # FastAPI application
├── start.sh              # Production startup script
├── requirements.txt      # Dependencies
└── .env                  # Environment variables
```

## API Endpoints

For a full list of API endpoints and their usage, please refer to the `AUTH_SETUP.md` documentation and the interactive API documentation at `/docs` when the server is running.

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