import os
import json
import re
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types

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
        Get the top 5 competitor tickers for a given ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            List[str]: List of competitor ticker symbols
        """
        try:
            print(f"🔍 Finding competitors for {ticker}...")
            
            # Create the prompt for finding competitors
            prompt = f"""
Find the top 5 direct competitors of the company with ticker symbol {ticker}.

You must return ONLY the ticker symbols of the competing companies, nothing else. 
Focus on companies that are in the same industry/sector and compete directly.
Only include publicly traded companies with valid stock ticker symbols.

Return the results in this exact JSON format:
```json
{{
 "competitors": [
   "TICKER1",
   "TICKER2", 
   "TICKER3",
   "TICKER4",
   "TICKER5"
 ]
}}
```

Do not include any explanation, analysis, or additional text. Just the JSON with ticker symbols.
"""
            
            # Try with Google grounding first
            try:
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                config = types.GenerateContentConfig(
                    tools=[grounding_tool]
                )
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config,
                )
                
                competitors = CompetitorAnalysisService._extract_competitors_from_response(response.text)
                if competitors:
                    print(f"✓ Found {len(competitors)} competitors: {competitors}")
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
                            model="gemini-2.5-flash",
                            contents=prompt,
                            config=config,
                        )
                        
                        competitors = CompetitorAnalysisService._extract_competitors_from_response(response.text)
                        if competitors:
                            print(f"✓ Found {len(competitors)} competitors: {competitors}")
                            return competitors
                            
                    except Exception as e2:
                        print(f"google_search_retrieval failed: {e2}")
                        # Fall through to no-grounding fallback
                
                # Final fallback: no grounding
                print("Using model without grounding...")
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                
                competitors = CompetitorAnalysisService._extract_competitors_from_response(response.text)
                if competitors:
                    print(f"✓ Found {len(competitors)} competitors: {competitors}")
                    return competitors
            
            print(f"⚠️ Could not find competitors for {ticker}")
            return []
            
        except Exception as e:
            print(f"❌ Error finding competitors for {ticker}: {e}")
            return []
    
    @staticmethod
    def _extract_competitors_from_response(response_text: str) -> List[str]:
        """Extract competitor tickers from AI response"""
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
            
            return valid_competitors[:5]  # Return max 5 competitors
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return []
        except Exception as e:
            print(f"Error extracting competitors: {e}")
            return [] 