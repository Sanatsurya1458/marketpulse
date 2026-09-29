# MarketPulse & Video Factory - Comprehensive Local Deployment Guide

This document is an end-to-end operational guide for setting up, configuring, running, and testing the entire **MarketPulse** multi-agent marketing intelligence suite and its automated **Product Demo Video Factory** on a local development machine or clean workstation.

---

## 1. System Requirements & Prerequisites

### Hardware
* **CPU**: 4+ Cores recommended (for smooth headless browser video recording and FFmpeg compositing).
* **RAM**: 8 GB minimum (16 GB recommended).
* **Disk**: 10 GB free space for virtual environments, Playwright browsers, and high-definition video captures.

### Software
* **Operating System**: Linux (Ubuntu 20.04+, Debian 11+), macOS (12+), or Windows WSL2.
* **Python**: Version 3.10 to 3.12 (Python 3.10+ required).
* **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended for deterministic fast installs) or standard pip.
* **Media Compositor**: ffmpeg and ffprobe (version 4.4+).
* **Google Chrome / Chromium**: Installed on system path.
* **Google Cloud SDK**: gcloud CLI installed and authenticated.
* **Git**: Version 2.28+.

---

## 2. Environment Preparation

### 2.1. System Package Installation

#### Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git ffmpeg curl libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2
```

#### macOS (Homebrew):
```bash
brew update
brew install python ffmpeg uv
```

### 2.2. Install uv (Fast Python Package Manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

---

## 3. Repository Setup & Dependencies

### 3.1. Clone the Codebase
```bash
git clone https://github.com/Sanatsurya1458/marketpulse.git
cd marketpulse
```

### 3.2. Primary Agent Virtual Environment
Install the primary agent framework dependencies using uv:
```bash
uv sync
```
Or using standard Python venv:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml
```

### 3.3. Dedicated Video Factory Virtual Environment
The video factory utilizes edge-tts, playwright, and moviepy for headless browser recording, neural voiceovers, and frame compositing:
```bash
python3 -m venv /tmp/video_env
/tmp/video_env/bin/pip install edge-tts playwright moviepy pillow numpy httpx
/tmp/video_env/bin/playwright install chromium
```

---

## 4. Google Cloud Authentication & Configuration

MarketPulse connects directly to Google Cloud services (Vertex AI, Cloud Firestore, Cloud Storage, and Agent Platform Sandbox).

### 4.1. Authenticate with Google Cloud
Run both user and application-default login:
```bash
# 1. Sign in to your Google Cloud user account
gcloud auth login

# 2. Acquire application-default credentials for client libraries (Firestore, Storage, Vertex AI)
gcloud auth application-default login

# 3. Set your active target GCP Project ID
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

### 4.2. Verify Enabled APIs
Ensure the necessary APIs are active on your project:
```bash
gcloud services enable   aiplatform.googleapis.com   firestore.googleapis.com   storage.googleapis.com   run.googleapis.com
```

### 4.3. Set Up Cloud Storage Bucket
Create a public storage bucket to host marketing ad creatives and demo videos:
```bash
gsutil mb -l us-east1 gs://marketpulse-assets-$GCP_PROJECT_ID
gsutil iam ch allUsers:objectViewer gs://marketpulse-assets-$GCP_PROJECT_ID
```

### 4.4. Initialize & Seed Cloud Firestore
Create a Firestore Native database if one does not exist:
```bash
gcloud firestore databases create --location=nam5 --type=firestore-native
```
Seed initial marketing campaigns into Firestore:
```bash
uv run python3 seed_firestore.py
```

---

## 5. Environment Variables & Credentials Configuration

Create a local .env file in the project root:
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT="your-project-id"
GCP_REGION="us-east1"

# Cloud Storage
ASSETS_BUCKET="marketpulse-assets-your-project-id"

# Optional: Social Distribution Live Credentials
# If left empty, MarketPulse operates in simulated Sandbox mode with Firestore audit logs.
LINKEDIN_ACCESS_TOKEN=""
LINKEDIN_ORG_URN="urn:li:organization:12345678"
META_ACCESS_TOKEN=""
FB_PAGE_ACCESS_TOKEN=""
FB_PAGE_ID=""
IG_USER_ID=""
AYRSHARE_API_KEY=""
```

---

## 6. Running MarketPulse Locally

### Option A: Local ADK Web Playground (Interactive Chat UI)
The Agent Development Kit (ADK) provides an interactive web interface with conversation history and dynamic A2UI card rendering:
```bash
uv run adk web . --port 8080 --reload_agents
```
* **URL**: Open http://localhost:8080 in your browser.
* **Testing Prompts**:
  * "List all active marketing campaigns in our database."
  * "Generate a modern ad creative banner showing ATS Resume Scanning."
  * "Publish our ATS Resume Builder launch to LinkedIn, Instagram, and Facebook."

---

### Option B: Running the Custom FastAPI Proxy & Frontend
MarketPulse includes a lightweight FastAPI proxy for production chat embedding:
```bash
cd frontend
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
* **URL**: Open http://localhost:8000 to access the standalone chat client.

---

## 7. Running the Product Demo Video Generator Locally

The video pipeline operates deterministically and does not require a browser window (runs headlessly).

### 7.1. Generate the Real UI Screenshot Demo Video
Captures live platform screens from https://mydigitalidentity.co.in, overlays neural narration, dynamic lower-thirds, and renders both landscape and vertical videos:
```bash
PYTHONPATH=. /tmp/video_env/bin/python3 /tmp/record_real_screenshot_video.py
```

### 7.2. Generate the Interactive Workflow Video
Launches the interactive deterministic web app (demo_app.html), animates virtual camera zooms, human-like cursor movements, clicks, and multi-track audio:
```bash
PYTHONPATH=. /tmp/video_env/bin/python3 -m marketpulse.marketing.video.renderer
```

### 7.3. Video Output Files
All generated outputs are saved in `marketing/video/output/`:
* `my_digital_identity_real_demo_16x9.mp4`: 1920x1080 @ 60 FPS Landscape Master.
* `my_digital_identity_real_demo_9x16.mp4`: 1080x1920 Vertical (Shorts/Reels).
* `real_thumbnail.png`: 1080p high-contrast video thumbnail.
* `narration.srt`: Millisecond-synchronized subtitles.
* `validation_report.json`: Audio/video stream diagnostic results.

---

## 8. Verifying Your Local Deployment

Run the automated verification scripts to ensure all components function properly:

1. **Social Distribution & Cloud Firestore Test**:
```bash
uv run python3 /tmp/test_social.py
```

2. **Video Quality Validator Test**:
```bash
/tmp/video_env/bin/python3 -c "
from marketpulse.marketing.video.validators.video_validator import VideoQualityValidator
res = VideoQualityValidator.inspect('marketing/video/output/my_digital_identity_real_demo_16x9.mp4')
print('Validation passed:', res.get('valid'), res.get('width'), 'x', res.get('height'))
"
```

---

## 9. Troubleshooting & FAQ

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'a2ui'` | Running outside project virtualenv | Execute with `uv run python3` or activate `.venv`. |
| `Playwright error: Host system missing dependencies` | Linux missing graphics libraries | Run `playwright install-deps chromium` or install `libnss3`, `libgbm1`. |
| `PermissionDenied: 403 Access Denied` on GCS | Application-default credentials missing | Run `gcloud auth application-default login` and verify bucket permissions. |
| `ffprobe: command not found` | FFmpeg not installed on host path | Run `sudo apt install -y ffmpeg` or `brew install ffmpeg`. |
| `Firestore UNAUTHENTICATED` | Incorrect project ID or token expired | Check `gcloud config get-value project` and refresh credentials. |

---

## 10. Summary of Architectural Files

```
marketpulse/
├── app/
│   ├── agent.py               # Root orchestrator & sub-agent definitions
│   ├── campaign_tools.py      # Firestore campaign manager tools
│   ├── creative_tools.py      # Vertex AI image/video generation & GCS uploads
│   ├── intelligence_tools.py  # Competitor SERP & ROI funnel simulator
│   ├── scanner_tools.py       # Website & codebase profiler
│   └── social_tools.py        # Multi-platform social publisher (LinkedIn, IG, FB)
├── marketing/video/
│   ├── camera.py              # Virtual camera pan/zoom & spotlight
│   ├── cursor.py              # Bezier mouse cursor motion simulation
│   ├── renderer.py            # Master video factory pipeline
│   ├── audio/audio_engine.py  # Neural voiceover, ambient pad, and UI sound effects
│   ├── demo/demo_app.html     # Interactive deterministic demo UI
│   └── validators/            # Frame & audio stream quality validators
├── LOCAL_DEPLOYMENT_GUIDE.md  # Comprehensive local setup & runbook
├── WORKFLOW.md                # System workflow and architecture flowchart
├── HANDOFF.md                 # Production handoff and asset catalog
└── README.md                  # Project overview and public links
```
