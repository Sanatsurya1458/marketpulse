# MarketPulse: Autonomous Digital Marketing & Growth Agent

MarketPulse is a multi-agent digital marketing strategist built on the Google Agent Development Kit (ADK) and deployed to Google Cloud Agent Platform. It coordinates specialized sub-agents to scan websites or codebases, manage marketing campaign catalogs, forecast ROI funnels, generate visual ad creative banners and short promo videos, and retain persistent memory across user sessions.

![MarketPulse Demo](assets/demo.gif)

---

## What the Agent Actually Does

MarketPulse implements an orchestrator-worker multi-agent architecture with three specialized sub-agents and a centralized root agent:

### 1. Specialized Sub-Agents & Capabilities
* **`profiler_agent` (Website & Codebase Profiler)**:
  * Scans public web URLs (`scan_website_url`) to extract meta tags, headlines, key product features, and target customer profiles.
  * Inspects local project repositories (`scan_local_codebase`) reading `package.json`, `pyproject.toml`, and `README.md` to profile technical products.
* **`creative_agent` (Creative Designer Specialist)**:
  * Renders digital marketing banners (`generate_ad_creative`) with gradient themes and value propositions.
  * Generates visual concepts and marketing hero assets using `gemini-3.1-flash-lite-image` (`generate_campaign_image`).
  * Produces short video teasers and promos using Google's Omni model `gemini-omni-flash-preview` in the global region (`generate_campaign_video`).
  * Saves generated images and videos directly as ADK Playground artifacts (`tool_context.save_artifact`) and uploads them to public Google Cloud Storage.
* **`analyst_agent` (Market Intelligence & Growth Analyst)**:
  * Scrapes live competitor search results and SERP messaging trends (`search_competitor_serp`).
  * Fetches real-time industry discussions, tech news, and developer sentiment from Hacker News (`fetch_industry_trends`).
  * Simulates campaign budget models, forecasting impressions, CPC, CAC, and conversion funnels (`simulate_campaign_roi`).
  * Runs complex Python models inside a secure **Agent Engine Sandbox** (`AgentEngineSandboxCodeExecutor`).

---

## Google Cloud Services Wired Up

The agent code directly interacts with the following Google Cloud services and models:

| Service / Component | Purpose in MarketPulse | Implementation Reference |
| :--- | :--- | :--- |
| **Vertex AI Agent Engine (Memory Bank)** | Cross-session long-term memory for remembering user preferences, brand tone, and constraints. | [`PreloadMemoryTool`](app/agent.py) & `generate_memories_callback` via `agentengine://<MEMORY_BANK_ID>` |
| **Cloud Firestore** | Persistent database storage for marketing campaign records, status toggles, target channels, and budgets. | [`app/campaign_tools.py`](app/campaign_tools.py) querying collection `marketing_campaigns` |
| **Cloud Storage** | Public object storage for ad banners, generated creatives, and demo videos. | [`app/creative_tools.py`](app/creative_tools.py) uploading to bucket `marketpulse-assets-<PROJECT_ID>` |
| **Vertex AI Generative AI** | Core reasoning, image synthesis, and short video generation. | `gemini-2.5-flash` (agent model), `gemini-3.1-flash-lite-image` (images), and `gemini-omni-flash-preview` (video) |
| **Agent Engine Code Sandbox** | Isolated remote Python sandbox execution for marketing ROI and conversion calculations. | [`AgentEngineSandboxCodeExecutor`](app/agent.py) |
| **A2UI (v0.8 Basic Catalog)** | Dynamic server-driven UI cards, rows, columns, and embedded images. | [`a2ui_callback`](app/a2ui_utils.py) and frontend A2UI client renderer |

---

## Planned / Roadmap (Not Yet Implemented)
* Automated live ad placement via Google Ads / Meta Ads API integrations (planned, not yet implemented).
* Continuous background schedule cron workers for automatic competitor price alerting (planned, not yet implemented).

---

## Local Setup & Development

### Prerequisites
* Python 3.10+
* `uv` package and project manager
* Google Cloud CLI (`gcloud`) authenticated to your GCP project with permissions for Vertex AI, Firestore, and Cloud Storage.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sanatsurya1458/marketpulse.git
   cd marketpulse
   ```

2. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project <YOUR_PROJECT_ID>
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Launch the local ADK Web Playground**:
   ```bash
   uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<YOUR_MEMORY_BANK_ID>
   ```

5. **Run the Custom Frontend Proxy (Optional)**:
   ```bash
   cd frontend
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```
