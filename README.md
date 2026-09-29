# MarketPulse: Autonomous Digital Marketing & Product Demo Video Factory

MarketPulse is a multi-agent digital marketing strategist and automated video production system built on the Google Agent Development Kit (ADK), Google Cloud Agent Platform, Playwright, and FFmpeg.

It coordinates specialized sub-agents to scan websites or codebases, manage marketing campaign catalogs, forecast ROI funnels, generate visual ad banners and Omni promo videos, and generate high-production-value, product-led demo videos in multiple aspect ratios (16:9 Landscape & 9:16 Vertical Shorts/Reels) inspired by **My Digital Identity** (`https://mydigitalidentity.co.in`).

![MarketPulse Demo](assets/demo.gif)

---

## What the System Actually Does

MarketPulse implements a dual-capability architecture: an **Autonomous Marketing Strategist Agent** and a **Self-Service Product Demo Video Factory**.

### 1. Product Demo Video Factory (`marketing/video/`)
An automated, real-UI video production pipeline engineered to produce professional product demos:
* **Real UI Demonstration**: Records actual interactive web workflows using Playwright headless Chromium (`demo_app.html` & `reference_slideshow_app.html`), avoiding generic fake AI mockups.
* **Authentic Production UI Screenshots**: Captures and animates live platform screens directly from `https://mydigitalidentity.co.in` (ATS Resume Builder, ATS Score Analytics, Job Tailoring, and Public Portfolio).
* **Virtual Camera System (`camera.py`)**: Smooth programmatic pan, dynamic zoom (`1.15x - 1.25x`), and spotlight masks focusing on active features.
* **Human-like Cursor (`cursor.py`)**: Bezier ease-in-out cursor movement paths with visual click feedback and ripple effects.
* **3-Layer Audio Master (`audio/audio_engine.py`)**:
  * **Neural Voiceover**: Synchronized speech synthesis via Edge-TTS (`en-US-GuyNeural`) generating word-boundary timestamped `.srt` subtitles.
  * **Ambient Background Music**: Procedurally generated ambient chord progression pad (Cmaj7 → Am7 → Fmaj7 → Gsus4) at `-18dB`.
  * **UI Sound Effects**: Procedural high-fidelity clicks (950Hz) and achievement score chimes (659Hz).
* **Multi-Format Adaptation**: Encodes both **16:9 Landscape (1920×1080 @ 60 FPS)** for YouTube/Web and **9:16 Vertical (1080×1920)** for Shorts/Reels.
* **Automated Quality Validator (`validators/video_validator.py`)**: Inspects stream integrity, audio sync, resolution, and black frame dropouts via `ffprobe` and `blackdetect`.

### 2. Specialized Sub-Agents & Marketing Intelligence
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

## Video Deliverables & Live Demos

| Deliverable | Format | Public Stream Link |
| :--- | :--- | :--- |
| **Real UI 16:9 Demo Video** | 1920×1080 @ 60 FPS | [Watch 16:9 Real UI Video](https://storage.googleapis.com/marketpulse-assets-qwiklabs-gcp-04-318fdaa34ac1/demos/my_digital_identity_real_demo_16x9.mp4) |
| **Real UI 9:16 Vertical Video** | 1080×1920 (Shorts/Reels) | [Watch 9:16 Vertical Video](https://storage.googleapis.com/marketpulse-assets-qwiklabs-gcp-04-318fdaa34ac1/demos/my_digital_identity_real_demo_9x16.mp4) |
| **Interactive Workflow 16:9** | 1920×1080 @ 60 FPS | [Watch Interactive 16:9 Video](https://storage.googleapis.com/marketpulse-assets-qwiklabs-gcp-04-318fdaa34ac1/demos/my_digital_identity_demo_16x9.mp4) |
| **Interactive Workflow 9:16** | 1080×1920 | [Watch Interactive 9:16 Video](https://storage.googleapis.com/marketpulse-assets-qwiklabs-gcp-04-318fdaa34ac1/demos/my_digital_identity_demo_9x16.mp4) |
| **High-Contrast Thumbnail** | 1920×1080 PNG | [View Thumbnail](https://storage.googleapis.com/marketpulse-assets-qwiklabs-gcp-04-318fdaa34ac1/demos/real_thumbnail.png) |

---

## Google Cloud Services Wired Up

| Service / Component | Purpose in MarketPulse | Implementation Reference |
| :--- | :--- | :--- |
| **Vertex AI Agent Engine (Memory Bank)** | Cross-session long-term memory for remembering user preferences, brand tone, and constraints. | [`PreloadMemoryTool`](app/agent.py) & `generate_memories_callback` via `agentengine://<MEMORY_BANK_ID>` |
| **Cloud Firestore** | Persistent database storage for marketing campaign records, status toggles, target channels, and budgets. | [`app/campaign_tools.py`](app/campaign_tools.py) querying collection `marketing_campaigns` |
| **Cloud Storage** | Public object storage for ad banners, generated creatives, demo recordings, and video factory outputs. | [`app/creative_tools.py`](app/creative_tools.py) uploading to bucket `marketpulse-assets-<PROJECT_ID>` |
| **Vertex AI Generative AI** | Core reasoning, image synthesis, and short video generation. | `gemini-2.5-flash` (agent model), `gemini-3.1-flash-lite-image` (images), and `gemini-omni-flash-preview` (video) |
| **Agent Engine Code Sandbox** | Isolated remote Python sandbox execution for marketing ROI and conversion calculations. | [`AgentEngineSandboxCodeExecutor`](app/agent.py) |
| **A2UI (v0.8 Basic Catalog)** | Dynamic server-driven UI cards, rows, columns, and embedded images. | [`a2ui_callback`](app/a2ui_utils.py) and frontend A2UI client renderer |

---

## Documentation Links

* **[WORKFLOW.md](WORKFLOW.md)**: End-to-end video pipeline architecture, audio mixing, camera director, and validation flowcharts.
* **[HANDOFF.md](HANDOFF.md)**: Client handoff report, operational runbook, environment setup, and future production roadmap.
* **[VIDEO_DEMO_REPORT.md](VIDEO_DEMO_REPORT.md)**: Technical acceptance test reports and frame validation statistics.

---

## Planned / Roadmap (Not Yet Implemented)
* Automated live ad placement via Google Ads / Meta Ads API integrations (planned, not yet implemented).
* Continuous background schedule cron workers for automatic competitor price alerting (planned, not yet implemented).

---

## Local Setup & Execution

### Prerequisites
* Python 3.10+
* `uv` package and project manager
* FFmpeg (`ffmpeg` and `ffprobe` installed on system path)
* Google Chrome or Chromium (`playwright install chromium`)
* Google Cloud CLI (`gcloud`) authenticated to your GCP project.

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

5. **Generate Product Demo Videos**:
   ```bash
   # Run the real platform UI screenshot video generator:
   python3 /tmp/record_real_screenshot_video.py

   # Or run the interactive UI workflow video factory:
   python3 -m marketpulse.marketing.video.renderer
   ```
