<<<<<<< HEAD
# 🎬 AutoStream AI Agent

A **production-ready Conversational AI Agent** for **AutoStream** — an AI-powered automated video editing SaaS platform. Built with **LangChain**, **LangGraph**, and **Google Gemini** (`gemini-1.5-flash`).

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
├── intent_detection.py    # Hybrid rule + Gemini intent classifier
├── tools.py               # Validators + mock_lead_capture tool
├── agent_graph.py         # LangGraph stateful agent
├── main.py                # CLI chat interface
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.10+
- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### 2. Install Dependencies

```bash
cd autostream-agent
pip install -r requirements.txt
```

### 3. Set Your Gemini API Key

**PowerShell:**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Bash / Zsh:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows CMD:**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

> ⚠️ **Never hardcode your API key in source code.** Always use environment variables.

### 4. Run the Agent

**Interactive CLI Mode:**
```bash
python main.py
```

**Premium Web UI (Streamlit):**
```bash
streamlit run app.py
```

---

## 🧠 Architecture Deep Dive

### Intent Classification (Hybrid Approach)

The system uses a two-layer classification strategy:

1. **Rule Layer (Fast Path):** Regex patterns detect obvious greetings; keyword matching catches strong buy signals (e.g., "sign up", "subscribe", "get started"). This layer is instant and doesn't consume API calls.

2. **LLM Layer (Fallback):** When rules are uncertain, the message is sent to Gemini with a constrained prompt that returns exactly one of three labels: `greeting`, `product_inquiry`, or `high_intent_lead`.

This hybrid approach balances **speed** (rules handle ~60% of messages) with **accuracy** (LLM handles ambiguous cases).

### RAG Pipeline

```
JSON Knowledge Base → Document chunking → Gemini Embeddings → FAISS Vector Store → Retriever
```

- The knowledge base (`knowledge_base.json`) contains structured data about pricing, policies, and FAQs.
- Each logical section (plan, policy, FAQ) becomes a LangChain `Document` with metadata.
- Documents are embedded using Google's `embedding-001` model and stored in a FAISS index.
- At query time, the top-3 most relevant documents are retrieved and injected into the LLM prompt as context.
- The LLM is instructed to answer **only** from the provided context — no hallucination.

### LangGraph State Management

The agent uses a **typed state dictionary** (`AgentState`) that persists across turns:

```python
class AgentState(TypedDict):
    messages: list          # Full conversation history (append-only)
    intent: str             # Current classified intent
    mode: str               # "answering" or "lead_capture"
    lead_name: str          # Collected lead name
    lead_email: str         # Collected lead email
    lead_platform: str      # Collected lead platform
    collecting_field: str   # Current field being collected
    last_response: str      # Latest agent reply
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

## 💬 Example Conversation

```
You ▶ Hi there!
AutoStream ▶ Hello! 👋 Welcome to AutoStream — the AI-powered video editing
platform that helps creators edit faster and smarter. How can I help you today?

You ▶ What plans do you offer?
AutoStream ▶ We have two plans:
  • Basic ($29/month) — 10 videos, 720p, basic templates, email support
  • Pro ($79/month) — Unlimited videos, 4K, AI captions, 24/7 priority support

You ▶ What's the refund policy?
AutoStream ▶ Full refunds are available within 7 days of purchase. After that,
no refunds are issued, but you can cancel anytime and keep access until the end
of your billing period.

You ▶ I'd like to sign up for Pro!
AutoStream ▶ Awesome, I'm excited to get you started with AutoStream! 🎬
Could you share your full name so we can set things up for you?

You ▶ John Doe
AutoStream ▶ ✅ Got it! What's the best email address to reach you at?

You ▶ john@example.com
AutoStream ▶ ✅ Got it! Which creator platform do you primarily use?

You ▶ YouTube
AutoStream ▶ 🎉 Lead captured successfully!
  • Name:     John Doe
  • Email:    john@example.com
  • Platform: Youtube
A member of the AutoStream team will reach out within 24 hours.
```

---

## 🔌 Extending to WhatsApp

This agent can be deployed to WhatsApp with minimal changes using a webhook-based architecture:

### Architecture

```
WhatsApp User → WhatsApp Business API → Webhook (Flask/FastAPI) → AutoStreamAgent → Response → WhatsApp API → User
```

### Implementation Steps

1. **Set up WhatsApp Business API** via Meta's Cloud API or a provider like Twilio.

2. **Create a webhook server** (Flask/FastAPI):
   ```python
   from fastapi import FastAPI, Request
   from agent_graph import AutoStreamAgent

   app = FastAPI()
   sessions: dict[str, AutoStreamAgent] = {}

   @app.post("/webhook")
   async def webhook(request: Request):
       data = await request.json()
       phone = data["from"]
       message = data["text"]

       # Get or create session
       if phone not in sessions:
           sessions[phone] = AutoStreamAgent()

       reply = sessions[phone].chat(message)

       # Send reply via WhatsApp API
       await send_whatsapp_message(phone, reply)
       return {"status": "ok"}
   ```

3. **Session management:** Each phone number gets its own `AutoStreamAgent` instance, maintaining independent conversation state.

4. **Production considerations:**
   - Use Redis or a database for session persistence across restarts
   - Add rate limiting and message queuing
   - Implement webhook signature verification for security
   - Replace `mock_lead_capture()` with actual CRM API calls
   - Add media handling for video/image messages
   - Deploy behind a reverse proxy (nginx) with HTTPS

---

## 🛡️ Error Handling

- **Missing API key:** The agent exits gracefully with setup instructions.
- **LLM failures:** Intent classification falls back to `product_inquiry` if the LLM call fails.
- **Validation errors:** Users receive clear feedback and can retry.
- **Unexpected exceptions:** Caught at the chat loop level with friendly error messages and logging.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `langchain` | Core LangChain framework |
| `langchain-google-genai` | Google Gemini LLM + Embeddings |
| `langgraph` | Stateful agent graph |
| `faiss-cpu` | Local vector similarity search |
| `google-generativeai` | Google Generative AI SDK |

---

## 📄 License

This project is for educational and demonstration purposes.
=======
# Inflx---AutoStream
**Inflx** is an AI-powered lead generation chatbot built with Streamlit using intent detection, RAG, and automated lead capture. It answers user queries, detects buying intent, and converts conversations into qualified sales leads.
>>>>>>> f7dcc7c7621da087545916c8337799cb6437b9d8
