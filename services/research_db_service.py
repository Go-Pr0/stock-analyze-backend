from sqlalchemy.orm import Session
from typing import List, Optional
from models.research_models import ResearchReport as ResearchReportModel
from models.schemas import ResearchReport, ReportData, CompanyOverview, Financials
import uuid

class ResearchDBService:
    @staticmethod
    def create_research_report(
        db: Session,
        user_id: int,
        report: ResearchReport,
        prompt: str = ""
    ) -> ResearchReportModel:
        """Save a research report to the database"""
        
        db_report = ResearchReportModel(
            id=report.id,
            user_id=user_id,
            company_name=report.companyName,
            ticker=report.data.overview.ticker,
            prompt=prompt,
            sector=report.data.overview.sector,
            market_cap=report.data.overview.marketCap,
            price=report.data.overview.price,
            change=report.data.overview.change,
            revenue=report.data.financials.revenue,
            net_income=report.data.financials.netIncome,
            eps=report.data.financials.eps,
            pe_ratio=report.data.financials.peRatio,
            analysis=report.data.analysis
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report
    
    @staticmethod
    def get_user_research_reports(
        db: Session,
        user_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ResearchReportModel]:
        """Get research reports for a specific user"""
        query = db.query(ResearchReportModel).filter(
            ResearchReportModel.user_id == user_id
        ).order_by(ResearchReportModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.offset(offset).all()
    
    @staticmethod
    def get_research_report_by_id(
        db: Session,
        report_id: str,
        user_id: int
    ) -> Optional[ResearchReportModel]:
        """Get a specific research report by ID for a user"""
        return db.query(ResearchReportModel).filter(
            ResearchReportModel.id == report_id,
            ResearchReportModel.user_id == user_id
        ).first()
    
    @staticmethod
    def delete_research_report(
        db: Session,
        report_id: str,
        user_id: int
    ) -> bool:
        """Delete a research report"""
        report = db.query(ResearchReportModel).filter(
            ResearchReportModel.id == report_id,
            ResearchReportModel.user_id == user_id
        ).first()
        
        if report:
            db.delete(report)
            db.commit()
            return True
        return False
    
    @staticmethod
    def convert_db_to_schema(db_report: ResearchReportModel) -> ResearchReport:
        """Convert database model to Pydantic schema"""
        return ResearchReport(
            id=db_report.id,
            companyName=db_report.company_name,
            timestamp=db_report.created_at.isoformat(),
            data=ReportData(
                overview=CompanyOverview(
                    name=db_report.company_name,
                    ticker=db_report.ticker,
                    sector=db_report.sector or "",
                    marketCap=db_report.market_cap or "",
                    price=db_report.price or "",
                    change=db_report.change or ""
                ),
                financials=Financials(
                    revenue=db_report.revenue or "",
                    netIncome=db_report.net_income or "",
                    eps=db_report.eps or "",
                    peRatio=db_report.pe_ratio or ""
                ),
                analysis=db_report.analysis or ""
            )
        )