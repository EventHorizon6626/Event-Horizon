"""
FastAPI server to expose AI agents as REST API endpoints.
Connects the frontend to the AI analysis agents.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Import existing agents
from agents.news_agent import NewsAgent
from agents.report_agent import ReportAnalysisAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Event Horizon AI API",
    description="AI-powered portfolio analysis API",
    version="1.0.0"
)

# CORS configuration - allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:80",    # Production frontend
        "http://frontend:3000",   # Docker network
        os.getenv("FRONTEND_URL", "")  # Configurable via env
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class PortfolioAnalysisRequest(BaseModel):
    stocks: List[str]

    class Config:
        schema_extra = {
            "example": {
                "stocks": ["AAPL", "TSLA", "GOOGL"]
            }
        }

class PortfolioAnalysisResponse(BaseModel):
    portfolio: List[str]
    analysis_timestamp: str
    news_data: Dict[str, Any]
    report_data: Dict[str, Any]
    summary: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "event-horizon-ai"
    }

# Main portfolio analysis endpoint
@app.post("/api/portfolio/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """
    Analyze a portfolio of stocks using AI agents.

    This endpoint:
    1. Validates the stock symbols
    2. Runs NewsAgent to fetch recent news
    3. Runs ReportAnalysisAgent to fetch financial data
    4. Returns combined analysis results
    """
    try:
        logger.info(f"Starting portfolio analysis for stocks: {request.stocks}")

        if not request.stocks or len(request.stocks) == 0:
            raise HTTPException(
                status_code=400,
                detail="No stocks provided. Please provide at least one stock symbol."
            )

        # Initialize agents
        news_agent = NewsAgent(
            name="NewsAgent",
            description="Fetches financial news for portfolio stocks"
        )

        report_agent = ReportAnalysisAgent(
            name="ReportAnalysisAgent",
            description="Analyzes financial reports and metrics"
        )

        # Execute agents with portfolio stocks
        logger.info("Executing NewsAgent...")
        news_result = news_agent.execute(symbols=request.stocks)

        logger.info("Executing ReportAnalysisAgent...")
        report_result = report_agent.execute(symbols=request.stocks)

        # Build summary statistics
        summary = {
            "total_stocks": len(request.stocks),
            "stocks_analyzed": request.stocks,
            "news_articles_count": len(news_result.get("data", {}).get("articles", [])) if news_result.get("success") else 0,
            "reports_fetched": len(report_result.get("data", {}).get("reports", {})) if report_result.get("success") else 0,
            "analysis_status": "completed"
        }

        # Check for errors
        errors = []
        if not news_result.get("success"):
            errors.append(f"News analysis: {news_result.get('error', 'Unknown error')}")
        if not report_result.get("success"):
            errors.append(f"Report analysis: {report_result.get('error', 'Unknown error')}")

        if errors:
            summary["warnings"] = errors

        logger.info(f"Portfolio analysis completed successfully for {len(request.stocks)} stocks")

        return PortfolioAnalysisResponse(
            portfolio=request.stocks,
            analysis_timestamp=datetime.now().isoformat(),
            news_data=news_result,
            report_data=report_result,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio analysis failed: {str(e)}"
        )

# Get news for specific stocks
@app.post("/api/news")
async def get_news(request: PortfolioAnalysisRequest):
    """Get news articles for specific stock symbols."""
    try:
        logger.info(f"Fetching news for stocks: {request.stocks}")

        news_agent = NewsAgent(
            name="NewsAgent",
            description="Fetches financial news"
        )

        result = news_agent.execute(symbols=request.stocks)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to fetch news")
            )

        return result

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"News fetch failed: {str(e)}"
        )

# Get financial reports for specific stocks
@app.post("/api/reports")
async def get_reports(request: PortfolioAnalysisRequest):
    """Get financial reports and metrics for specific stock symbols."""
    try:
        logger.info(f"Fetching reports for stocks: {request.stocks}")

        report_agent = ReportAnalysisAgent(
            name="ReportAnalysisAgent",
            description="Fetches financial reports"
        )

        result = report_agent.execute(symbols=request.stocks)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to fetch reports")
            )

        return result

    except Exception as e:
        logger.error(f"Error fetching reports: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Report fetch failed: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint with service information."""
    return {
        "service": "Event Horizon AI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze_portfolio": "/api/portfolio/analyze",
            "get_news": "/api/news",
            "get_reports": "/api/reports",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "4000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"

    logger.info(f"Starting Event Horizon AI API on {host}:{port}")

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
