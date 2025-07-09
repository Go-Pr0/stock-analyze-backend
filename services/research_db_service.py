from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List, Optional
from models.research_models import ResearchReport as ResearchReportModel
from models.schemas import ResearchReport, ReportData, CompanyOverview, Financials, CompetitiveAnalysis, CompetitorData
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
        
        # Prepare competitive analysis data for JSON storage
        global_competitors_json = None
        national_competitors_json = None
        
        if report.data.competitive:
            if report.data.competitive.global_competitors:
                global_competitors_json = [comp.dict() for comp in report.data.competitive.global_competitors]
            if report.data.competitive.national_competitors:
                national_competitors_json = [comp.dict() for comp in report.data.competitive.national_competitors]
        
        # Create the base report data
        report_data = {
            'id': report.id,
            'user_id': user_id,
            'company_name': report.companyName,
            'ticker': report.data.overview.ticker,
            'prompt': prompt,
            'sector': report.data.overview.sector,
            'market_cap': report.data.overview.marketCap,
            'price': report.data.overview.price,
            'change': report.data.overview.change,
            'revenue': report.data.financials.revenue,
            'net_income': report.data.financials.netIncome,
            'eps': report.data.financials.eps,
            'pe_ratio': report.data.financials.peRatio,
            'analysis': report.data.analysis
        }
        
        # Try to add competitive analysis columns if they exist
        try:
            report_data['global_competitors'] = global_competitors_json
            report_data['national_competitors'] = national_competitors_json
            db_report = ResearchReportModel(**report_data)
        except Exception as e:
            # If the columns don't exist, create without them
            print(f"⚠️ Competitive analysis columns not available, creating report without them: {e}")
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
        try:
            # Try to query with all columns including competitive analysis
            query = db.query(ResearchReportModel).filter(
                ResearchReportModel.user_id == user_id
            ).order_by(ResearchReportModel.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.offset(offset).all()
            
        except OperationalError as e:
            if "does not exist" in str(e):
                print("⚠️ Competitive analysis columns don't exist yet, querying without them")
                # Fallback: query without the competitive analysis columns
                return ResearchDBService._get_user_research_reports_legacy(db, user_id, limit, offset)
            else:
                raise e
    
    @staticmethod
    def _get_user_research_reports_legacy(
        db: Session,
        user_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ResearchReportModel]:
        """Legacy method to get research reports without competitive analysis columns"""
        from sqlalchemy import text
        
        # Build the SQL query manually to avoid the missing columns
        sql = """
        SELECT id, user_id, company_name, ticker, prompt, sector, market_cap, 
               price, change, revenue, net_income, eps, pe_ratio, analysis, 
               created_at, updated_at
        FROM research_reports 
        WHERE user_id = :user_id 
        ORDER BY created_at DESC
        """
        
        if limit:
            sql += f" LIMIT {limit}"
        sql += f" OFFSET {offset}"
        
        result = db.execute(text(sql), {"user_id": user_id})
        rows = result.fetchall()
        
        # Convert rows to ResearchReportModel objects
        reports = []
        for row in rows:
            # Create a mock object with the available data
            report = type('ResearchReportModel', (), {})()
            report.id = row[0]
            report.user_id = row[1]
            report.company_name = row[2]
            report.ticker = row[3]
            report.prompt = row[4]
            report.sector = row[5]
            report.market_cap = row[6]
            report.price = row[7]
            report.change = row[8]
            report.revenue = row[9]
            report.net_income = row[10]
            report.eps = row[11]
            report.pe_ratio = row[12]
            report.analysis = row[13]
            report.created_at = row[14]
            report.updated_at = row[15]
            # Set competitive analysis fields to None for legacy reports
            report.global_competitors = None
            report.national_competitors = None
            reports.append(report)
        
        return reports
    
    @staticmethod
    def get_research_report_by_id(
        db: Session,
        report_id: str,
        user_id: int
    ) -> Optional[ResearchReportModel]:
        """Get a specific research report by ID for a user"""
        try:
            return db.query(ResearchReportModel).filter(
                ResearchReportModel.id == report_id,
                ResearchReportModel.user_id == user_id
            ).first()
        except OperationalError as e:
            if "does not exist" in str(e):
                print("⚠️ Competitive analysis columns don't exist yet, querying without them")
                return ResearchDBService._get_research_report_by_id_legacy(db, report_id, user_id)
            else:
                raise e
    
    @staticmethod
    def _get_research_report_by_id_legacy(
        db: Session,
        report_id: str,
        user_id: int
    ) -> Optional[ResearchReportModel]:
        """Legacy method to get a research report by ID without competitive analysis columns"""
        from sqlalchemy import text
        
        sql = """
        SELECT id, user_id, company_name, ticker, prompt, sector, market_cap, 
               price, change, revenue, net_income, eps, pe_ratio, analysis, 
               created_at, updated_at
        FROM research_reports 
        WHERE id = :report_id AND user_id = :user_id
        """
        
        result = db.execute(text(sql), {"report_id": report_id, "user_id": user_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        # Create a mock object with the available data
        report = type('ResearchReportModel', (), {})()
        report.id = row[0]
        report.user_id = row[1]
        report.company_name = row[2]
        report.ticker = row[3]
        report.prompt = row[4]
        report.sector = row[5]
        report.market_cap = row[6]
        report.price = row[7]
        report.change = row[8]
        report.revenue = row[9]
        report.net_income = row[10]
        report.eps = row[11]
        report.pe_ratio = row[12]
        report.analysis = row[13]
        report.created_at = row[14]
        report.updated_at = row[15]
        # Set competitive analysis fields to None for legacy reports
        report.global_competitors = None
        report.national_competitors = None
        
        return report
    
    @staticmethod
    def delete_research_report(
        db: Session,
        report_id: str,
        user_id: int
    ) -> bool:
        """Delete a research report"""
        try:
            report = db.query(ResearchReportModel).filter(
                ResearchReportModel.id == report_id,
                ResearchReportModel.user_id == user_id
            ).first()
            
            if report:
                db.delete(report)
                db.commit()
                return True
            return False
        except OperationalError as e:
            if "does not exist" in str(e):
                # Use raw SQL for deletion if columns don't exist
                from sqlalchemy import text
                result = db.execute(
                    text("DELETE FROM research_reports WHERE id = :report_id AND user_id = :user_id"),
                    {"report_id": report_id, "user_id": user_id}
                )
                db.commit()
                return result.rowcount > 0
            else:
                raise e
    
    @staticmethod
    def convert_db_to_schema(db_report: ResearchReportModel) -> ResearchReport:
        """Convert database model to Pydantic schema"""
        
        # Reconstruct competitive analysis from JSON data (if available)
        competitive_analysis = None
        
        # Check if the report has competitive analysis data
        global_competitors_data = getattr(db_report, 'global_competitors', None)
        national_competitors_data = getattr(db_report, 'national_competitors', None)
        
        if global_competitors_data or national_competitors_data:
            global_competitors = []
            national_competitors = []
            
            if global_competitors_data:
                try:
                    global_competitors = [CompetitorData(**comp) for comp in global_competitors_data]
                except Exception as e:
                    print(f"⚠️ Error parsing global competitors data: {e}")
            
            if national_competitors_data:
                try:
                    national_competitors = [CompetitorData(**comp) for comp in national_competitors_data]
                except Exception as e:
                    print(f"⚠️ Error parsing national competitors data: {e}")
            
            if global_competitors or national_competitors:
                competitive_analysis = CompetitiveAnalysis(
                    global_competitors=global_competitors,
                    national_competitors=national_competitors
                )
        
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
                analysis=db_report.analysis or "",
                competitive=competitive_analysis
            )
        )