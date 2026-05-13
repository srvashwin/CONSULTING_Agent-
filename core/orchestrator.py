import json
import os
from datetime import datetime
from typing import Optional
from core.llm_client import LLMClient
from core.config import config
from knowledge_base.vector_store import VectorStore
from tools.web_search import WebSearchTool
from tools.financial_data import FinancialDataTool
from tools.document_reader import DocumentReaderTool
from tools.market_analysis import MarketAnalysisTool
from templates.deliverable import generate_deliverable


class ConsultingOrchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
        self.web = WebSearchTool()
        self.financial = FinancialDataTool()
        self.doc_reader = DocumentReaderTool()
        self.market = MarketAnalysisTool()

    def run_structured(
        self,
        company: str,
        question: str,
        ticker: Optional[str] = None,
        documents: Optional[list] = None,
    ) -> dict:
        ticker = ticker or self._resolve_ticker(company)
        result = {
            "company": company,
            "question": question,
            "ticker": ticker,
            "status": "running",
            "engagement": {},
            "frameworks": [],
            "company_data": {},
            "financials": {},
            "multi_year_financials": {},
            "price_history": {},
            "competitor_benchmark": {},
            "industry_benchmark": {},
            "analysis": {},
            "recommendations": {},
            "documents_ingested": [],
            "deliverable_path": "",
            "generated_at": datetime.now().isoformat(),
        }

        result["engagement"] = self._classify_engagement(question)
        frameworks_raw = self._get_frameworks(question, result["engagement"]["type"])
        result["frameworks"] = [
            {"name": f["metadata"].get("name", ""), "content": f["content"]}
            for f in frameworks_raw
        ]

        result["company_data"] = self.web.research_company(company)

        if ticker:
            fin = self.financial.get_company_financials(ticker)
            if "error" not in fin:
                result["financials"] = fin
            multi = self.financial.get_multi_year_financials(ticker)
            if "error" not in multi:
                result["multi_year_financials"] = multi
            price = self.financial.get_stock_price_history(ticker)
            if "error" not in price:
                result["price_history"] = price

            benchmark = self.market.competitor_benchmarking(ticker, question=question)
            if "error" not in benchmark:
                result["competitor_benchmark"] = benchmark
            ind_bench = self.market.industry_benchmarks(ticker, question=question)
            if "error" not in ind_bench:
                result["industry_benchmark"] = ind_bench

        doc_texts = []
        if documents:
            for doc in documents:
                content = self.doc_reader.read_file(doc)
                doc_texts.append(content[:15000])
                result["documents_ingested"].append(os.path.basename(doc))

        result["analysis"] = self._analyze(
            company=company,
            question=question,
            engagement_type=result["engagement"]["type"],
            frameworks=frameworks_raw,
            company_data=result["company_data"],
            financials=result["financials"],
            multi_year=result["multi_year_financials"],
            competitor_benchmark=result["competitor_benchmark"],
            industry_benchmark=result["industry_benchmark"],
            doc_texts=doc_texts,
        )

        result = self._deep_research_loop(result)

        result["recommendations"] = self._generate_recommendations(
            company=company,
            question=question,
            analysis=result["analysis"],
            financials=result["financials"],
        )

        result["deliverable_path"] = generate_deliverable(
            title=f"{result['engagement']['type'].title()} Analysis: {company}",
            engagement_type=result["engagement"]["type"],
            sections={
                "executive_summary": result["analysis"].get("executive_summary", ""),
                "background": result["analysis"].get("background", ""),
                "analysis": result["analysis"].get("detailed_analysis", ""),
                "frameworks": self._format_frameworks(frameworks_raw),
                "findings": self._format_findings(result["analysis"].get("findings", [])),
                "recommendations": result["recommendations"].get("recommendations", ""),
                "risks": result["recommendations"].get("risks", ""),
                "sources": self._format_sources(result["company_data"]),
            },
        )

        result["status"] = "complete"
        return result

    def _resolve_ticker(self, company: str) -> str:
        NAME_MAP = {
            "apple": "AAPL", "google": "GOOGL", "alphabet": "GOOGL",
            "microsoft": "MSFT", "amazon": "AMZN", "meta": "META",
            "facebook": "META", "nvidia": "NVDA", "tesla": "TSLA",
            "netflix": "NFLX", "disney": "DIS", "walmart": "WMT",
            "costco": "COST", "exxon": "XOM", "chevron": "CVX",
            "jpmorgan": "JPM", "goldman sachs": "GS", "bank of america": "BAC",
            "berkshire hathaway": "BRK.B", "johnson & johnson": "JNJ",
            "procter & gamble": "PG", "coca-cola": "KO", "pepsi": "PEP",
            "verizon": "VZ", "at&t": "T", "comcast": "CMCSA",
            "intel": "INTC", "amd": "AMD", "qualcomm": "QCOM",
            "ibm": "IBM", "oracle": "ORCL", "salesforce": "CRM",
            "adobe": "ADBE", "paypal": "PYPL", "uber": "UBER",
            "lyft": "LYFT", "twitter": "TWTR", "snap": "SNAP",
            "pinterest": "PINS", "spotify": "SPOT", "shopify": "SHOP",
            "square": "SQ", "block": "SQ", "robinhood": "HOOD",
            "coinbase": "COIN", "samsung": "SSNLF", "sony": "SONY",
            "nike": "NKE", "mcdonald's": "MCD", "starbucks": "SBUX",
            "boeing": "BA", "ford": "F", "general motors": "GM",
            "toyota": "TM", "honda": "HMC", "rivian": "RIVN",
            "lucid": "LCID", "byd": "BYDDF", "pfizer": "PFE",
            "moderna": "MRNA", "johnson": "JNJ", "unitedhealth": "UNH",
        }
        key = company.strip().lower()
        if key in NAME_MAP:
            return NAME_MAP[key]
        try:
            import yfinance as yf
            t = yf.Ticker(key)
            info = t.info or {}
            return info.get("symbol", "")
        except Exception:
            return ""

    def _classify_engagement(self, question: str) -> dict:
        system = (
            "You are a consulting engagement classifier. "
            "Classify the business question into an engagement type and focus areas. "
            "Return JSON with: type (strategy/m_and_a/operations/digital/hr/esg/general), "
            "focus_areas (list of strings)."
        )
        return self.llm.structured_light(
            system=system,
            messages=[{"role": "user", "content": f"Question: {question}"}],
            schema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "strategy",
                            "m_and_a",
                            "operations",
                            "digital",
                            "hr",
                            "esg",
                            "general",
                        ],
                    },
                    "focus_areas": {"type": "array", "items": {"type": "string"}},
                },
            },
        )

    def _get_frameworks(self, question: str, engagement_type: str) -> list:
        results = self.vector_store.search(question, n_results=5)
        relevant = []
        seen = set()
        for r in results:
            name = r["metadata"].get("name", "")
            if name and name not in seen:
                seen.add(name)
                relevant.append(r)
        return relevant[:3]

    def _deep_research_loop(self, result: dict) -> dict:
        system = (
            "You are a senior consultant reviewing your first-pass analysis. "
            "Identify 2-3 critical knowledge gaps that would significantly improve the analysis "
            "if you had better data. Be specific about what data is missing. "
            "Return JSON with: gaps (array of objects with 'what' (what's missing) and "
            "'search_query' (a specific search query to find it))."
        )
        eng = result.get("engagement", result.get("engagement_type", "analysis"))
        analysis_summary = json.dumps(
            {
                "engagement": eng,
                "findings_count": len(result["analysis"].get("findings", [])),
                "exec_summary_preview": result["analysis"].get("executive_summary", "")[:300],
            }
        )

        gaps = self.llm.structured_light(
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"First-pass analysis summary:\n{analysis_summary}\n\nQuestion: {result.get('question', result.get('issue', ''))}\nCompany: {result['company']}",
                }
            ],
            schema={
                "type": "object",
                "properties": {
                    "gaps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "what": {"type": "string"},
                                "search_query": {"type": "string"},
                            },
                        },
                        "minItems": 2,
                        "maxItems": 3,
                    }
                },
            },
        )

        gap_results = []
        gaps_list = gaps if isinstance(gaps, list) else gaps.get("gaps", [])
        for gap in gaps_list:
            query = gap.get("search_query", "")
            what = gap.get("what", "")
            if query:
                results = self.web.search(query, num_results=4)
                pages = []
                seen_urls = set()
                for r in results[:3]:
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        content = self.web.fetch_page(url)
                        pages.append({"url": url, "content": content[:3000]})
                gap_results.append({"gap": what, "query": query, "results": results, "pages": pages})

                # Merge gap results into company_data so frontend sources section shows them
                seen_existing = set(
                    r.get("url", "") for r in result["company_data"].get("search_results", [])
                )
                for r in results:
                    url = r.get("url", "")
                    if url and url not in seen_existing:
                        seen_existing.add(url)
                        result["company_data"].setdefault("search_results", []).append(r)

        if gap_results:
            gap_text = ""
            for g in gap_results:
                gap_text += f"\nGap: {g['gap']}\n"
                gap_text += f"Search: {g['query']}\n"
                for p in g["pages"]:
                    gap_text += f"\n--- {p['url']} ---\n{p['content'][:1500]}\n"

            system = (
                "You are a senior strategy consultant. You have been given additional research "
                "to fill gaps in your initial analysis. Incorporate this new information "
                "to refine and strengthen your findings. "
                "Return JSON with: executive_summary (updated 2-3 paragraph summary), "
                "detailed_analysis (updated full analysis incorporating new data), "
                "findings (updated array of 5-8 specific findings)."
            )
            user_msg = (
                f"Original question: {result.get('question', result.get('issue', ''))}\n"
                f"Company: {result['company']}\n\n"
                f"Previous analysis:\n{result['analysis'].get('detailed_analysis', '')[:4000]}\n\n"
                f"Previous findings:\n{json.dumps(result['analysis'].get('findings', []), indent=2)}\n\n"
                f"New research to incorporate:\n{gap_text[:8000]}"
            )

            refined = self.llm.structured_heavy(
                system=system,
                messages=[{"role": "user", "content": user_msg}],
                schema={
                    "type": "object",
                    "properties": {
                        "executive_summary": {"type": "string"},
                        "detailed_analysis": {"type": "string"},
                        "findings": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 5,
                            "maxItems": 8,
                        },
                    },
                },
            )

            refined_dict = refined if isinstance(refined, dict) else {}
            result["analysis"]["executive_summary"] = refined_dict.get(
                "executive_summary", result["analysis"].get("executive_summary", "")
            )
            result["analysis"]["detailed_analysis"] = refined_dict.get(
                "detailed_analysis", result["analysis"].get("detailed_analysis", "")
            )
            result["analysis"]["findings"] = refined_dict.get(
                "findings", result["analysis"].get("findings", [])
            )
            result["deep_research_gaps"] = gap_results

        return result

    def _analyze(
        self,
        company: str,
        question: str,
        engagement_type: str,
        frameworks: list,
        company_data: dict,
        financials: dict,
        multi_year: dict = None,
        competitor_benchmark: dict = None,
        industry_benchmark: dict = None,
        doc_texts: list = None,
    ) -> dict:
        framework_text = "\n\n".join([f["content"] for f in frameworks])

        research_text = ""
        for p in company_data.get("pages", []):
            research_text += f"\n--- Source: {p['url']} ---\n{p['content'][:2000]}\n"

        financial_text = ""
        if financials and "error" not in financials:
            financial_text = json.dumps(financials, indent=2, default=str)

        multi_year_text = ""
        if multi_year and "error" not in multi_year:
            summary = multi_year.get("summary", {})
            multi_year_text = f"Revenue CAGR: {summary.get('revenue_cagr', 'N/A')}\n"
            multi_year_text += f"Years span: {summary.get('years_span', 'N/A')}\n"
            for y in multi_year.get("years", []):
                multi_year_text += (
                    f"  {y['year']}: Rev={y['total_revenue']}, "
                    f"GP={y['gross_profit']}, NI={y['net_income']}, "
                    f"FCF={y.get('free_cashflow', 'N/A')}\n"
                )

        benchmark_text = ""
        if competitor_benchmark and "error" not in competitor_benchmark:
            benchmark_text = f"Industry peers: {list(competitor_benchmark.get('peers', {}).keys())}\n"
            for s in competitor_benchmark.get("strengths", []):
                benchmark_text += f"  Strength: {s}\n"
            for w in competitor_benchmark.get("weaknesses", []):
                benchmark_text += f"  Weakness: {w}\n"

        ind_bench_text = ""
        if industry_benchmark and "error" not in industry_benchmark:
            ind_bench_text = (
                f"Industry score: {industry_benchmark.get('overall_score', 'N/A')}/100 "
                f"({industry_benchmark.get('overall_rating', 'N/A')})\n"
            )

        doc_text = ""
        if doc_texts:
            for i, dt in enumerate(doc_texts):
                doc_text += f"\n--- Document {i+1} ---\n{dt[:3000]}\n"

        system = (
            "You are a senior strategy consultant at a top-tier firm. "
            "Perform a thorough analysis of the client's question. "
            "Return your analysis as valid JSON with these keys: "
            "executive_summary (2-3 paragraph summary), "
            "background (context about the company and situation), "
            "detailed_analysis (full analysis with data-driven insights, "
            "structured in sections with sub-headings), "
            "findings (array of 5-8 specific, actionable findings)."
        )

        sections = []
        sections.append(f"Company: {company}")
        sections.append(f"Question: {question}")
        sections.append(f"Engagement Type: {engagement_type}")
        sections.append(f"\nRelevant Frameworks:\n{framework_text}")
        sections.append(f"\nCompany Research:\n{research_text[:8000]}")

        if financial_text:
            sections.append(f"\nFinancial Data:\n{financial_text[:4000]}")
        if multi_year_text:
            sections.append(f"\nMulti-Year Financial Trends:\n{multi_year_text}")
        if benchmark_text:
            sections.append(f"\nCompetitor Benchmarking:\n{benchmark_text}")
        if ind_bench_text:
            sections.append(f"\nIndustry Benchmark Score:\n{ind_bench_text}")
        if doc_text:
            sections.append(f"\nClient Documents:\n{doc_text}")

        user_msg = (
            "\n".join(sections)
            + "\n\nInstructions:\n"
            + "1. Apply the relevant frameworks to structure your thinking\n"
            + "2. Use multi-year trends to identify growth/deceleration patterns\n"
            + "3. Use competitor benchmarks to assess relative position\n"
            + "4. Identify specific, data-driven insights with quantified support\n"
            + "5. Structure findings as actionable statements"
        )

        return self.llm.structured_heavy(
            system=system,
            messages=[{"role": "user", "content": user_msg}],
            schema={
                "type": "object",
                "properties": {
                    "executive_summary": {"type": "string"},
                    "background": {"type": "string"},
                    "detailed_analysis": {"type": "string"},
                    "findings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 5,
                        "maxItems": 8,
                    },
                },
            },
        )

    def _generate_recommendations(
        self, company: str, question: str, analysis: dict, financials: dict
    ) -> dict:
        system = (
            "You are a senior partner at a top consulting firm. "
            "Based on the analysis, provide strategic recommendations and risk assessment. "
            "Return JSON with: recommendations (3-5 specific recommendations numbered format), "
            "risks (3-5 risks with mitigation strategies)."
        )
        return self.llm.structured_heavy(
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Company: {company}\nQuestion: {question}\n\n"
                        f"Analysis: {analysis.get('detailed_analysis', '')}\n\n"
                        f"Findings: {json.dumps(analysis.get('findings', []))}"
                    ),
                }
            ],
            schema={
                "type": "object",
                "properties": {
                    "recommendations": {"type": "string"},
                    "risks": {"type": "string"},
                },
            },
        )

    def _format_frameworks(self, frameworks: list) -> str:
        if not frameworks:
            return "Standard consulting frameworks were applied to structure this analysis."
        lines = []
        for f in frameworks:
            name = f["metadata"].get("name", "Framework")
            lines.append(f"- **{name}**: Applied to structure analysis")
        return "\n".join(lines)

    def _format_findings(self, findings: list) -> str:
        if not findings:
            return "No specific findings identified."
        lines = []
        for i, f in enumerate(findings, 1):
            lines.append(f"{i}. {f}")
        return "\n".join(lines)

    def _format_sources(self, company_data: dict) -> str:
        sources = company_data.get("search_results", [])
        if not sources:
            return "Primary research conducted via web search and financial databases."
        lines = []
        seen = set()
        for s in sources[:20]:
            url = s.get("url", "")
            if url and url not in seen:
                seen.add(url)
                lines.append(f"- [{s.get('title', 'Source')}]({url})")
        return "\n".join(lines) if lines else "Web research and financial data analysis."

    # ── Multi-step conversational engagement ──

    def engage(self, issue: str, company: str, ticker: str, conversation: list, issue_type: str = None) -> dict:
        is_first_round = len(conversation) == 0
        conv_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Agent'}: {m['content']}"
            for m in conversation[-6:]  # last 6 messages for context window
        )

        if is_first_round:
            system = (
                "You are a senior strategy consultant conducting an initial client discovery session. "
                "Your goal is to understand the client's business issue deeply before providing analysis.\n\n"
                "Classify the issue into one of these types:\n"
                "- profitability: revenue/cost/margin/pricing problems\n"
                "- growth: expansion/new markets/product launch/scaling\n"
                "- hiring_talent: recruitment/team building/skills gaps\n"
                "- restructuring: layoffs/headcount reduction/reorganization\n"
                "- merger_acquisition: M&A/due diligence/integration/valuation\n"
                "- operations: process efficiency/supply chain/workflow\n"
                "- strategy: competitive positioning/market threats/long-term direction\n"
                "- other: anything not covered above\n\n"
                "Return JSON:\n"
                "{\n"
                '  "issue_type": "<classified type>",\n'
                '  "understanding": "<1-2 sentence summary of what you understand>",\n'
                '  "questions": ["<question 1>", "<question 2>", ...],\n'
                '  "next_action": "questions"\n'
                "}\n\n"
                "Ask 2-3 targeted questions that clarify scope, metrics, and constraints. "
                "Be specific and ask for numbers where possible."
            )
            messages = [
                {"role": "user", "content": f"Company: {company}\nIssue: {issue}"}
            ]
            result = self.llm.structured_conversational(system, messages, {
                "type": "object",
                "properties": {
                    "issue_type": {"type": "string"},
                    "understanding": {"type": "string"},
                    "questions": {"type": "array", "items": {"type": "string"}},
                    "next_action": {"type": "string", "enum": ["questions", "ready"]},
                },
            })
            return result

        # Subsequent rounds: process user's answer, decide next step
        system = (
            "You are a senior strategy consultant. You are in the middle of a discovery conversation with a client.\n\n"
            "Classify the issue into one of these types if not already known:\n"
            "- profitability / growth / hiring_talent / restructuring / merger_acquisition / operations / strategy / other\n\n"
            "Review the conversation history and the user's latest answer. Decide whether you have enough information "
            "to proceed with analysis or need more details.\n\n"
            "Return JSON:\n"
            "{\n"
            '  "issue_type": "<type or keep previous>",\n'
            '  "understanding": "<updated 1-2 sentence summary>",\n'
            '  "questions": ["<follow-up question, if needed>"],\n'
            '  "additional_data_hint": "<what data would help: e.g. employee CSV, financial statements, org chart, or empty string>",\n'
            '  "next_action": "questions" or "ready"\n'
            "}\n\n"
            "If you need more info, set next_action to 'questions' and ask 1-2 focused follow-ups. "
            "If you have a clear picture, set next_action to 'ready'."
        )
        messages = [
            {"role": "user", "content": f"Company: {company}\nIssue type: {issue_type or 'unknown'}\nIssue: {issue}\n\nRecent conversation:\n{conv_text}"}
        ]
        result = self.llm.structured_conversational(system, messages, {
            "type": "object",
            "properties": {
                "issue_type": {"type": "string"},
                "understanding": {"type": "string"},
                "questions": {"type": "array", "items": {"type": "string"}},
                "additional_data_hint": {"type": "string"},
                "next_action": {"type": "string", "enum": ["questions", "ready"]},
            },
        })
        return result

    def run_issue_analysis(self, issue: str, company: str, ticker: str, issue_type: str, conversation: list, documents: list = None) -> dict:
        conv_summary = "\n".join(f"{m['role']}: {m['content']}" for m in conversation[-10:])
        engagement_label = {
            "profitability": "Profitability Analysis",
            "growth": "Growth Strategy",
            "hiring_talent": "Talent & Hiring Plan",
            "restructuring": "Restructuring & Cost Optimization",
            "merger_acquisition": "M&A Due Diligence",
            "operations": "Operations Improvement",
            "strategy": "Strategic Analysis",
            "other": "Business Analysis",
        }
        eng_type = engagement_label.get(issue_type, "Business Analysis")

        result = {
            "company": company,
            "ticker": ticker or "",
            "issue": issue,
            "issue_type": issue_type,
            "engagement_type": eng_type,
            "conversation": conversation,
            "status": "running",
            "generated_at": datetime.now().isoformat(),
            "financials": {},
            "multi_year_financials": {},
            "price_history": {},
            "competitor_benchmark": {},
            "industry_benchmark": {},
            "company_data": {},
            "analysis": {},
            "recommendations": {},
            "before_after": {},
            "documents_ingested": [],
            "deliverable_path": "",
        }

        # 1. Web research
        result["company_data"] = self.web.research_company(company)

        # 2. Financial data (only if public ticker)
        if ticker:
            fin = self.financial.get_company_financials(ticker)
            if "error" not in fin:
                result["financials"] = fin
            multi = self.financial.get_multi_year_financials(ticker)
            if "error" not in multi:
                result["multi_year_financials"] = multi
            price = self.financial.get_stock_price_history(ticker)
            if "error" not in price:
                result["price_history"] = price
            bench = self.market.competitor_benchmarking(ticker, question=issue)
            if "error" not in bench:
                result["competitor_benchmark"] = bench
            ind_bench = self.market.industry_benchmarks(ticker, question=issue)
            if "error" not in ind_bench:
                result["industry_benchmark"] = ind_bench

        # 3. Document ingestion
        parsed_data = {"employees": [], "financials": [], "notes": ""}
        if documents:
            for doc in documents:
                content = self.doc_reader.read_file(doc)
                parsed_data["notes"] += f"\n--- {os.path.basename(doc)} ---\n{content[:15000]}"
                result["documents_ingested"].append(os.path.basename(doc))
                # Parse CSV for employee data
                if doc.endswith(".csv"):
                    parsed = self.doc_reader.parse_employee_csv(doc)
                    if parsed:
                        parsed_data["employees"].extend(parsed)

        # 4. Build analysis prompt based on issue type
        system = self._build_issue_prompt(eng_type, issue_type, conv_summary)

        user_msg = f"Company: {company}\nIssue: {issue}\n\nConversation summary:\n{conv_summary}\n\n"
        if result["financials"]:
            user_msg += f"Financial data:\n{json.dumps(result['financials'], indent=2, default=str)[:2000]}\n\n"
        if result.get("multi_year_financials", {}).get("years"):
            user_msg += f"Multi-year trends:\n{json.dumps(result['multi_year_financials'], indent=2, default=str)[:2000]}\n\n"
        if result.get("competitor_benchmark", {}).get("strengths"):
            user_msg += f"Competitor benchmarks:\n{json.dumps(result['competitor_benchmark'], indent=2, default=str)[:2000]}\n\n"
        if parsed_data["notes"]:
            user_msg += f"User-provided documents:\n{parsed_data['notes'][:6000]}\n\n"
        if parsed_data["employees"]:
            user_msg += f"Employee data ({len(parsed_data['employees'])} records):\n{json.dumps(parsed_data['employees'][:30], default=str)[:3000]}\n\n"

        analysis = self.llm.structured_heavy(system, [{"role": "user", "content": user_msg}], {
            "type": "object",
            "properties": {
                "executive_summary": {"type": "string"},
                "detailed_analysis": {"type": "string"},
                "findings": {"type": "array", "items": {"type": "string"}},
            },
        })
        analysis_dict = analysis if isinstance(analysis, dict) else {}
        result["analysis"] = analysis_dict

        # 5. Deep research loop
        result = self._deep_research_loop(result)

        # 6. Recommendations
        recs = self.llm.structured_heavy(
            "You are a senior partner at a top consulting firm. "
            "Based on the analysis, provide strategic recommendations and risk assessment. "
            "Return JSON with: recommendations (3-5 specific recommendations numbered format), "
            "risks (3-5 risks with mitigation strategies).",
            [{"role": "user", "content": f"Company: {company}\nIssue type: {issue_type}\n\nAnalysis: {(result.get('analysis') or {}).get('detailed_analysis', '')[:4000]}\n\nFindings: {json.dumps((result.get('analysis') or {}).get('findings', []))}"}],
            {"type": "object", "properties": {"recommendations": {"type": "string"}, "risks": {"type": "string"}}},
        )
        recs_dict = recs if isinstance(recs, dict) else {}
        result["recommendations"] = recs_dict

        # 7. Before/After comparison
        result["before_after"] = self._generate_before_after(company, issue, issue_type, parsed_data, result["analysis"], result["recommendations"])

        result["status"] = "complete"
        return result

    def _build_issue_prompt(self, eng_type: str, issue_type: str, context: str) -> str:
        base = (
            f"You are a senior strategy consultant conducting a '{eng_type}' engagement. "
            "Base your analysis on the client's description, any provided data, financial metrics, and market research. "
            "Be specific, data-driven, and actionable.\n\n"
        )
        specifics = {
            "restructuring": (
                "Focus: Analyze the current team structure and costs. Identify optimal reduction strategy "
                "that minimizes business impact. Consider severance costs, retention risks, org design "
                "best practices, and performance-based criteria. Provide quantified savings and headcount recommendations."
            ),
            "profitability": (
                "Focus: Analyze revenue streams, cost structure, margins, and pricing. Compare against "
                "industry benchmarks. Identify profit improvement levers (revenue growth, cost reduction, "
                "pricing optimization) with quantified impact estimates."
            ),
            "growth": (
                "Focus: Analyze market opportunity, competitive landscape, and company readiness. "
                "Recommend growth channels, market entry strategy, resource requirements, and expected "
                "timeline to scale. Consider organic vs. acquisition paths."
            ),
            "hiring_talent": (
                "Focus: Assess current team structure, skills gaps, and hiring needs. Recommend optimal "
                "team size, role prioritization, sourcing strategy, and timeline. Consider budget "
                "constraints, ramp-up time, and cultural fit."
            ),
            "merger_acquisition": (
                "Focus: Evaluate strategic fit, financial implications, and integration challenges. "
                "Assess valuation, synergy opportunities, cultural compatibility, and regulatory risks. "
                "Provide a clear recommendation with rationale."
            ),
            "operations": (
                "Focus: Identify operational bottlenecks, inefficiencies, and improvement opportunities. "
                "Recommend process changes, technology investments, or workflow optimizations with "
                "quantified efficiency and cost impact projections."
            ),
            "strategy": (
                "Focus: Analyze competitive position, market trends, and strategic options. "
                "Evaluate build vs. buy vs. partner decisions. Provide a clear strategic direction "
                "with implementation roadmap and key milestones."
            ),
            "other": (
                "Focus: Provide a general strategic analysis addressing the client's specific issue. "
                "Use relevant frameworks, data, and benchmarks. Be practical and actionable."
            ),
        }
        return base + specifics.get(issue_type, specifics["other"])

    def _generate_before_after(self, company: str, issue: str, issue_type: str, parsed_data: dict, analysis: dict, recommendations: dict) -> dict:
        system = (
            "You are a senior strategy consultant presenting findings to a client. "
            "Create a clear before/after comparison showing the current state vs. the projected state "
            "after implementing the recommendations.\n\n"
            "Return JSON:\n"
            "{\n"
            '  "before_summary": "<2-3 sentences describing the current state with specific metrics>",\n'
            '  "after_summary": "<2-3 sentences describing the projected state with specific improvements>",\n'
            '  "verdict": "<1-2 sentence clear recommendation>",\n'
            '  "comparison": [\n'
            '    {"metric": "<metric name>", "before": "<value>", "after": "<value>", "change": "<direction and %>"}\n'
            "  ],\n"
            '  "key_benefits": ["<benefit 1>", "<benefit 2>", "<benefit 3>"]\n'
            "}\n\n"
            "Include specific quantified metrics from the analysis. The comparison table should have 4-7 rows "
            "covering the most important dimensions (cost, headcount, revenue, efficiency, timeline, risk)."
        )

        emp_count = len(parsed_data.get("employees", []))
        emp_text = f"Employee data available for {emp_count} people." if emp_count else ""
        msg = (
            f"Company: {company}\nIssue: {issue}\nIssue type: {issue_type}\n{emp_text}\n\n"
            f"Executive summary: {(analysis or {}).get('executive_summary', '')[:1500]}\n\n"
            f"Recommendations: {(recommendations or {}).get('recommendations', '')[:1500]}\n\n"
            f"Risks: {(recommendations or {}).get('risks', '')[:1000]}"
        )
        result = self.llm.structured_conversational(system, [{"role": "user", "content": msg}], {
            "type": "object",
            "properties": {
                "before_summary": {"type": "string"},
                "after_summary": {"type": "string"},
                "verdict": {"type": "string"},
                "comparison": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string"},
                            "before": {"type": "string"},
                            "after": {"type": "string"},
                            "change": {"type": "string"},
                        },
                    },
                },
                "key_benefits": {"type": "array", "items": {"type": "string"}},
            },
        })
        return result if isinstance(result, dict) else {}
