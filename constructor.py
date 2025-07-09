def construct_report(stock_data: dict, analysis: str) -> str:
    full_report = stock_data
    #add on the contents of the analysis dict to the full_report dictionary
    full_report.update(analysis)
    return full_report

if __name__ == "__main__":
    parse_branches_from_text

"""
Expected output to the frontend:
{
  "id": "1678886400000",
  "companyName": "Analyze the growth potential for Apple",
  "timestamp": "2023-03-15T12:00:00Z",
  "data": {
    "overview": {
      "name": "Apple Inc.",
      "ticker": "AAPL",
      "sector": "Technology",
      "marketCap": "$2.6T",
      "price": "$165.23",
      "change": "+1.21%"
    },
    "financials": {
      "revenue": "$394.3B",
      "netIncome": "$99.8B",
      "eps": "$6.16",
      "peRatio": "26.8"
    },
    "analysis": "Final summary from generate.py" //add this in
  }
}

Initial input from the frontend:
{
  "prompt": "Apple",
  "ticker": "AAPL"
}


"""