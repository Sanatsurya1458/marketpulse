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

"""MarketPulse: Autonomous Digital Marketing & Growth Agent."""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .campaign_tools import (
    get_campaign,
    list_campaigns,
    save_campaign,
    update_campaign_status,
)
from .creative_tools import generate_ad_creative, generate_campaign_image
from .intelligence_tools import (
    fetch_industry_trends,
    search_competitor_serp,
    simulate_campaign_roi,
)
from .scanner_tools import scan_local_codebase, scan_website_url

MODEL = "gemini-2.5-flash"
MEMORY_BANK_ID = "3336127185881661440"
SANDBOX_RESOURCE_NAME = "projects/307546545107/locations/us-east1/reasoningEngines/3336127185881661440/sandboxEnvironments/7972013455236399104"

# Code executor backed by Agent Platform sandbox
code_executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=SANDBOX_RESOURCE_NAME)


# Memory generation callback: extracts and stores durable facts/preferences across turns
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None

# ==========================================
# Specialized Sub-Agents
# ==========================================

profiler_agent = Agent(
    name="profiler_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Website & Codebase Profiler specialist for MarketPulse. "
        "Your role is to scan a website URL or a local codebase repository, extract its core value propositions, "
        "identify key features and target customer personas, and provide structured product intelligence."
    ),
    tools=[scan_website_url, scan_local_codebase],
)

creative_agent = Agent(
    name="creative_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Creative Designer specialist for MarketPulse. "
        "You generate marketing visuals, campaign concept art, and digital ad banners "
        "using gemini-3.1-flash-lite-image (via generate_campaign_image), saving artifacts "
        "and uploading images directly to public Cloud Storage for web embedding."
    ),
    tools=[generate_campaign_image, generate_ad_creative],
)

analyst_agent = Agent(
    name="analyst_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Market Intelligence & Growth Analyst specialist for MarketPulse. "
        "You gather live competitor search insights and SERP messaging trends (via search_competitor_serp), "
        "fetch real-time market trends, viral discussions, and developer sentiment (via fetch_industry_trends), "
        "and perform financial ROI, CAC, and conversion funnel simulations (via simulate_campaign_roi). "
        "You can also write and execute Python code in your secure Agent Engine sandbox to perform complex calculations."
    ),
    tools=[search_competitor_serp, fetch_industry_trends, simulate_campaign_roi],
    code_executor=code_executor,
)

# ==========================================
# Root Orchestrator Agent
# ==========================================

ROOT_INSTRUCTION = """You are MarketPulse, an autonomous digital marketing strategist agent.
You orchestrate specialized capabilities to help users grow their business, scan their product or website,
manage marketing campaigns, generate ad copy variations, and create visual ad assets.
You can safely run Python code calculations in a secure Agent Engine sandbox.

When appropriate to present campaigns, product summaries, or creative banners visually, emit A2UI v0.8 components:
Keep every surface flat and clean: ONE Card > ONE Column > Text and Row components.
Supported components: Card, Column, Row, Text, Image, Divider.
When displaying generated ad creatives, include an Image component with the exact public https:// URL.
Example A2UI surface:
[
  {
    "beginRendering": {
      "surfaceId": "marketpulse-surface",
      "root": "root-card"
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "marketpulse-surface",
      "components": [
        {
          "id": "root-card",
          "component": {
            "Card": {
              "child": "main-col"
            }
          }
        },
        {
          "id": "main-col",
          "component": {
            "Column": {
              "children": ["title-text", "body-text"]
            }
          }
        },
        {
          "id": "title-text",
          "component": {
            "Text": {
              "text": {"literalString": "MarketPulse Strategy"},
              "usageHint": "h1"
            }
          }
        },
        {
          "id": "body-text",
          "component": {
            "Text": {
              "text": {"literalString": "Campaign summary and recommendations here."},
              "usageHint": "body"
            }
          }
        }
      ]
    }
  }
]
Always return actionable, high-impact marketing recommendations.
"""

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ROOT_INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        list_campaigns,
        get_campaign,
        save_campaign,
        update_campaign_status,
        scan_website_url,
        scan_local_codebase,
        generate_campaign_image,
        generate_ad_creative,
        search_competitor_serp,
        fetch_industry_trends,
        simulate_campaign_roi,
    ],
    code_executor=code_executor,
    sub_agents=[profiler_agent, creative_agent, analyst_agent],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
