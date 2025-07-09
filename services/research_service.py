import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from .stock_data import fetch_stock_summary
from .generate import setup_initial_questions, analyze_all_branches_async, structure_findings
from .competitor_service import CompetitorAnalysisService
from models.schemas import ResearchReport, ReportData, CompanyOverview, Financials, CompetitorData, CompetitiveAnalysis


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
            
            # Step 2: Run AI analysis and competitive analysis in parallel
            company_name = prompt if prompt else (stock_data['data']['overview']['name'] if stock_data else ticker)
            
            # Start both tasks concurrently
            analysis_task = ResearchService._generate_ai_analysis(company_name)
            competitive_task = ResearchService._generate_competitive_analysis(ticker) if ticker and ticker.strip() else None
            
            # Wait for both to complete
            if competitive_task:
                analysis_text, competitive_analysis = await asyncio.gather(
                    analysis_task,
                    competitive_task,
                    return_exceptions=True
                )
                
                # Handle exceptions from competitive analysis
                if isinstance(competitive_analysis, Exception):
                    print(f"⚠ Competitive analysis failed: {competitive_analysis}")
                    competitive_analysis = None
            else:
                analysis_text = await analysis_task
                competitive_analysis = None
            
            # Handle exception from main analysis
            if isinstance(analysis_text, Exception):
                print(f"⚠ Main analysis failed: {analysis_text}")
                analysis_text = f"Analysis temporarily unavailable. Error: {str(analysis_text)}"
            
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
                        analysis=analysis_text,
                        competitive=competitive_analysis
                    )
                )
            else:
                # Fallback to mock data with AI analysis
                report = ResearchService._create_mock_report_with_analysis(company_name, analysis_text, competitive_analysis)
            
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
    async def _generate_competitive_analysis(ticker: str) -> Optional[CompetitiveAnalysis]:
        """Generate competitive analysis by finding both global and national competitors and fetching their data"""
        try:
            print(f"🏁 Generating competitive analysis for: {ticker}")
            
            # Step 1: Get both global and national competitor tickers
            competitors_dict = await CompetitorAnalysisService.get_global_and_national_competitors(ticker.upper())
            global_tickers = competitors_dict.get("global_competitors", [])
            national_tickers = competitors_dict.get("national_competitors", [])
            
            if not global_tickers and not national_tickers:
                print(f"⚠ No competitors found for {ticker}")
                return None
            
            print(f"✓ Found {len(global_tickers)} global competitors: {global_tickers}")
            print(f"✓ Found {len(national_tickers)} national competitors: {national_tickers}")
            
            # Step 2: Fetch stock data for global competitors
            global_competitor_data = []
            for comp_ticker in global_tickers:
                try:
                    stock_data = fetch_stock_summary(comp_ticker)
                    global_competitor_data.append(CompetitorData(
                        ticker=comp_ticker,
                        name=stock_data['data']['overview']['name'],
                        sector=stock_data['data']['overview']['sector'],
                        marketCap=stock_data['data']['overview']['marketCap'],
                        price=stock_data['data']['overview']['price'],
                        change=stock_data['data']['overview']['change'],
                        revenue=stock_data['data']['financials']['revenue'],
                        netIncome=stock_data['data']['financials']['netIncome'],
                        eps=stock_data['data']['financials']['eps'],
                        peRatio=stock_data['data']['financials']['peRatio']
                    ))
                    print(f"✓ Fetched data for global competitor: {comp_ticker}")
                except Exception as e:
                    print(f"⚠ Could not fetch data for global competitor {comp_ticker}: {e}")
                    continue
            
            # Step 3: Fetch stock data for national competitors
            national_competitor_data = []
            for comp_ticker in national_tickers:
                try:
                    stock_data = fetch_stock_summary(comp_ticker)
                    national_competitor_data.append(CompetitorData(
                        ticker=comp_ticker,
                        name=stock_data['data']['overview']['name'],
                        sector=stock_data['data']['overview']['sector'],
                        marketCap=stock_data['data']['overview']['marketCap'],
                        price=stock_data['data']['overview']['price'],
                        change=stock_data['data']['overview']['change'],
                        revenue=stock_data['data']['financials']['revenue'],
                        netIncome=stock_data['data']['financials']['netIncome'],
                        eps=stock_data['data']['financials']['eps'],
                        peRatio=stock_data['data']['financials']['peRatio']
                    ))
                    print(f"✓ Fetched data for national competitor: {comp_ticker}")
                except Exception as e:
                    print(f"⚠ Could not fetch data for national competitor {comp_ticker}: {e}")
                    continue
            
            if global_competitor_data or national_competitor_data:
                print(f"✓ Successfully fetched data for {len(global_competitor_data)} global and {len(national_competitor_data)} national competitors")
                return CompetitiveAnalysis(
                    global_competitors=global_competitor_data,
                    national_competitors=national_competitor_data
                )
            else:
                print(f"⚠ No competitor data could be fetched")
                return None
                
        except Exception as e:
            print(f"❌ Error in competitive analysis: {e}")
            return None
    
    @staticmethod
    async def mock_generate_research_report(prompt: str, ticker: str) -> ResearchReport:
        """
        MOCK AI: Generate a research report with real stock data and MOCK AI analysis. ONLY AI IS MOCKED
        
        Args:
            prompt: Company name or research prompt
            ticker: Stock ticker symbol
            
        Returns:
            ResearchReport: Complete research report in the format expected by frontend
        """
        print("--- MOCK AI: Generating report with real stock data ---")
        
        # Step 1: Get real stock data if ticker is provided
        stock_data = None
        if ticker and ticker.strip():
            try:
                stock_data = fetch_stock_summary(ticker.upper())
                print(f"✓ Fetched real stock data for {ticker}")
            except Exception as e:
                print(f"⚠ Could not fetch stock data for {ticker}: {e}")
        
        # Simulate a small delay for perceived AI generation
        await asyncio.sleep(1)

        # Step 2: Use a mock analysis text and generate competitive analysis
        company_name_for_analysis = prompt or (stock_data['data']['overview']['name'] if stock_data else ticker)
        mock_analysis_text = f"""
## Executive Summary (Mock Analysis)

This is a mock AI analysis for **{company_name_for_analysis}**. The financial data below is real, but this text is a placeholder for development and testing purposes.

### Key Findings (Mock):
* **Market Position:** The company is presented as a leader in its sector for testing.
* **Financial Health:** Real-time financial data is included below.
* **Future Outlook:** This section is a mock-up and does not represent a real forecast.

This report for **{ticker}** was generated using real-time financial data combined with a simulated AI analysis to facilitate testing.
        """
        
        # Step 2.5: Generate competitive analysis in parallel (but start after mock delay)
        competitive_analysis = None
        if ticker and ticker.strip():
            try:
                competitive_analysis = await ResearchService._generate_competitive_analysis(ticker)
            except Exception as e:
                print(f"⚠ Competitive analysis failed in mock mode: {e}")

        # Step 3: Construct the final report
        if stock_data:
            # Use real stock data as base and add mock AI analysis
            report = ResearchReport(
                id=stock_data['id'],
                companyName=stock_data['companyName'],
                timestamp=stock_data['timestamp'],
                data=ReportData(
                    overview=CompanyOverview(**stock_data['data']['overview']),
                    financials=Financials(**stock_data['data']['financials']),
                    analysis=mock_analysis_text,
                    competitive=competitive_analysis
                )
            )
        else:
            # Fallback to a fully mock report if stock data fails
            print("--- MOCK AI: Could not fetch real data, falling back to fully mock report ---")
            report = ResearchService._create_mock_report_with_analysis(prompt, mock_analysis_text, competitive_analysis)
            
        print("--- MOCK AI: Report generated successfully ---")
        
        return report

    @staticmethod
    def _create_mock_report_with_analysis(company_name: str, analysis: str, competitive_analysis: Optional[CompetitiveAnalysis] = None) -> ResearchReport:
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
                analysis=analysis,
                competitive=competitive_analysis
            )
        )