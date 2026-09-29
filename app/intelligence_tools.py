# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Marketing intelligence and campaign simulation tools for MarketPulse.

Includes:
1. search_competitor_serp: Fetches live competitor snippets, headlines, and search intelligence.
2. simulate_campaign_roi: Computes projected clicks, CAC, conversions, and budget allocations.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import httpx


def search_competitor_serp(query: str, max_results: int = 4) -> Dict[str, Any]:
    """Searches live web search results to gather competitor messaging, SERP headlines, and search trends.

    Args:
        query: Search keywords or competitor topic (e.g. 'AI developer tools' or 'sustainable fashion ecommerce').
        max_results: Maximum number of search results to retrieve (default: 4).

    Returns:
        A dictionary containing search snippets, competitor titles, and target query info.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        url = f"https://html.duckduckgo.com/html/?q={httpx.URL(query)}"
        with httpx.Client(timeout=8.0, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Dict[str, str]] = []

        result_elements = soup.find_all("div", class_="result")
        for el in result_elements:
            title_tag = el.find("a", class_="result__a")
            snippet_tag = el.find("a", class_="result__snippet")
            url_tag = el.find("a", class_="result__url")

            if title_tag and snippet_tag:
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True)
                link = url_tag.get_text(strip=True) if url_tag else ""

                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                })
                if len(results) >= max_results:
                    break

        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "competitor_insights": results,
        }
    except Exception as e:
        return {
            "error": f"Failed to retrieve competitor SERP results: {str(e)}",
            "query": query,
        }


def simulate_campaign_roi(
    budget_usd: float,
    channel: str = "Google Search",
    target_cpc: Optional[float] = None,
    conversion_rate_pct: float = 2.5,
    average_order_value_usd: float = 75.0,
) -> Dict[str, Any]:
    """Calculates projected marketing performance, customer acquisition cost (CAC), and return on ad spend (ROAS).

    Args:
        budget_usd: Total planned ad spend in USD (e.g. 1500.0).
        channel: Target advertising channel (e.g. 'Google Search', 'Meta / Instagram', 'LinkedIn', 'Twitter / X').
        target_cpc: Optional estimated Cost Per Click in USD. If omitted, benchmark averages are used based on channel.
        conversion_rate_pct: Estimated conversion rate percentage from visitor to customer (e.g. 2.5 for 2.5%).
        average_order_value_usd: Average revenue per paying customer/conversion in USD (default: 75.0).

    Returns:
        A dictionary with projected clicks, estimated conversions, CAC, revenue, and ROAS.
    """
    # Industry benchmark cost-per-click averages
    benchmarks = {
        "google search": 2.20,
        "meta": 1.10,
        "instagram": 1.25,
        "linkedin": 4.50,
        "twitter": 1.40,
        "youtube": 1.80,
    }

    cpc = target_cpc
    if cpc is None or cpc <= 0:
        cpc = 1.75
        for ch_key, ch_val in benchmarks.items():
            if ch_key in channel.lower():
                cpc = ch_val
                break

    cvr = max(0.001, conversion_rate_pct / 100.0)
    estimated_clicks = int(budget_usd / cpc) if cpc > 0 else 0
    estimated_conversions = int(estimated_clicks * cvr)
    estimated_revenue = estimated_conversions * average_order_value_usd
    cac = round(budget_usd / max(1, estimated_conversions), 2)
    roas = round((estimated_revenue / budget_usd) * 100, 1) if budget_usd > 0 else 0.0

    return {
        "status": "success",
        "channel": channel,
        "budget_usd": budget_usd,
        "estimated_cpc_usd": round(cpc, 2),
        "conversion_rate_pct": conversion_rate_pct,
        "average_order_value_usd": average_order_value_usd,
        "projected_clicks": estimated_clicks,
        "projected_conversions": estimated_conversions,
        "projected_revenue_usd": round(estimated_revenue, 2),
        "customer_acquisition_cost_usd": cac,
        "return_on_ad_spend_pct": roas,
        "summary": (
            f"With a ${budget_usd:,.2f} budget on {channel} at ${cpc:.2f} CPC and {conversion_rate_pct}% CVR: "
            f"~{estimated_clicks:,} clicks, ~{estimated_conversions:,} conversions, CAC: ${cac:.2f}, "
            f"Projected Revenue: ${estimated_revenue:,.2f} ({roas}% ROAS)."
        ),
    }


def fetch_industry_trends(topic: str, max_items: int = 5) -> Dict[str, Any]:
    """Fetches real-time market trends, viral discussions, and developer sentiment from the free Hacker News API.

    Args:
        topic: The industry topic, technology, or niche to check trends for (e.g. 'AI agents', 'marketing', 'SaaS').
        max_items: Number of trending discussions to return (default: 5).

    Returns:
        A dictionary containing trending headlines, engagement points, comments count, and article URLs.
    """
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "query": topic,
        "tags": "story",
        "hitsPerPage": max(1, min(max_items, 10)),
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        hits = data.get("hits", [])
        trends = []
        for h in hits:
            trends.append({
                "title": h.get("title"),
                "url": h.get("url") or f"https://news.ycombinaator.com/item?id={h.get('objectID')}",
                "points": h.get("points", 0),
                "comments": h.get("num_comments", 0),
                "created_at": h.get("created_at"),
            })

        return {
            "status": "success",
            "topic": topic,
            "count": len(trends),
            "trends": trends,
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch market trends for '{topic}': {str(e)}",
            "topic": topic,
        }

