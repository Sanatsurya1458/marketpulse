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

"""Firestore database tools for MarketPulse marketing campaigns."""

import datetime
from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded project ID as string.
# On Agent Platform, google.auth.default() and GOOGLE_CLOUD_PROJECT resolve
# to the project number rather than the project ID, which breaks Firestore.
PROJECT_ID = "qwiklabs-gcp-04-318fdaa34ac1"
COLLECTION_NAME = "marketing_campaigns"

_db_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Lazily initializes and returns the Firestore client."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def list_campaigns(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists marketing campaigns from the Firestore database.

    Args:
        status_filter: Optional filter to return campaigns by status (e.g. 'active', 'paused', 'draft').

    Returns:
        A list of dictionaries representing marketing campaigns with their details and metrics.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)
    if status_filter:
        query = query.where("status", "==", status_filter.lower())

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_campaign(campaign_id: str) -> Dict[str, Any]:
    """Retrieves details of a specific marketing campaign by its ID.

    Args:
        campaign_id: The unique ID of the campaign (e.g. 'camp_saas_launch').

    Returns:
        A dictionary with the campaign data, or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(campaign_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Campaign '{campaign_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_campaign(
    campaign_id: str,
    name: str,
    channel: str,
    target_audience: str,
    key_message: str,
    budget_usd: float = 500.0,
    status: str = "draft",
    ad_variants: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Creates or updates a marketing campaign in Firestore.

    Args:
        campaign_id: Unique identifier for the campaign (e.g. 'camp_product_hunt').
        name: Name or title of the marketing campaign.
        channel: Channels targeted (e.g. 'Twitter / X', 'Google Ads', 'LinkedIn', 'Instagram').
        target_audience: Description of the ideal customer persona or audience demographic.
        key_message: Main value proposition or headline for the campaign.
        budget_usd: Total allocated budget in USD. Defaults to 500.0.
        status: Campaign status ('active', 'paused', 'draft', 'completed'). Defaults to 'draft'.
        ad_variants: Optional list of ad copy variations.

    Returns:
        A dictionary confirming the campaign creation/update.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(campaign_id)

    existing = doc_ref.get()
    campaign_data = {
        "id": campaign_id,
        "name": name,
        "channel": channel,
        "target_audience": target_audience,
        "key_message": key_message,
        "budget_usd": budget_usd,
        "status": status.lower(),
        "ad_variants": ad_variants or [],
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    if not existing.exists:
        campaign_data["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        campaign_data["spent_usd"] = 0.0
        campaign_data["clicks"] = 0
        campaign_data["conversions"] = 0
        doc_ref.set(campaign_data)
        action = "created"
    else:
        doc_ref.update(campaign_data)
        action = "updated"

    return {"status": "success", "action": action, "campaign": campaign_data}


def update_campaign_status(campaign_id: str, status: str) -> Dict[str, Any]:
    """Updates the status of an existing marketing campaign (e.g., to activate or pause).

    Args:
        campaign_id: The unique ID of the campaign to update.
        status: The new status ('active', 'paused', 'draft', 'completed').

    Returns:
        A dictionary confirming the status update.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(campaign_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Campaign '{campaign_id}' not found."}

    valid_statuses = ["active", "paused", "draft", "completed"]
    normalized_status = status.lower()
    if normalized_status not in valid_statuses:
        return {"error": f"Invalid status '{status}'. Must be one of: {valid_statuses}"}

    doc_ref.update({
        "status": normalized_status,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    return {"status": "success", "campaign_id": campaign_id, "new_status": normalized_status}
