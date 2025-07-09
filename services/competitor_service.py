import os
import json
import re
from typing import List, Optional, Dict
from pydantic import BaseModel
from google import genai
from google.genai import types
from .prompt import get_global_competitor_prompt

# Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("The GEMINI_API_KEY environment variable is not set. Please set it in your deployment environment (e.g., Railway).")

client = genai.Client(api_key=GEMINI_API_KEY)

class CompetitorAnalysisService:
    """Service to find competitor companies for a given ticker using AI with Google grounding"""
    
    @staticmethod
    async def get_competitor_tickers(ticker: str) -> List[str]:
        """
        DEPRECATED: Use get_global_and_national_competitors instead.
        Get the top 5 competitor tickers for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            List[str]: List of competitor ticker symbols
        """
        result = await CompetitorAnalysisService.get_global_and_national_competitors(ticker)
        return result.get("global_competitors", [])
    
    @staticmethod
    async def get_global_and_national_competitors(ticker: str) -> Dict[str, List[str]]:
        """
        Get both global and national competitors for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dict[str, List[str]]: Dictionary with 'global_competitors' and 'national_competitors' keys
        """
        try:
            print(f"🔍 Finding global and national competitors for {ticker}...")
            
            # Use the updated prompt that returns both global and national competitors
            prompt = get_global_competitor_prompt(ticker)
            
            # Try with Google grounding first
            try:
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                config = types.GenerateContentConfig(
                    tools=[grounding_tool]
                )
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-05-20",
                    contents=prompt,
                    config=config,
                )
                
                competitors = CompetitorAnalysisService._extract_global_national_competitors_from_response(response.text)
                if competitors:
                    print(f"✓ Found global: {len(competitors.get('global_competitors', []))} competitors, national: {len(competitors.get('national_competitors', []))} competitors")
                    return competitors
                
            except Exception as e:
                if "Search Grounding is not supported" in str(e):
                    print("Search grounding not supported, trying google_search_retrieval...")
                    
                    # Fallback to google_search_retrieval
                    try:
                        grounding_tool = types.Tool(
                            google_search_retrieval=types.GoogleSearchRetrieval()
                        )
                        config = types.GenerateContentConfig(
                            tools=[grounding_tool]
                        )
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-pro-preview-06-05",
                            contents=prompt,
                            config=config,
                        )
                        
                        competitors = CompetitorAnalysisService._extract_global_national_competitors_from_response(response.text)
                        if competitors:
                            print(f"✓ Found global: {len(competitors.get('global_competitors', []))} competitors, national: {len(competitors.get('national_competitors', []))} competitors")
                            return competitors
                            
                    except Exception as e2:
                        print(f"google_search_retrieval failed: {e2}")
                        # Fall through to no-grounding fallback
                
                # Final fallback: no grounding
                print("Using model without grounding...")
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-05-20",
                    contents=prompt,
                )
                
                competitors = CompetitorAnalysisService._extract_global_national_competitors_from_response(response.text)
                if competitors:
                    print(f"✓ Found global: {len(competitors.get('global_competitors', []))} competitors, national: {len(competitors.get('national_competitors', []))} competitors")
                    return competitors
            
            print(f"⚠️ Could not find competitors for {ticker}")
            return {"global_competitors": [], "national_competitors": []}
            
        except Exception as e:
            print(f"❌ Error finding competitors for {ticker}: {e}")
            return {"global_competitors": [], "national_competitors": []}
    
    @staticmethod
    def _extract_global_national_competitors_from_response(response_text: str) -> Dict[str, List[str]]:
        """Extract both global and national competitor tickers from AI response"""
        try:
            # First try to extract JSON from code blocks
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to find generic code blocks
                json_match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    # Try to find JSON-like structure without code blocks
                    json_match = re.search(r'(\{[^}]*"global_competitors"[^}]*\})', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                    else:
                        print("Could not find JSON in response")
                        return {"global_competitors": [], "national_competitors": []}
            
            # Parse JSON
            data = json.loads(json_str)
            global_competitors = data.get("global_competitors", [])
            national_competitors = data.get("national_competitors", [])
            
            # Validate and clean ticker symbols
            def validate_and_clean_tickers(tickers):
                valid_tickers = []
                for ticker in tickers:
                    if isinstance(ticker, str):
                        # Clean ticker symbol (remove spaces, make uppercase)
                        clean_ticker = ticker.strip().upper()
                        # Basic validation (1-5 characters, letters only)
                        if clean_ticker and len(clean_ticker) <= 5 and clean_ticker.isalpha():
                            valid_tickers.append(clean_ticker)
                return valid_tickers[:3]  # Return max 5 competitors
            
            return {
                "global_competitors": validate_and_clean_tickers(global_competitors),
                "national_competitors": validate_and_clean_tickers(national_competitors)
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"global_competitors": [], "national_competitors": []}
        except Exception as e:
            print(f"Error extracting competitors: {e}")
            return {"global_competitors": [], "national_competitors": []}
    
    @staticmethod
    def _extract_competitors_from_response(response_text: str) -> List[str]:
        """Extract competitor tickers from AI response (legacy method for backward compatibility)"""
        try:
            # First try to extract JSON from code blocks
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to find generic code blocks
                json_match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    # Try to find JSON-like structure without code blocks
                    json_match = re.search(r'(\{[^}]*"competitors"[^}]*\})', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                    else:
                        print("Could not find JSON in response")
                        return []
            
            # Parse JSON
            data = json.loads(json_str)
            competitors = data.get("competitors", [])
            
            # Validate and clean ticker symbols
            valid_competitors = []
            for ticker in competitors:
                if isinstance(ticker, str):
                    # Clean ticker symbol (remove spaces, make uppercase)
                    clean_ticker = ticker.strip().upper()
                    # Basic validation (1-5 characters, letters only)
                    if clean_ticker and len(clean_ticker) <= 5 and clean_ticker.isalpha():
                        valid_competitors.append(clean_ticker)
            
            return valid_competitors[:3]  # Return max 5 competitors
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return []
        except Exception as e:
            print(f"Error extracting competitors: {e}")
            return []