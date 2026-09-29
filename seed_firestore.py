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

"""Seed initial marketing campaigns into Firestore for MarketPulse."""

import datetime
from google.cloud import firestore

# NOTE: Project ID must be a hardcoded string.
# On Agent Platform, google.auth.default() and GOOGLE_CLOUD_PROJECT resolve
# to the project number rather than the project ID, which breaks Firestore.
PROJECT_ID = "qwiklabs-gcp-04-318fdaa34ac1"
COLLECTION_NAME = "marketing_campaigns"

SAMPLE_CAMPAIGNS = [
    {
        "id": "camp_saas_launch",
        "name": "Q3 SaaS Early Access Launch",
        "channel": "Twitter / X & LinkedIn",
        "target_audience": "Tech startup founders, CTOs, and engineering leads",
        "status": "active",
        "budget_usd": 1500.0,
        "spent_usd": 420.0,
        "clicks": 1840,
        "conversions": 142,
        "key_message": "Automate your dev workflows 10x faster with AI-native pipelines.",
        "ad_variants": [
            "Tired of manual build pipelines? Let our autonomous agent handle it.",
            "Ship software faster with zero boilerplate. Try early access today.",
        ],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "id": "camp_ecommerce_summer",
        "name": "Summer Flash Sale & Retargeting",
        "channel": "Instagram & Meta Ads",
        "target_audience": "Active shoppers aged 18-35 interested in sustainable fashion",
        "status": "active",
        "budget_usd": 3000.0,
        "spent_usd": 1890.0,
        "clicks": 6200,
        "conversions": 415,
        "key_message": "Up to 40% off organic eco-wear. Sustainable style made effortless.",
        "ad_variants": [
            "Refresh your summer wardrobe sustainably. Limited stock at 40% off!",
            "Look good, feel good. Eco-friendly fabrics designed for warm weather.",
        ],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "id": "camp_developer_newsletter",
        "name": "Weekly Growth & Dev Newsletter Sponsorship",
        "channel": "Substack & Dev.to",
        "target_audience": "Full-stack developers and AI enthusiasts",
        "status": "draft",
        "budget_usd": 800.0,
        "spent_usd": 0.0,
        "clicks": 0,
        "conversions": 0,
        "key_message": "Get the top curated agentic AI tutorials directly in your inbox.",
        "ad_variants": [
            "Master autonomous agents with bite-sized weekly engineering breakdowns.",
        ],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
    {
        "id": "camp_seo_webinar",
        "name": "High-Converting Website SEO Webinar",
        "channel": "Google Search & YouTube Ads",
        "target_audience": "Growth marketers, product managers, and indie hackers",
        "status": "paused",
        "budget_usd": 1200.0,
        "spent_usd": 750.0,
        "clicks": 2100,
        "conversions": 89,
        "key_message": "Live workshop: Turn website visitors into paying customers.",
        "ad_variants": [
            "Stop losing site traffic. Join our free conversion optimization masterclass.",
        ],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    },
]


def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SAMPLE_CAMPAIGNS:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  [Seeded] Campaign '{item['name']}' -> ID: {doc_id}")

    print(f"Successfully seeded {len(SAMPLE_CAMPAIGNS)} campaigns into '{COLLECTION_NAME}' collection.")


if __name__ == "__main__":
    seed_database()
