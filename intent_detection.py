"""
AutoStream AI Agent - Intent Detection
Hybrid rule + LLM classifier that maps user messages to one of three intents:
  • greeting
  • product_inquiry
  • high_intent_lead

Returns a dict: { "intent": str, "confidence": int, "reason": str }
"""

import logging
import re

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config import GROQ_API_KEY, LLM_MODEL, INTENT_GREETING, INTENT_INQUIRY, INTENT_HIGH_INTENT

logger = logging.getLogger("autostream.intent")

# ---------------------------------------------------------------------------
# Rule-based pre-filter (fast path)
# ---------------------------------------------------------------------------

_GREETING_PATTERNS = re.compile(
    r"^\s*(hi|hello|hey|howdy|what'?s\s*up|good\s*(morning|afternoon|evening)|yo|sup)\b",
    re.IGNORECASE,
)

_HIGH_INTENT_KEYWORDS = [
    "sign up", "signup", "subscribe", "buy", "purchase", "start",
    "get started", "interested", "ready to", "i want to join",
    "let's do it", "i'd like to", "i want the", "count me in",
    "take my money", "how do i pay", "i'll take", "enroll",
    "register", "onboard", "let's go", "i'm in", "demo",
    "trial", "free trial", "try it", "give it a shot",
]


def _rule_classify(message: str) -> dict | None:
    """
    Return a result dict if rules are confident, else None (fall through to LLM).
    """
    text = message.strip().lower()

    # Pure greeting (short message matching pattern)
    if _GREETING_PATTERNS.match(text) and len(text.split()) <= 5:
        logger.debug("Rule classifier → greeting")
        return {
            "intent": INTENT_GREETING,
            "confidence": 95,
            "reason": "Message matches a greeting pattern (hi/hello/hey etc.)"
        }

    # Strong buy-signal keywords
    for kw in _HIGH_INTENT_KEYWORDS:
        if kw in text:
            logger.debug("Rule classifier → high_intent_lead (keyword: %s)", kw)
            return {
                "intent": INTENT_HIGH_INTENT,
                "confidence": 93,
                "reason": f'User used high-intent keyword: "{kw}"'
            }

    return None  # uncertain → defer to LLM


# ---------------------------------------------------------------------------
# LLM classifier (fallback)
# ---------------------------------------------------------------------------

_CLASSIFY_SYSTEM_PROMPT = """\
You are an intent classifier for AutoStream, an automated video editing SaaS.
Given a user message, respond with EXACTLY one of these labels (nothing else):
  greeting
  product_inquiry
  high_intent_lead

Definitions:
• greeting — casual hello, small talk, or generic opener.
• product_inquiry — questions about features, pricing, plans, policies, support,
  comparisons, capabilities, or how AutoStream works.
• high_intent_lead — the user expresses clear intent to sign up, subscribe,
  purchase, start a trial, or otherwise convert into a paying customer.

Respond with the label ONLY, no explanation."""


# Friendly display names and reasons for each LLM-classified intent
_INTENT_META = {
    INTENT_GREETING: {
        "confidence": 88,
        "reason": "LLM classified message as a casual greeting or small talk"
    },
    INTENT_INQUIRY: {
        "confidence": 82,
        "reason": "LLM detected a question about features, pricing, or policies"
    },
    INTENT_HIGH_INTENT: {
        "confidence": 90,
        "reason": "LLM detected strong purchase or sign-up intent from the user"
    },
}


def classify_intent(message: str) -> dict:
    """
    Classify *message* into one of the three intent categories.

    Returns:
        {
            "intent":     str   — one of INTENT_GREETING / INTENT_INQUIRY / INTENT_HIGH_INTENT
            "confidence": int   — 0–100 confidence score
            "reason":     str   — human-readable explanation for the sidebar card
        }
    """

    # 1. Rule-based fast path (returns full dict already)
    rule_result = _rule_classify(message)
    if rule_result is not None:
        return rule_result

    # 2. LLM fallback
    try:
        llm = ChatGroq(
            model=LLM_MODEL,
            groq_api_key=GROQ_API_KEY,
            temperature=0.0,
        )
        response = llm.invoke([
            SystemMessage(content=_CLASSIFY_SYSTEM_PROMPT),
            HumanMessage(content=message),
        ])
        label = response.content.strip().lower().replace(" ", "_")

        # Validate label and return with metadata
        if label in _INTENT_META:
            logger.info("LLM classifier → %s", label)
            return {
                "intent": label,
                **_INTENT_META[label]
            }

        # Unexpected label — safe default
        logger.warning("LLM returned unexpected label '%s'; defaulting to product_inquiry", label)
        return {
            "intent": INTENT_INQUIRY,
            "confidence": 55,
            "reason": "Uncertain input — defaulted to product inquiry"
        }

    except Exception as exc:
        logger.error("Intent classification failed: %s — defaulting to product_inquiry", exc)
        return {
            "intent": INTENT_INQUIRY,
            "confidence": 40,
            "reason": f"Classification error — fallback applied"
        }
