# 🚀 MarketPulse — Autonomous Digital Marketing & Growth Agent

> An intelligent, multi-agent AI system built on Google's Agent Development Kit (ADK) and Gemini 2.5. MarketPulse scans websites or codebases, manages marketing campaigns with Firestore persistence, generates visual ad creatives via Cloud Storage, surfaces real-time market trends, and models financial ROI/CAC metrics.

---

## 🌟 Highlights & Capabilities

- **🔍 Automated Website & Codebase Profiler**
  - Live URL scanner (`scan_website_url`) extracts `<title>`, OpenGraph data, headings, and value propositions.
  - Local repository scanner (`scan_local_codebase`) inspects `README`, `package.json`, and project configs to profile apps.
- **📊 Firestore Campaign Backend**
  - Manages active, draft, and paused marketing campaigns in Google Cloud Firestore.
  - Complete read/write/update toolset (`list_campaigns`, `get_campaign`, `save_campaign`, `update_campaign_status`).
- **🎨 Visual Ad Creative Generator**
  - Generates high-resolution ad banners with custom headlines, brand badges, and call-to-action hooks.
  - Automatically uploads to a public Google Cloud Storage bucket (`marketpulse-assets-...`) with public HTTPS URLs.
- **📈 Market Intelligence & Trend Discovery**
  - Queries live Hacker News trends and community discussions via public APIs to spot viral narratives and sentiment.
  - Competitor SERP search tool (`search_competitor_serp`) extracts real-world search headlines and competitor messaging.
- **🧮 Financial ROI & CAC Funnel Simulator**
  - Computes clicks, conversions, Customer Acquisition Cost (CAC), and Return on Ad Spend (ROAS %) across channels (Google Search, Meta, LinkedIn, Twitter/X).
- **📱 A2UI Rich UI Cards**
  - Emits A2UI v0.8 schemas natively rendered as visual cards, comparison columns, and embedded images.

---

## 🏛️ Multi-Agent Architecture

```
                       ┌─────────────────────────────────────────┐
                       │               MarketPulse               │
                       │           (root_agent / Gemini)          │
                       └─┬──────────────────┬──────────────────┬─┘
                         │                  │                  │
                         ▼                  ▼                  ▼
             ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
             │  Profiler Agent  │ │  Creative Agent  │ │  Analyst Agent   │
             ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
             │ • Web URL Fetch  │ │ • Ad Banners     │ │ • SERP Search    │
             │ • Local Repo     │ │ • GCS Upload     │ │ • HN Trends      │
             │   Inspection     │ │ • Public CDN     │ │ • ROI Simulation │
             └──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## 📁 Repository Structure

```
marketpulse/
├── app/
│   ├── agent.py                 # Multi-agent definitions, instructions & A2UI callback
│   ├── campaign_tools.py        # Firestore database read/write/status tools
│   ├── scanner_tools.py         # Live URL and local codebase profiling
│   ├── creative_tools.py        # Ad banner generator & Cloud Storage uploader
│   ├── intelligence_tools.py    # SERP intelligence, HN trends & ROI simulation
│   ├── a2ui_utils.py            # A2UI v0.8 message rewrapping callback
│   └── fast_api_app.py          # FastAPI application server
├── seed_firestore.py            # Script to seed initial marketing campaigns
├── agents-cli-manifest.yaml     # Google Agents CLI deployment manifest
├── pyproject.toml               # Python package configuration & dependencies
└── README.md                    # Project documentation
```

---

## 🛠️ Prerequisites & Setup

1. **Python & uv**:
   ```bash
   # uv package manager handles all environments and dependencies
   uv sync
   ```

2. **Google Cloud Services**:
   - Google Cloud Project with Firestore & Cloud Storage enabled
   - Authenticated with Google Cloud (`gcloud auth application-default login`)

3. **Seed Firestore Database**:
   ```bash
   uv run python seed_firestore.py
   ```

---

## 💻 Running Locally

### Interactive ADK Web Development UI
Launch the local ADK playground to test multi-turn conversations and inspect A2UI cards:

```bash
uv run adk web --port 8080 --allow_origins "*" --reload_agents
```

### FastAPI Server
```bash
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📄 License
Licensed under the Apache License, Version 2.0.
