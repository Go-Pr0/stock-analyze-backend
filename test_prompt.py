#!/usr/bin/env python3
"""
Test script to verify the updated prompt function works correctly.
"""

from services.prompt import get_global_competitor_prompt

def test_prompt():
    """Test the updated prompt function"""
    ticker = "AAPL"
    prompt = get_global_competitor_prompt(ticker)
    
    print("🧪 Testing updated prompt function...")
    print(f"📝 Generated prompt for {ticker}:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    
    # Check if prompt contains required elements
    required_elements = [
        "global_competitors",
        "national_competitors", 
        ticker,
        "JSON format"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in prompt:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing required elements: {missing_elements}")
        return False
    else:
        print("✅ Prompt contains all required elements")
        return True

if __name__ == "__main__":
    success = test_prompt()
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}")