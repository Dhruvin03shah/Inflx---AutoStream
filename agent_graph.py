"""
AutoStream AI Agent - LangGraph Agent
Stateful conversational agent built with LangGraph.

States
------
answering   – default state; handles greetings + RAG-powered inquiries
lead_capture – activated on high-intent; collects name → email → platform

The graph maintains full conversation memory and dynamically transitions
between states based on detected intent.
"""

import logging
from typing import TypedDict, Annotated, Literal
from operator import add

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config import (
    GROQ_API_KEY,
    LLM_MODEL,
    INTENT_GREETING,
    INTENT_INQUIRY,
    INTENT_HIGH_INTENT,
    LEAD_FIELDS,
    LEAD_FIELD_PROMPTS,
)
from intent_detection import classify_intent
from rag_pipeline import retrieve_context
from tools import FIELD_VALIDATORS, mock_lead_capture

logger = logging.getLogger("autostream.agent")


# ═══════════════════════════════════════════════════════════════════════════
# State schema
# ═══════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """Represents the full agent state across turns."""

    # Conversation history (append-only via reducer)
    messages: Annotated[list, add]

    # Current detected intent
    intent: str
    confidence: int
    reason: str

    # Agent mode: "answering" | "lead_capture"
    mode: str

    # Lead-capture fields
    lead_name: str
    lead_email: str
    lead_platform: str

    # Which field we are currently collecting (name / email / platform / done)
    collecting_field: str

    # Latest agent reply (for the CLI loop to display)
    last_response: str
    
    # Tool log for UI to display lead info
    tool_log: dict
    
    # Callback for real-time UI streaming
    stream_callback: any


# ═══════════════════════════════════════════════════════════════════════════
# Shared LLM instance factory
# ═══════════════════════════════════════════════════════════════════════════

def _get_llm(temperature: float = 0.4, callbacks=None) -> ChatGroq:
    return ChatGroq(
        model=LLM_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=temperature,
        streaming=bool(callbacks),
        callbacks=callbacks
    )


# ═══════════════════════════════════════════════════════════════════════════
# Node: classify intent
# ═══════════════════════════════════════════════════════════════════════════

def classify_node(state: AgentState) -> dict:
    """Classify the latest user message and decide whether to switch mode."""

    # Grab the last human message
    user_msg = ""
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break

    intent_data = classify_intent(user_msg)
    intent_val = intent_data["intent"]
    logger.info("Intent detected: %s", intent_val)

    updates: dict = {
        "intent": intent_val,
        "confidence": intent_data.get("confidence", 0),
        "reason": intent_data.get("reason", "")
    }

    # If already in lead_capture, stay there (don't reclassify mid-flow)
    if state.get("mode") == "lead_capture" and state.get("collecting_field") != "done":
        logger.debug("Already in lead_capture mode — keeping it.")
        return updates

    # Transition to lead_capture on high intent
    if intent_val == INTENT_HIGH_INTENT:
        updates["mode"] = "lead_capture"
        updates["collecting_field"] = "name"  # start from the first field
        logger.info("Switching to lead_capture mode")

    return updates


# ═══════════════════════════════════════════════════════════════════════════
# Node: handle answering (greetings + RAG inquiries)
# ═══════════════════════════════════════════════════════════════════════════

_ANSWERING_SYSTEM_PROMPT = """\
You are the friendly and knowledgeable AI assistant for **AutoStream**, an
AI-powered automated video editing platform.

Guidelines:
• Be warm, professional, and concise.
• For greetings, welcome the user and briefly mention what AutoStream does.
• For product / pricing questions, use ONLY the context provided below to
  answer. Do NOT make up features or prices.
• If the context does not contain the answer, say so honestly.
• Subtly encourage users to try AutoStream when appropriate.

{context_block}
"""


def answering_node(state: AgentState) -> dict:
    """Handle greeting or product inquiry using RAG-grounded generation."""

    user_msg = ""
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break

    intent = state.get("intent", INTENT_INQUIRY)

    # Build context block
    if intent == INTENT_GREETING:
        context_block = "Context: This is a greeting. No product lookup needed."
    else:
        raw_context = retrieve_context(user_msg)
        context_block = f"Context from knowledge base:\n\n{raw_context}"

    system_prompt = _ANSWERING_SYSTEM_PROMPT.format(context_block=context_block)

    # Build message history for the LLM (keep last 10 turns for efficiency)
    history = state["messages"][-20:]  # ~10 user + 10 assistant turns
    llm_messages = [SystemMessage(content=system_prompt)] + history

    cb = state.get("stream_callback")
    callbacks = [cb] if cb else None

    llm = _get_llm(callbacks=callbacks)
    response = llm.invoke(llm_messages)
    reply = response.content

    logger.debug("Answering node reply length: %d chars", len(reply))

    return {
        "messages": [AIMessage(content=reply)],
        "last_response": reply,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Node: handle lead capture
# ═══════════════════════════════════════════════════════════════════════════

def lead_capture_node(state: AgentState) -> dict:
    """Sequentially collect name → email → platform, validate, and finally
    call mock_lead_capture only when all three fields are present."""

    collecting = state.get("collecting_field", "name")
    updates: dict = {}

    # --- First entry into lead capture (no field collected yet) ------------
    agent_msgs = [m.content for m in state["messages"] if isinstance(m, AIMessage)]
    last_agent_msg = agent_msgs[-1] if agent_msgs else ""
    
    if not state.get("lead_name") and collecting == "name":
        # Check if this is the very first time (we haven't prompted yet)
        if LEAD_FIELD_PROMPTS['name'] not in last_agent_msg and "⚠️" not in last_agent_msg:
            reply = (
                "Awesome, I'm excited to get you started with Inflx! 🎬\n\n"
                f"{LEAD_FIELD_PROMPTS['name']}"
            )
            return {
                "messages": [AIMessage(content=reply)],
                "last_response": reply,
            }

    # --- Collect current field from the latest user message ----------------
    user_msg = ""
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break

    # Determine which field we're validating
    field = collecting
    validator = FIELD_VALIDATORS.get(field)

    if validator:
        is_valid, result = validator(user_msg)

        if not is_valid:
            # Validation failed — ask again
            reply = f"⚠️ {result}\n\nPlease try again:"
            return {
                "messages": [AIMessage(content=reply)],
                "last_response": reply,
            }

        # Store the validated value
        field_key = f"lead_{field}"
        updates[field_key] = result

        # Advance to next field
        current_idx = LEAD_FIELDS.index(field)
        if current_idx + 1 < len(LEAD_FIELDS):
            next_field = LEAD_FIELDS[current_idx + 1]
            updates["collecting_field"] = next_field
            reply = f"✅ Got it! {LEAD_FIELD_PROMPTS[next_field]}"
            updates["messages"] = [AIMessage(content=reply)]
            updates["last_response"] = reply
            return updates
        else:
            # All fields collected — call the tool!
            updates["collecting_field"] = "done"
            name = updates.get("lead_name") or state.get("lead_name", "")
            email = updates.get("lead_email") or state.get("lead_email", "")
            platform = result  # this is the last field

            capture_result = mock_lead_capture(name, email, platform)

            reply = (
                f"🎉 {capture_result['message']}\n\n"
                "Is there anything else you'd like to know about AutoStream?"
            )
            updates["messages"] = [AIMessage(content=reply)]
            updates["last_response"] = reply
            updates["mode"] = "answering"  # reset mode after capture
            updates["tool_log"] = capture_result
            return updates

    # Fallback (shouldn't reach here)
    reply = "Something went wrong in the lead capture flow. Let me start over — what's your name?"
    updates["collecting_field"] = "name"
    updates["messages"] = [AIMessage(content=reply)]
    updates["last_response"] = reply
    return updates


# ═══════════════════════════════════════════════════════════════════════════
# Router: decide which node to visit after classification
# ═══════════════════════════════════════════════════════════════════════════

def route_after_classify(state: AgentState) -> Literal["answering_node", "lead_capture_node"]:
    """Conditional edge: route to the appropriate handler node."""
    if state.get("mode") == "lead_capture":
        return "lead_capture_node"
    return "answering_node"


# ═══════════════════════════════════════════════════════════════════════════
# Build the graph
# ═══════════════════════════════════════════════════════════════════════════

def build_agent_graph() -> StateGraph:
    """Construct and compile the LangGraph agent."""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify_node", classify_node)
    graph.add_node("answering_node", answering_node)
    graph.add_node("lead_capture_node", lead_capture_node)

    # Entry point
    graph.set_entry_point("classify_node")

    # Conditional routing from classifier
    graph.add_conditional_edges(
        "classify_node",
        route_after_classify,
        {
            "answering_node": "answering_node",
            "lead_capture_node": "lead_capture_node",
        },
    )

    # Terminal edges
    graph.add_edge("answering_node", END)
    graph.add_edge("lead_capture_node", END)

    compiled = graph.compile()
    logger.info("Agent graph compiled successfully")
    return compiled


# ═══════════════════════════════════════════════════════════════════════════
# High-level run helper
# ═══════════════════════════════════════════════════════════════════════════

class AutoStreamAgent:
    """Wrapper that maintains persistent state across invocations."""

    def __init__(self):
        self.graph = build_agent_graph()
        self.state: AgentState = {
            "messages": [],
            "intent": "",
            "confidence": 0,
            "reason": "",
            "mode": "answering",
            "lead_name": "",
            "lead_email": "",
            "lead_platform": "",
            "collecting_field": "",
            "last_response": "",
            "tool_log": {},
            "stream_callback": None,
        }
        logger.info("AutoStreamAgent initialized")

    def chat(self, user_message: str, stream_callback=None) -> str:
        """Process a single user message and return the agent's reply."""

        # Append user message to state
        self.state["messages"] = self.state["messages"] + [HumanMessage(content=user_message)]
        if stream_callback:
            self.state["stream_callback"] = stream_callback

        # Run the graph
        result = self.graph.invoke(self.state)
        
        if "stream_callback" in self.state:
            del self.state["stream_callback"]

        # Merge result back into persistent state
        self.state["messages"] = result.get("messages", self.state["messages"])
        self.state["intent"] = result.get("intent", self.state["intent"])
        self.state["confidence"] = result.get("confidence", self.state.get("confidence", 0))
        self.state["reason"] = result.get("reason", self.state.get("reason", ""))
        self.state["mode"] = result.get("mode", self.state["mode"])
        self.state["lead_name"] = result.get("lead_name", self.state["lead_name"])
        self.state["lead_email"] = result.get("lead_email", self.state["lead_email"])
        self.state["lead_platform"] = result.get("lead_platform", self.state["lead_platform"])
        self.state["collecting_field"] = result.get("collecting_field", self.state["collecting_field"])
        self.state["last_response"] = result.get("last_response", self.state["last_response"])
        self.state["tool_log"] = result.get("tool_log", self.state.get("tool_log", {}))

        return self.state["last_response"]
