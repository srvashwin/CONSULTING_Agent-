from typing import Optional
import yfinance as yf


class FinancialDataTool:
    def get_company_financials(self, ticker: str) -> dict:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}

            return {
                "name": info.get("longName", info.get("shortName", ticker)),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "enterprise_value": info.get("enterpriseValue", 0),
                "revenue": info.get("totalRevenue", 0),
                "revenue_growth": info.get("revenueGrowth", 0),
                "gross_margins": info.get("grossMargins", 0),
                "operating_margins": info.get("operatingMargins", 0),
                "profit_margins": info.get("profitMargins", 0),
                "ebitda": info.get("ebitda", 0),
                "ebitda_margins": info.get("ebitdaMargins", 0),
                "free_cashflow": info.get("freeCashflow", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "forward_pe": info.get("forwardPE", 0),
                "price_to_book": info.get("priceToBook", 0),
                "debt_to_equity": info.get("debtToEquity", 0),
                "return_on_equity": info.get("returnOnEquity", 0),
                "return_on_assets": info.get("returnOnAssets", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "payout_ratio": info.get("payoutRatio", 0),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "target_mean_price": info.get("targetMeanPrice", 0),
                "number_of_analysts": info.get("numberOfAnalystOpinions", 0),
                "recommendation": info.get("recommendationKey", "N/A"),
                "employees": info.get("fullTimeEmployees", 0),
                "country": info.get("country", "N/A"),
                "website": info.get("website", ""),
                "revenue_growth_3y": info.get("revenueGrowth3y", None),
                "earnings_growth": info.get("earningsGrowth", None),
                "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth", None),
            }
        except Exception as e:
            return {"error": f"Could not fetch financials for {ticker}: {e}"}

    def get_multi_year_financials(self, ticker: str, years: int = 4) -> dict:
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            balance = stock.balance_sheet
            cashflow = stock.cashflow

            if financials is None or financials.empty:
                return {"error": "No multi-year financial data available"}

            data = {"ticker": ticker, "years": []}
            columns = financials.columns[:years]

            for col in columns:
                year_data = {
                    "year": str(col.year) if hasattr(col, 'year') else str(col),
                    "total_revenue": self._safe_get(financials, col, "Total Revenue"),
                    "gross_profit": self._safe_get(financials, col, "Gross Profit"),
                    "operating_income": self._safe_get(financials, col, "Operating Income"),
                    "net_income": self._safe_get(financials, col, "Net Income"),
                    "ebitda": self._safe_get(financials, col, "EBITDA"),
                }

                if balance is not None and not balance.empty and col in balance.columns:
                    year_data["total_assets"] = self._safe_get(balance, col, "Total Assets")
                    year_data["total_debt"] = self._safe_get(balance, col, "Total Debt")
                    year_data["stockholder_equity"] = self._safe_get(balance, col, "Stockholders Equity")

                if cashflow is not None and not cashflow.empty and col in cashflow.columns:
                    year_data["free_cashflow"] = self._safe_get(cashflow, col, "Free Cash Flow")
                    year_data["operating_cashflow"] = self._safe_get(cashflow, col, "Operating Cash Flow")

                data["years"].append(year_data)

            if data["years"]:
                yearly = data["years"]
                latest = yearly[0]
                oldest = yearly[-1]

                rev_diff = (latest["total_revenue"] - oldest["total_revenue"]) / abs(oldest["total_revenue"]) if oldest["total_revenue"] else 0
                cagr = ((latest["total_revenue"] / oldest["total_revenue"]) ** (1 / max(len(yearly) - 1, 1)) - 1) if oldest["total_revenue"] else 0

                data["summary"] = {
                    "revenue_cagr": cagr,
                    "revenue_growth_total": rev_diff,
                    "years_span": len(yearly),
                    "latest_year": yearly[0]["year"],
                }

            return data

        except Exception as e:
            return {"error": f"Error fetching multi-year data: {e}"}

    def _safe_get(self, df, col, field):
        try:
            if field in df.index and col in df.columns:
                val = df.loc[field, col]
                return None if val is None or (hasattr(val, 'isna') and val.isna()) else float(val)
        except Exception:
            pass
        return None

    def get_stock_price_history(self, ticker: str, period: str = "1y") -> dict:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return {"error": "No price data available"}

            prices = []
            for idx, row in hist.iterrows():
                prices.append({
                    "date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                })

            return {
                "ticker": ticker,
                "period": period,
                "prices": prices,
                "current_price": float(hist["Close"].iloc[-1]),
                "high_52w": float(hist["Close"].max()),
                "low_52w": float(hist["Close"].min()),
                "avg_volume": int(hist["Volume"].mean()),
                "total_return": float(
                    (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
                ),
            }
        except Exception as e:
            return {"error": f"Could not fetch price history: {e}"}

    def get_industry_peers(self, ticker: str, max_peers: int = 6) -> list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            sector = info.get("sector", "")
            industry = info.get("industry", "")

            peers = info.get("recommendedSymbols", [])
            if not peers:
                peers = info.get("peerSymbols", [])

            peer_list = []
            if isinstance(peers, list):
                for p in peers[:max_peers]:
                    if isinstance(p, dict):
                        peer_list.append(p.get("symbol", ""))
                    elif isinstance(p, str):
                        peer_list.append(p)

            return {
                "sector": sector,
                "industry": industry,
                "peers": [p for p in peer_list if p and p.upper() != ticker.upper()][:max_peers],
            }
        except Exception:
            return {"sector": "", "industry": "", "peers": []}
