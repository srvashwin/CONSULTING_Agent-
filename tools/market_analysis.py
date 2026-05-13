import re
from .financial_data import FinancialDataTool


class MarketAnalysisTool:
    def __init__(self):
        self.fin = FinancialDataTool()

    QUESTION_PEERS = {
        r"\bev\b|\belectric vehicle\b|\bautomotive\b|\bcar\b|\bauto\b": ["TSLA", "F", "GM", "RIVN", "LCID", "TM", "BYDDF", "HMC", "VWAGY", "STLA"],
        r"\bstreaming\b|\bentertainment\b|\bcontent\b|\bhbo\b|\bnetflix\b": ["NFLX", "DIS", "WBD", "PARA", "SPOT", "ROKU", "AMZN", "AAPL"],
        r"\bcloud\b|\biaas\b|\bsaas\b|\bpaas\b|\bdata center\b|\bazure\b|\baws\b|\bgcp\b": ["AMZN", "MSFT", "GOOGL", "CRM", "ORCL", "ADBE", "IBM"],
        r"\bsemiconductor\b|\bchip\b|\bgpu\b|\bfab\b|\bprocessor\b": ["NVDA", "AMD", "INTC", "AVGO", "QCOM", "MRVL", "TSM", "ASML"],
        r"\bsocial media\b|\bsocial network\b|\badvertising\b|\bmeta\b|\btiktok\b": ["META", "GOOGL", "SNAP", "PINS", "TTWO", "MSFT"],
        r"\be-commerce\b|\bonline retail\b|\bmarketplace\b|\bshopify\b": ["AMZN", "WMT", "TGT", "COST", "SHOP", "EBAY", "PDD", "BABA"],
        r"\bfintech\b|\bpayment\b|\bbanking\b|\bcrypto\b|\bblockchain\b": ["V", "MA", "PYPL", "SQ", "JPM", "GS", "MS", "COIN"],
        r"\bhealthcare\b|\bpharma\b|\bbiotech\b|\bdrug\b|\bmedical\b": ["UNH", "PFE", "JNJ", "ABBV", "MRK", "LLY", "TMO", "ABT"],
        r"\bgaming\b|\bvideo game\b|\besports\b|\bconsole\b": ["MSFT", "SONY", "TTWO", "EA", "PLTK", "UBSFY", "NTDOY"],
        r"\brenewable\b|\bclean energy\b|\bsolar\b|\bwind\b|\bgreen\b": ["ENPH", "SEDG", "FSLR", "NEE", "PLUG", "BE", "CWEN"],
        r"\bai\b|\bartificial intelligence\b|\bllm\b|\bfoundation model\b|\bgpt\b": ["MSFT", "GOOGL", "META", "AMZN", "NVDA", "CRM", "ORCL"],
    }

    FALLBACK_PEERS = {
        "MSFT": ["GOOGL", "AMZN", "CRM", "ORCL", "ADBE"],
        "AAPL": ["MSFT", "GOOGL", "AMZN", "META", "CRM"],
        "GOOGL": ["MSFT", "AMZN", "META", "AAPL", "CRM"],
        "AMZN": ["MSFT", "GOOGL", "AAPL", "CRM", "WMT"],
        "META": ["GOOGL", "MSFT", "SNAP", "PINS", "TTWO"],
        "NVDA": ["AMD", "INTC", "AVGO", "QCOM", "MRVL"],
        "TSLA": ["F", "GM", "RIVN", "LCID", "TM"],
        "JPM": ["GS", "MS", "BAC", "C", "WFC"],
        "PG": ["CL", "KMB", "CHD", "K", "CPB"],
        "DIS": ["CMCSA", "NFLX", "WBD", "PARA", "FOX"],
    }

    def competitor_benchmarking(self, primary_ticker: str, peer_tickers: list = None, question: str = None) -> dict:
        if peer_tickers is None:
            # Check if question signals a specific industry for peer matching
            if question:
                for pattern, tickers in self.QUESTION_PEERS.items():
                    if re.search(pattern, question, re.IGNORECASE):
                        peer_tickers = tickers
                        break
            if not peer_tickers:
                peer_info = self.fin.get_industry_peers(primary_ticker)
                peer_tickers = peer_info.get("peers", [])
            if not peer_tickers:
                peer_tickers = self.FALLBACK_PEERS.get(primary_ticker.upper(), [])

        all_tickers = [primary_ticker] + peer_tickers[:5]
        companies = {}
        for t in all_tickers:
            fin = self.fin.get_company_financials(t)
            if "error" not in fin:
                companies[t] = fin

        if not companies:
            return {"error": "Could not fetch competitor data"}

        primary = companies.get(primary_ticker, {})
        peers_data = {k: v for k, v in companies.items() if k != primary_ticker}

        comparison_metrics = ["market_cap", "revenue", "revenue_growth", "gross_margins",
                              "operating_margins", "profit_margins", "ebitda_margins",
                              "pe_ratio", "return_on_equity", "debt_to_equity", "employees"]

        comparison_table = []
        for t, c in companies.items():
            row = {"ticker": t, "name": c.get("name", t)}
            for m in comparison_metrics:
                row[m] = c.get(m)
            comparison_table.append(row)

        benchmarks = {}
        for m in comparison_metrics:
            peer_vals = [c.get(m) for t, c in companies.items() if c.get(m) is not None and isinstance(c.get(m), (int, float)) and t != primary_ticker]
            pv = primary.get(m)
            if peer_vals and pv is not None:
                benchmarks[m] = {
                    "median": sorted(peer_vals)[len(peer_vals) // 2],
                    "min": min(peer_vals),
                    "max": max(peer_vals),
                    "primary_value": pv,
                }

        primary_name = primary.get("name", primary_ticker)
        strengths = []
        weaknesses = []
        for m, b in benchmarks.items():
            pv = b["primary_value"]
            higher_is_better = m not in ("pe_ratio", "debt_to_equity")
            above_median = pv >= b["median"] if higher_is_better else pv <= b["median"]
            if above_median:
                strengths.append(f"Best-in-class {m.replace('_', ' ')}: {self._fmt(pv, m)} vs peer median {self._fmt(b['median'], m)}")
            else:
                weaknesses.append(f"Below peer median {m.replace('_', ' ')}: {self._fmt(pv, m)} vs peer median {self._fmt(b['median'], m)}")

        return {
            "primary_ticker": primary_ticker,
            "primary_name": primary_name,
            "peers": peers_data,
            "comparison_table": comparison_table,
            "benchmarks": benchmarks,
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "insight": (
                f"{primary_name} has {len(strengths)} competitive strengths and {len(weaknesses)} areas of improvement "
                f"vs {len(peers_data)} industry peers."
            ),
        }

    def industry_benchmarks(self, primary_ticker: str, peer_tickers: list = None, question: str = None) -> dict:
        data = self.competitor_benchmarking(primary_ticker, peer_tickers, question=question)
        if "error" in data:
            return data

        benchmarks = data.get("benchmarks", {})
        primary = data.get("primary_name", primary_ticker)

        normalized = {}
        for m, b in benchmarks.items():
            pv = b.get("primary_value")
            if pv is None or not isinstance(pv, (int, float)):
                continue

            denom = max(abs(b["max"]), abs(b["min"]))
            if denom == 0:
                continue

            higher_is_better = m not in ("pe_ratio", "debt_to_equity")
            score = (pv - b["min"]) / (b["max"] - b["min"]) if (b["max"] - b["min"]) != 0 else 0.5

            if not higher_is_better:
                score = 1 - score

            normalized[m] = {
                "score": round(max(0, min(1, score)) * 100),
                "primary_value": pv,
                "median": b["median"],
                "min": b["min"],
                "max": b["max"],
            }

        overall = round(sum(n["score"] for n in normalized.values()) / len(normalized)) if normalized else 0

        rating = "Strong" if overall >= 70 else "Average" if overall >= 40 else "Weak"

        return {
            "primary_name": primary,
            "overall_score": overall,
            "overall_rating": rating,
            "metrics": normalized,
            "insight": f"{primary} scores {overall}/100 overall, rated '{rating}' against industry peers.",
        }

    def _fmt(self, val, metric):
        if val is None:
            return "N/A"
        if metric in ("market_cap", "revenue", "ebitda_margins"):
            return f"${val:,.0f}" if abs(val) > 1 else f"{val*100:.1f}%"
        if metric in ("revenue_growth", "gross_margins", "operating_margins", "profit_margins",
                      "return_on_equity", "return_on_assets", "ebitda_margins"):
            return f"{val*100:.1f}%"
        if metric in ("pe_ratio", "forward_pe", "price_to_book", "debt_to_equity"):
            return f"{val:.2f}"
        if metric in ("employees",):
            return f"{int(val):,}"
        return str(val)

    def size_total_addressable_market(self, industry: str, region: str = "global") -> dict:
        return {
            "industry": industry,
            "region": region,
            "methodology": "Top-down TAM estimation based on industry reports",
            "note": "For precise TAM, ingest industry reports via document upload or provide specific data sources.",
            "status": "needs_data",
            "suggested_sources": [
                f"IBISWorld {industry} report",
                f"Gartner {industry} market forecast",
                "Statista industry data",
                "SEC filings of public companies in this space",
            ],
        }
