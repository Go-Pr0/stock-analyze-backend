from fastapi import APIRouter, HTTPException
from typing import List, Optional

from models.schemas import SearchRequest, ResearchReport
from services.research_service import ResearchService

router = APIRouter(prefix="/api", tags=["research"])

# In-memory storage (in production, use a proper database)
research_reports: List[ResearchReport] = []

@router.post("/research", response_model=ResearchReport)
async def create_research_report(request: SearchRequest):
    """Generate a comprehensive research report for a company"""
    try:
        print(f"📊 Generating research report for: {request.prompt} ({request.ticker})")
        
        # Generate comprehensive report using the research service
        report = await ResearchService.generate_research_report(
            prompt=request.prompt,
            ticker=request.ticker
        )
        
        # Store in memory (in production, save to database)
        research_reports.append(report)
        
        print(f"✅ Research report generated successfully for {request.prompt}")
        return report
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/research", response_model=List[ResearchReport])
async def get_research_history(limit: Optional[int] = 10):
    """Get research history"""
    return research_reports[-limit:] if limit else research_reports

@router.get("/research/{report_id}", response_model=ResearchReport)
async def get_research_report(report_id: str):
    """Get a specific research report by ID"""
    for report in research_reports:
        if report.id == report_id:
            return report
    raise HTTPException(status_code=404, detail="Report not found")

@router.delete("/research/{report_id}")
async def delete_research_report(report_id: str):
    """Delete a research report"""
    global research_reports
    research_reports = [r for r in research_reports if r.id != report_id]
    return {"message": "Report deleted successfully"}