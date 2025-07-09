from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SearchRequest(BaseModel):
    prompt: str
    ticker: str

class CompanyOverview(BaseModel):
    name: str
    ticker: str
    sector: str
    marketCap: str
    price: str
    change: str

class Financials(BaseModel):
    revenue: str
    netIncome: str
    eps: str
    peRatio: str

class ReportData(BaseModel):
    overview: CompanyOverview
    financials: Financials
    analysis: str

class ResearchReport(BaseModel):
    id: str
    companyName: str
    timestamp: str
    data: ReportData