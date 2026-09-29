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

"""Creative designer tools: generate ad banners and upload them to public Cloud Storage."""

import datetime
import io
import math
import re
import uuid
from typing import Any, Dict, Optional
from google.cloud import storage
from PIL import Image, ImageDraw, ImageFont

# Hardcoded project ID as string.
# On Agent Platform, google.auth.default() and GOOGLE_CLOUD_PROJECT resolve
# to the project number rather than the project ID, which breaks GCP clients.
PROJECT_ID = "qwiklabs-gcp-04-318fdaa34ac1"
REGION = "us-east1"
BUCKET_NAME = "marketpulse-assets-qwiklabs-gcp-04-318fdaa34ac1"

_storage_client: Optional[storage.Client] = None


def get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


def _render_creative_banner(title: str, subtitle: str, theme: str = "blue") -> bytes:
    """Renders a sleek, high-resolution gradient digital marketing banner."""
    width, height = 1080, 1080
    base = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(base)

    # Gradient background simulation
    color_schemes = {
        "blue": ((30, 58, 138), (14, 165, 233), (99, 102, 241)),
        "purple": ((76, 29, 149), (168, 85, 247), (236, 72, 153)),
        "emerald": ((6, 78, 59), (16, 185, 129), (52, 211, 153)),
        "amber": ((120, 53, 15), (245, 158, 11), (251, 191, 36)),
    }
    c1, c2, c3 = color_schemes.get(theme.lower(), color_schemes["blue"])

    for y in range(height):
        factor = y / height
        r = int(c1[0] * (1 - factor) + c2[0] * factor)
        g = int(c1[1] * (1 - factor) + c2[1] * factor)
        b = int(c1[2] * (1 - factor) + c2[2] * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Glow overlay circles
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([-100, -100, 600, 600], fill=(c3[0], c3[1], c3[2], 70))
    glow_draw.ellipse([600, 600, 1200, 1200], fill=(c1[0], c1[1], c1[2], 90))
    base = Image.alpha_composite(base, glow)
    draw = ImageDraw.Draw(base)

    # Card container in center
    margin = 80
    card_box = [margin, margin, width - margin, height - margin]
    draw.rounded_rectangle(card_box, radius=40, fill=(15, 23, 42, 210), outline=(255, 255, 255, 60), width=3)

    # Brand badge
    draw.rounded_rectangle([margin + 60, margin + 60, margin + 300, margin + 120], radius=20, fill=(c2[0], c2[1], c2[2], 230))
    draw.text((margin + 85, margin + 78), "MARKETPULSE", fill=(255, 255, 255, 255), font_size=26)

    # Ad Headline
    clean_title = title if len(title) <= 50 else title[:47] + "..."
    draw.text((margin + 60, margin + 260), clean_title, fill=(255, 255, 255, 255), font_size=56)

    # Subtitle / Value proposition (wrapped)
    words = subtitle.split()
    lines = []
    curr = []
    for w in words:
        if len(" ".join(curr + [w])) <= 34:
            curr.append(w)
        else:
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    wrapped_sub = "\n".join(lines[:4])

    draw.text((margin + 60, margin + 420), wrapped_sub, fill=(203, 213, 225, 255), font_size=34)

    # CTA Button
    btn_y = height - margin - 160
    draw.rounded_rectangle([margin + 60, btn_y, margin + 380, btn_y + 80], radius=24, fill=(c3[0], c3[1], c3[2], 255))
    draw.text((margin + 105, btn_y + 24), "Get Started Now →", fill=(255, 255, 255, 255), font_size=28)

    # Export to bytes
    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()


def generate_ad_creative(
    headline: str,
    subtitle: str,
    campaign_id: str = "general",
    color_theme: str = "blue",
) -> Dict[str, Any]:
    """Generates a high-quality visual advertising banner and uploads it to public Cloud Storage.

    Args:
        headline: Main catchy headline or campaign hook (e.g. 'Accelerate Your AI Growth').
        subtitle: Secondary descriptive copy or value proposition.
        campaign_id: Unique identifier of the campaign this creative belongs to.
        color_theme: Aesthetic color theme: 'blue', 'purple', 'emerald', or 'amber'.

    Returns:
        A dictionary containing the public image URL, bucket URI, and creative metadata.
    """
    clean_campaign = re.sub(r"[^a-zA-Z0-9_-]", "", campaign_id) or "general"
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4().hex[:6]
    object_name = f"creatives/{clean_campaign}_{timestamp}_{unique_suffix}.png"

    try:
        image_bytes = _render_creative_banner(
            title=headline,
            subtitle=subtitle,
            theme=color_theme,
        )

        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"

        return {
            "status": "success",
            "campaign_id": campaign_id,
            "public_url": public_url,
            "gcs_uri": f"gs://{BUCKET_NAME}/{object_name}",
            "headline": headline,
            "subtitle": subtitle,
            "theme": color_theme,
        }
    except Exception as e:
        return {
            "error": f"Failed to generate ad creative: {str(e)}",
            "campaign_id": campaign_id,
        }
