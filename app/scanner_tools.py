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

"""Website and codebase scanning tools for MarketPulse."""

import json
import os
from typing import Any, Dict
from bs4 import BeautifulSoup
import httpx


def scan_website_url(url: str) -> Dict[str, Any]:
    """Fetches a public website and extracts marketing information, meta tags, and content.

    Args:
        url: The web URL to scan (e.g. 'https://example.com' or 'https://github.com/facebook/react').

    Returns:
        A dictionary containing page title, meta description, keywords, headings, and extracted text.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        with httpx.Client(timeout=12.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        return {
            "error": f"Failed to fetch website at {url}: {str(e)}",
            "url": url,
        }

    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, and svg elements
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()

    og_title = ""
    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    if og_title_tag and og_title_tag.get("content"):
        og_title = og_title_tag["content"].strip()

    headings = []
    for h in soup.find_all(["h1", "h2"]):
        text = h.get_text(separator=" ", strip=True)
        if text and len(text) > 3:
            headings.append(text)

    # Get body preview snippet
    body_text = soup.get_text(separator=" ", strip=True)
    body_snippet = " ".join(body_text.split()[:200])

    return {
        "status": "success",
        "url": url,
        "title": title or og_title,
        "meta_description": meta_desc,
        "headings": headings[:8],
        "content_snippet": body_snippet,
    }


def scan_local_codebase(path: str = ".") -> Dict[str, Any]:
    """Scans a local project directory/repository to profile the application or software.

    Reads files like README.md, package.json, pyproject.toml, or Dockerfile to infer
    what the application does, its tech stack, and key value propositions.

    Args:
        path: Path to the directory or codebase (defaults to current directory '.').

    Returns:
        A dictionary with extracted metadata, readme highlights, and project configuration.
    """
    abs_path = os.path.abspath(path)
    if not os.path.isdir(abs_path):
        return {"error": f"Directory not found: {abs_path}"}

    summary: Dict[str, Any] = {
        "status": "success",
        "scanned_path": abs_path,
        "readme_excerpt": None,
        "project_type": "generic",
        "dependencies_found": [],
        "manifest_info": {},
    }

    # Inspect README
    for readme_name in ["README.md", "README", "readme.md", "readme.txt"]:
        readme_file = os.path.join(abs_path, readme_name)
        if os.path.isfile(readme_file):
            try:
                with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(2500)
                    summary["readme_excerpt"] = content.strip()
                    break
            except Exception:
                pass

    # Inspect package.json
    pkg_json = os.path.join(abs_path, "package.json")
    if os.path.isfile(pkg_json):
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                summary["project_type"] = "Node/JavaScript"
                summary["manifest_info"]["name"] = data.get("name")
                summary["manifest_info"]["description"] = data.get("description")
                summary["dependencies_found"] = list(data.get("dependencies", {}).keys())[:15]
        except Exception:
            pass

    # Inspect pyproject.toml
    pyproject = os.path.join(abs_path, "pyproject.toml")
    if os.path.isfile(pyproject):
        summary["project_type"] = "Python"
        try:
            with open(pyproject, "r", encoding="utf-8") as f:
                content = f.read(1500)
                summary["manifest_info"]["pyproject_snippet"] = content
        except Exception:
            pass

    return summary
