import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from .stock_data import fetch_stock_summary
from .generate import setup_initial_questions, analyze_all_branches_async, structure_findings
from models.schemas import ResearchReport, ReportData, CompanyOverview, Financials


class ResearchService:
    """Service to orchestrate the complete research process"""
    
    @staticmethod
    async def generate_research_report(prompt: str, ticker: str) -> ResearchReport:
        """
        Generate a comprehensive research report combining real stock data and AI analysis
        
        Args:
            prompt: Company name or research prompt
            ticker: Stock ticker symbol
            
        Returns:
            ResearchReport: Complete research report in the format expected by frontend
        """
        try:
            # Step 1: Get real stock data if ticker is provided
            stock_data = None
            if ticker and ticker.strip():
                try:
                    stock_data = fetch_stock_summary(ticker.upper())
                    print(f"✓ Fetched stock data for {ticker}")
                except Exception as e:
                    print(f"⚠ Could not fetch stock data for {ticker}: {e}")
            
            # Step 2: Generate AI analysis
            company_name = prompt if prompt else (stock_data['data']['overview']['name'] if stock_data else ticker)
            analysis_text = await ResearchService._generate_ai_analysis(company_name)
            
            # Step 3: Construct the final report
            if stock_data:
                # Use real stock data as base
                report_data = stock_data
                # Add AI analysis
                report_data['data']['analysis'] = analysis_text
                
                # Create ResearchReport object
                report = ResearchReport(
                    id=report_data['id'],
                    companyName=report_data['companyName'],
                    timestamp=report_data['timestamp'],
                    data=ReportData(
                        overview=CompanyOverview(**report_data['data']['overview']),
                        financials=Financials(**report_data['data']['financials']),
                        analysis=analysis_text
                    )
                )
            else:
                # Fallback to mock data with AI analysis
                report = ResearchService._create_mock_report_with_analysis(company_name, analysis_text)
            
            return report
            
        except Exception as e:
            print(f"Error generating research report: {e}")
            # Return fallback mock report
            return ResearchService._create_mock_report_with_analysis(
                prompt or ticker, 
                f"Analysis temporarily unavailable. Error: {str(e)}"
            )
    
    @staticmethod
    async def _generate_ai_analysis(company_name: str) -> str:
        """Generate AI-powered analysis using the existing generate.py functionality"""
        try:
            print(f"🔍 Generating AI analysis for: {company_name}")
            
            # Step 1: Generate research branches
            topics = setup_initial_questions(company_name)
            if not topics:
                return f"Unable to generate detailed analysis for {company_name} at this time."
            
            print(f"✓ Generated {len(topics)} research branches")
            
            # Step 2: Analyze all branches
            all_findings = await analyze_all_branches_async(topics)
            if not all_findings:
                return f"Research completed for {company_name}, but no specific findings were collected."
            
            print(f"✓ Collected {len(all_findings)} findings")
            
            # Step 3: Structure findings into final report
            final_analysis = structure_findings(company_name, all_findings)
            print(f"✓ Generated final analysis")
            
            return final_analysis
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return f"AI analysis for {company_name} is temporarily unavailable due to technical issues."
    
    @staticmethod
    def _create_mock_report_with_analysis(company_name: str, analysis: str) -> ResearchReport:
        """Create a mock report when real stock data is unavailable"""
        now = datetime.now(timezone.utc)
        
        # Mock data variations based on company name
        mock_data = {
            "Apple": {
                "ticker": "AAPL",
                "sector": "Technology",
                "marketCap": "$2.8T",
                "price": "$185.92",
                "change": "+1.24%",
                "revenue": "$394.3B",
                "netIncome": "$99.8B",
                "eps": "$6.16",
                "peRatio": "30.2"
            },
            "Microsoft": {
                "ticker": "MSFT",
                "sector": "Technology",
                "marketCap": "$2.4T",
                "price": "$338.11",
                "change": "+0.87%",
                "revenue": "$211.9B",
                "netIncome": "$72.4B",
                "eps": "$9.65",
                "peRatio": "35.0"
            },
            "Tesla": {
                "ticker": "TSLA",
                "sector": "Automotive",
                "marketCap": "$800B",
                "price": "$248.50",
                "change": "-2.15%",
                "revenue": "$96.8B",
                "netIncome": "$15.0B",
                "eps": "$4.73",
                "peRatio": "52.5"
            }
        }
        
        # Use specific data if available, otherwise generate generic data
        if company_name in mock_data:
            data = mock_data[company_name]
        else:
            data = {
                "ticker": company_name[:4].upper() if len(company_name) >= 4 else "UNKN",
                "sector": "Technology",
                "marketCap": "$1.2T",
                "price": "$150.00",
                "change": "+1.50%",
                "revenue": "$200.0B",
                "netIncome": "$50.0B",
                "eps": "$5.00",
                "peRatio": "30.0"
            }
        
        return ResearchReport(
            id=str(uuid.uuid4()),
            companyName=company_name,
            timestamp=now.isoformat().replace("+00:00", "Z"),
            data=ReportData(
                overview=CompanyOverview(
                    name=company_name,
                    ticker=data["ticker"],
                    sector=data["sector"],
                    marketCap=data["marketCap"],
                    price=data["price"],
                    change=data["change"]
                ),
                financials=Financials(
                    revenue=data["revenue"],
                    netIncome=data["netIncome"],
                    eps=data["eps"],
                    peRatio=data["peRatio"]
                ),
                analysis=analysis
            )
        )