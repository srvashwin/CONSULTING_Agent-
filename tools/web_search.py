import json
import re
import urllib.parse
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from core.config import config


class WebSearchTool:
    def __init__(self):
        self.tavily_key = config.TAVILY_API_KEY

    def search(self, query: str, num_results: int = None) -> List[dict]:
        num = num_results or config.MAX_SEARCH_RESULTS
        results = self._tavily_search(query, num)
        if results:
            return results
        return self._ddg_search(query, num)

    def fetch_page(self, url: str, max_chars: int = 5000) -> str:
        try:
            resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0, follow_redirects=True)
            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return text[:max_chars]
        except Exception as e:
            return f"Error fetching page: {e}"

    def research_company(self, company_name: str) -> dict:
        queries = [
            f"{company_name} company overview revenue 2025 2026",
            f"{company_name} business model competitors market share",
            f"{company_name} recent news strategy 2026",
            f"{company_name} SWOT analysis strengths weaknesses",
        ]
        all_results = []
        for q in queries:
            all_results.extend(self.search(q, num_results=3))

        seen_urls = set()
        results_deduped = []
        for r in all_results:
            u = r.get("url", "")
            if u and u not in seen_urls:
                seen_urls.add(u)
                results_deduped.append(r)

        pages = []
        for r in results_deduped[:6]:
            url = r.get("url", "")
            if url:
                content = self.fetch_page(url)
                pages.append({"url": url, "content": content})

        return {
            "search_results": results_deduped[:12],
            "pages": pages,
        }

    def _tavily_search(self, query: str, num_results: int) -> Optional[List[dict]]:
        if not self.tavily_key:
            return None
        import urllib.request
        endpoint = "https://api.tavily.com/search"
        payload = json.dumps({
            "api_key": self.tavily_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": min(num_results, 20),
            "topic": "general",
        }).encode()
        try:
            req = urllib.request.Request(
                endpoint, data=payload, headers={"Content-Type": "application/json"}
            )
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            results = []
            for r in data.get("results", []):
                content = r.get("content", r.get("snippet", ""))
                clean = re.sub(r'#+ |\*\*|__|\[.*?\]\(.*?\)|\|', '', content)
                clean = clean.strip().split('\n')[0]
                if len(clean) > 150:
                    clean = clean[:147] + "..."
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": clean,
                    "score": r.get("score", 0),
                    "source": "tavily",
                })
            return results if results else None
        except Exception:
            return None

    def _ddg_search(self, query: str, num_results: int) -> List[dict]:
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for r in soup.select(".result")[:num_results]:
                title_el = r.select_one(".result__title a")
                snippet_el = r.select_one(".result__snippet")
                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": title_el.get("href", ""),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                        "source": "duckduckgo",
                    })
            return results
        except Exception as e:
            return [{"title": "Search failed", "url": "", "snippet": str(e), "source": "ddg_error"}]
