from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String, primary_key=True, index=True)  # UUID string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    
    # Company Overview fields
    sector = Column(String)
    market_cap = Column(String)
    price = Column(String)
    change = Column(String)
    
    # Financial fields
    revenue = Column(String)
    net_income = Column(String)
    eps = Column(String)
    pe_ratio = Column(String)
    
    # Analysis
    analysis = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="research_reports")