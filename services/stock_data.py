# backend/stock_data.py
# returns the exact format frontend expects but without analysis section

import yfinance as yf
from datetime import datetime, timezone

def fetch_stock_summary(symbol: str):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    financials = ticker.financials

    # Safely extract financial values
    def get_value(df, key):
        try:
            return df.loc[key].iloc[0]
        except Exception:
            return None

    # Format large numbers as readable strings
    def format_billions(value):
        if value is None:
            return "N/A"
        return f"${value/1e9:.1f}B"

    # Get current UTC time
    now = datetime.now(timezone.utc)

    # Build output structure
    result = {
        "id": str(int(now.timestamp() * 1000)),  # ✅ correct timestamp in ms
        "companyName": f"Analyze the growth potential for {info.get('shortName', symbol)}",
        "timestamp": now.isoformat().replace("+00:00", "Z"),  # ✅ ISO 8601 + Z
        "data": {
            "overview": {
                "name": info.get("longName", "N/A"),
                "ticker": symbol.upper(),
                "sector": info.get("sector", "N/A"),
                "marketCap": format_billions(info.get("marketCap")),
                "price": f"${info.get('currentPrice', 0):.2f}",
                "change": f"{info.get('regularMarketChangePercent', 0):+.2f}%"
            },
            "financials": {
                "revenue": format_billions(get_value(financials, "Total Revenue")),
                "netIncome": format_billions(get_value(financials, "Net Income")),
                "eps": f"${info.get('trailingEps', 0):.2f}",
                "peRatio": f"{info.get('trailingPE', 0):.1f}"
            }
        }
    }

    return result

# Example usage
if __name__ == "__main__":
    summary = fetch_stock_summary("AAPL")
    from pprint import pprint
    pprint(summary)
