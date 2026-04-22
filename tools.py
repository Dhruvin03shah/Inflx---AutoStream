"""
AutoStream AI Agent - Tools
Mock tool functions that the agent can invoke once lead data is fully collected.
"""

import logging
import re
from typing import Dict

logger = logging.getLogger("autostream.tools")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
_VALID_PLATFORMS = {
    "youtube", "tiktok", "instagram", "twitch", "facebook",
    "linkedin", "twitter", "x", "vimeo", "dailymotion", "other",
}


def validate_name(name: str) -> tuple[bool, str]:
    """Return (is_valid, error_or_clean_value)."""
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, "Name must be at least 2 characters long."
    if not all(c.isalpha() or c.isspace() or c in ".-'" for c in cleaned):
        return False, "Name should only contain letters, spaces, hyphens, or apostrophes."
    return True, cleaned.title()


def validate_email(email: str) -> tuple[bool, str]:
    """Return (is_valid, error_or_clean_value)."""
    cleaned = email.strip().lower()
    if _EMAIL_RE.match(cleaned):
        return True, cleaned
    return False, "That doesn't look like a valid email address. Please try again."


def validate_platform(platform: str) -> tuple[bool, str]:
    """Return (is_valid, error_or_clean_value)."""
    cleaned = platform.strip().lower()
    if cleaned in _VALID_PLATFORMS:
        return True, cleaned.capitalize()
    # Fuzzy: check if any valid platform is a substring
    for p in _VALID_PLATFORMS:
        if p in cleaned or cleaned in p:
            return True, p.capitalize()
    return False, (
        f"I didn't recognize that platform. Please choose one of: "
        f"{', '.join(sorted(p.capitalize() for p in _VALID_PLATFORMS))}."
    )


FIELD_VALIDATORS = {
    "name": validate_name,
    "email": validate_email,
    "platform": validate_platform,
}


# ---------------------------------------------------------------------------
# Mock lead-capture tool
# ---------------------------------------------------------------------------

def mock_lead_capture(name: str, email: str, platform: str) -> Dict[str, str]:
    from datetime import datetime
    """Simulate sending lead data to a CRM / webhook."""
    logger.info(
        "🚀 LEAD CAPTURED → Name: %s | Email: %s | Platform: %s",
        name, email, platform,
    )

    lead_id = f"LS-{abs(hash(email)) % 99999:05d}"
    return {
        "status": "success",
        "lead_id": lead_id,
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assigned_to": "sales-team-apac@autostream.io",
        "message": (
            f"Lead captured successfully!\n"
            f"  • Name:     {name}\n"
            f"  • Email:    {email}\n"
            f"  • Platform: {platform}\n"
            f"A member of the AutoStream team will reach out within 24 hours."
        ),
    }
