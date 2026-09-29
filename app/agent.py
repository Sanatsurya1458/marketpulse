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

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
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
from .creative_tools import (
    generate_ad_creative,
    generate_campaign_image,
    generate_campaign_video,
)
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
        "using gemini-3.1-flash-lite-image (via generate_campaign_image), short video teasers and promos "
        "using Google's Omni model gemini-omni-flash-preview (via generate_campaign_video), saving artifacts "
        "and uploading assets directly to public Cloud Storage for web embedding."
    ),
    tools=[generate_campaign_image, generate_campaign_video, generate_ad_creative],
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

a2ui_schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

ROOT_INSTRUCTION = a2ui_schema_manager.generate_system_prompt(
    role_description=(
        "You are MarketPulse, an autonomous digital marketing strategist agent. "
        "You orchestrate specialized capabilities to help users grow their business, scan their product or website, "
        "manage marketing campaigns in Firestore, generate ad copy variations, and create visual ad assets and short video teasers. "
        "You can safely run Python code calculations in a secure Agent Engine sandbox. "
        "You remember and strictly respect the user's stated preferences, dietary restrictions, and allergies (e.g. food, drug, contact allergies) from previous sessions to personalize your interactions and recommendations safely."
    ),
    workflow_description="Analyze the marketing request, coordinate tools, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

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
        generate_campaign_video,
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
