# Inflx · AutoStream AI Agent

**Inflx** is an AI-powered lead generation chatbot built with Streamlit using intent detection, RAG, and automated lead capture. It answers user queries, detects buying intent, and converts conversations into qualified sales leads.

A **production-ready Conversational AI Agent** for **AutoStream** — an AI-powered automated video editing SaaS platform. Built with **LangChain**, **LangGraph**, and **Groq LLMs**.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Intent Classification** | Hybrid rule + LLM classifier (greeting / product inquiry / high-intent lead) |
| **RAG Pipeline** | FAISS vector store over a local JSON knowledge base for grounded answers |
| **Stateful Conversations** | LangGraph maintains memory across turns with typed state schema |
| **Lead Capture Flow** | Sequential collection of name → email → platform with validation |
| **Mock CRM Integration** | `mock_lead_capture()` simulates posting leads to a CRM |
| **Clean Architecture** | Modular files: config, RAG, intent, tools, agent graph, main |

---

## 📁 Project Structure

```
autostream-agent/
├── config.py              # API keys, model settings, constants
├── knowledge_base.json    # Product pricing, policies, and FAQs
├── rag_pipeline.py        # FAISS vector store + retriever
├── intent_detection.py    # Hybrid rule + LLM intent classifier
├── tools.py               # Validators + mock_lead_capture tool
├── agent_graph.py         # LangGraph stateful agent
├── main.py                # CLI chat interface
├── app.py                 # Streamlit UI
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.10+
- A Groq API key (configured via environment variables or `.env`)

### 2. Install Dependencies

```bash
cd autostream-agent
pip install -r requirements.txt
```

### 3. Set Your Groq API Key

Create a `.env` file in the root directory and add:
```
GROQ_API_KEY="your-api-key-here"
```

### 4. Run the Agent

**Premium Web UI (Streamlit):**
```bash
streamlit run app.py
```

---

## 🧠 Architecture Deep Dive

### Intent Classification (Hybrid Approach)

The system uses a two-layer classification strategy:

1. **Rule Layer (Fast Path):** Regex patterns detect obvious greetings; keyword matching catches strong buy signals (e.g., "sign up", "subscribe", "get started"). This layer is instant and doesn't consume API calls.

2. **LLM Layer (Fallback):** When rules are uncertain, the message is sent to the LLM with a constrained prompt that returns exactly one of three labels: `greeting`, `product_inquiry`, or `high_intent_lead`.

This hybrid approach balances **speed** (rules handle ~60% of messages) with **accuracy** (LLM handles ambiguous cases).

### RAG Pipeline

```
JSON Knowledge Base → Document chunking → Embeddings → FAISS Vector Store → Retriever
```

- The knowledge base (`knowledge_base.json`) contains structured data about pricing, policies, and FAQs.
- Each logical section (plan, policy, FAQ) becomes a LangChain `Document` with metadata.
- Documents are embedded and stored in a FAISS index.
- At query time, the top-3 most relevant documents are retrieved and injected into the LLM prompt as context.
- The LLM is instructed to answer **only** from the provided context — no hallucination.

### LangGraph State Management

The agent uses a **typed state dictionary** (`AgentState`) that persists across turns:

```python
class AgentState(TypedDict):
    messages: list          # Full conversation history (append-only)
    intent: str             # Current classified intent
    confidence: int         # Confidence score of the intent
    reason: str             # Reason for the intent
    mode: str               # "answering" or "lead_capture"
    lead_name: str          # Collected lead name
    lead_email: str         # Collected lead email
    lead_platform: str      # Collected lead platform
    collecting_field: str   # Current field being collected
    last_response: str      # Latest agent reply
    tool_log: dict          # Captured lead payload
```

**Graph Flow:**

```
┌────────────┐
│   START    │
└─────┬──────┘
      │
      ▼
┌────────────────┐       ┌──────────────────┐
│ classify_node  │──────▶│  answering_node  │──▶ END
│ (intent detect)│       │  (greeting/RAG)  │
└────────┬───────┘       └──────────────────┘
         │
         │ (high intent)
         ▼
┌──────────────────────┐
│  lead_capture_node   │──▶ END
│  (sequential fields) │
└──────────────────────┘
```

- **`classify_node`:** Detects intent. If already in lead capture, skips reclassification.
- **`answering_node`:** Handles greetings (warm welcome) and inquiries (RAG-grounded answers).
- **`lead_capture_node`:** Sequentially collects name → email → platform. Validates each field. Only calls `mock_lead_capture()` after all three are collected.

### Lead Capture Flow

The lead capture is designed to be **sequential and validated**:

1. User expresses high intent → agent switches to `lead_capture` mode
2. Agent asks for **name** → validates (alphabetic, ≥2 chars)
3. Agent asks for **email** → validates (regex email pattern)
4. Agent asks for **platform** → validates (against known platforms list)
5. Only after all three are valid → `mock_lead_capture(name, email, platform)` is called
6. Agent confirms capture and returns to `answering` mode

**No premature execution:** The tool function is never called until all fields pass validation.

---

## 🛡️ Error Handling

- **Missing API key:** The agent logs a warning.
- **LLM failures:** Intent classification falls back to `product_inquiry` if the LLM call fails.
- **Validation errors:** Users receive clear feedback and can retry.
- **Unexpected exceptions:** Caught at the chat loop level with friendly error messages and logging.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `langchain` | Core LangChain framework |
| `langchain-groq` | Groq LLM |
| `langgraph` | Stateful agent graph |
| `faiss-cpu` | Local vector similarity search |
| `streamlit` | UI Web framework |

---

## 📄 License

This project is for educational and demonstration purposes.
