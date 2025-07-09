from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from models.schemas import SearchRequest, ResearchReport, User
from services.research_service import ResearchService
from services.research_db_service import ResearchDBService
from auth import get_current_active_user
from database import get_db

router = APIRouter(prefix="/api", tags=["research"])

@router.post("/research", response_model=ResearchReport)
async def create_research_report(
    request: SearchRequest, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a comprehensive research report for a company"""
    try:
        print(f"📊 Generating research report for: {request.prompt} ({request.ticker})")
        
        # MOCK IMPLEMENTATION: Use the mock service to generate a report with real data and mock AI
        report = await ResearchService.mock_generate_research_report(
            prompt=request.prompt,
            ticker=request.ticker
        )
        
        # ORIGINAL IMPLEMENTATION (commented out for testing)
        # report = await ResearchService.generate_research_report(
        #     prompt=request.prompt,
        #     ticker=request.ticker
        # )
        
        # Save to database
        db_report = ResearchDBService.create_research_report(
            db=db,
            user_id=current_user.id,
            report=report,
            prompt=request.prompt
        )
        
        print(f"✅ Research report generated and saved for user {current_user.id}")
        return report
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/research", response_model=List[ResearchReport])
async def get_research_history(
    limit: Optional[int] = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get research history for the current user"""
    try:
        db_reports = ResearchDBService.get_user_research_reports(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        # Convert database models to Pydantic schemas
        reports = [ResearchDBService.convert_db_to_schema(db_report) for db_report in db_reports]
        return reports
        
    except Exception as e:
        print(f"❌ Error fetching research history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching research history: {str(e)}")

@router.get("/research/{report_id}", response_model=ResearchReport)
async def get_research_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific research report by ID"""
    try:
        db_report = ResearchDBService.get_research_report_by_id(
            db=db,
            report_id=report_id,
            user_id=current_user.id
        )
        
        if not db_report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ResearchDBService.convert_db_to_schema(db_report)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching research report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching research report: {str(e)}")

@router.delete("/research/{report_id}")
async def delete_research_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a research report"""
    try:
        success = ResearchDBService.delete_research_report(
            db=db,
            report_id=report_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {"message": "Report deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting research report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting research report: {str(e)}")