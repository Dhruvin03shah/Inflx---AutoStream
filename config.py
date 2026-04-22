"""
AutoStream AI Agent - Configuration Module
Manages API keys, model settings, and application constants.
"""

import os
import logging

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_LEVEL = logging.INFO

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger("autostream.config")

# ---------------------------------------------------------------------------
# Groq API
# ---------------------------------------------------------------------------
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    logger.warning(
        "GROQ_API_KEY not found in environment variables. "
        "Set it via: $env:GROQ_API_KEY='your-key' (PowerShell) or "
        "export GROQ_API_KEY='your-key' (bash)."
    )

LLM_MODEL = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# Knowledge-base path
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

# ---------------------------------------------------------------------------
# Intent labels
# ---------------------------------------------------------------------------
INTENT_GREETING = "greeting"
INTENT_INQUIRY = "product_inquiry"
INTENT_HIGH_INTENT = "high_intent_lead"

# ---------------------------------------------------------------------------
# Lead-capture field order
# ---------------------------------------------------------------------------
LEAD_FIELDS = ["name", "email", "platform"]
LEAD_FIELD_PROMPTS = {
    "name": "Could you share your full name so we can set things up for you?",
    "email": "Great! What's the best email address to reach you at?",
    "platform": (
        "Almost done! Which creator platform do you primarily use? "
        "(e.g., YouTube, TikTok, Instagram, Twitch)"
    ),
}
