from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Authentication Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Research Schemas
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

class CompetitorData(BaseModel):
    ticker: str
    name: str
    sector: str
    marketCap: str
    price: str
    change: str
    revenue: str
    netIncome: str
    eps: str
    peRatio: str

class CompetitiveAnalysis(BaseModel):
    competitors: List[CompetitorData]

class ReportData(BaseModel):
    overview: CompanyOverview
    financials: Financials
    analysis: str
    competitive: Optional[CompetitiveAnalysis] = None

class ResearchReport(BaseModel):
    id: str
    companyName: str
    timestamp: str
    data: ReportData