import re
from datetime import datetime
from typing import Tuple

import streamlit as st

# ── Must be the very first Streamlit call ─────────────────────────────────────
st.set_page_config(
    page_title="AutoStream · AI Lead Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════
KNOWLEDGE_BASE = {
    "plans": {
        "basic": {
            "name": "Basic Plan",
            "price": "$29/month",
            "features": ["10 videos/month", "720p resolution", "Standard support"],
        },
        "pro": {
            "name": "Pro Plan",
            "price": "$79/month",
            "features": [
                "Unlimited videos",
                "4K resolution",
                "AI captions",
                "24/7 priority support",
            ],
        },
    },
    "policies": [
        "No refunds after 7 days of purchase.",
        "24/7 live support is exclusively available on the Pro plan.",
        "Annual billing saves 20% compared to monthly pricing.",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  CSS  — Cinematic Dark / Video-Suite Aesthetic
# ══════════════════════════════════════════════════════════════════════════════
def inject_css() -> None:
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
:root {
  --bg:        #07070D;
  --surface:   #0E0E18;
  --card:      #141420;
  --card2:     #1C1C2C;
  --border:    #25253A;
  --border2:   #35355A;
  --accent:    #FF6B35;
  --accent2:   #FF9A6C;
  --cyan:      #00D9FF;
  --green:     #22C55E;
  --txt:       #E8E8F8;
  --txt2:      #9999BB;
  --txt3:      #55556A;
  --glow:      0 0 20px rgba(255,107,53,0.35);
  --radius:    14px;
  --radius-sm: 8px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--txt) !important;
  font-family: 'Outfit', sans-serif !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
footer { display: none !important; }

[data-testid="stMain"] > div { padding-top: 0 !important; }
[data-testid="block-container"] {
  padding: 0 1.5rem 2rem !important;
  max-width: 100% !important;
}
[data-testid="column"] { padding: 0 0.5rem !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Top Nav */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.5rem; margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  background: rgba(14,14,24,0.9);
  backdrop-filter: blur(16px);
  position: sticky; top: 0; z-index: 100;
}
.topbar-logo {
  font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.35rem;
  color: var(--txt); text-transform: uppercase; letter-spacing: 0.06em;
}
.topbar-logo span { color: var(--accent); }
.topbar-badge {
  display: flex; align-items: center; gap: 8px;
  background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3);
  border-radius: 99px; padding: 4px 14px;
  font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;
  color: var(--green);
}
.pulse-dot {
  width: 7px; height: 7px; border-radius: 50%; background: var(--green);
  box-shadow: 0 0 8px var(--green); animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:0.45; transform:scale(0.65); }
}

.glow-line {
  height: 2px; border-radius: 99px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  margin-bottom: 1.5rem; opacity: 0.55;
}

.section-label {
  font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--txt3); margin-bottom: 0.7rem;
}

/* Metric grid */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 1rem; }
.metric-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 12px 14px;
}
.metric-val {
  font-family: 'Syne', sans-serif; font-weight: 800;
  font-size: 1.55rem; color: var(--txt);
}
.metric-lbl {
  font-size: 0.68rem; color: var(--txt3);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px;
}

/* Intent panel */
.intent-panel {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.2rem; margin-bottom: 1rem;
}
.intent-label {
  font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--txt3); margin-bottom: 0.6rem;
}
.intent-tag {
  display: inline-flex; align-items: center; gap: 8px;
  border-radius: 99px; padding: 6px 18px;
  font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.88rem;
}
.intent-greeting { background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.4); color:#C084FC; }
.intent-inquiry  { background:rgba(0,217,255,0.1);   border:1px solid rgba(0,217,255,0.3);  color:var(--cyan); }
.intent-high     { background:rgba(255,107,53,0.15); border:1px solid rgba(255,107,53,0.5); color:var(--accent2); box-shadow:var(--glow); }
.intent-neutral  { background:rgba(85,85,106,0.12);  border:1px solid var(--border2);       color:var(--txt2); }

.conf-bar-wrap { margin-top: 0.8rem; }
.conf-bar-label {
  display: flex; justify-content: space-between; margin-bottom: 4px;
  font-size: 0.7rem; color: var(--txt2); font-family: 'JetBrains Mono', monospace;
}
.conf-bar-track { background: var(--card2); border-radius: 99px; height: 5px; overflow: hidden; }
.conf-bar-fill  { height: 100%; border-radius: 99px; }

/* Pipeline panel */
.pipeline-panel {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.2rem; margin-bottom: 1rem;
}
.pipeline-steps { display: flex; flex-direction: column; gap: 9px; margin-top: 0.7rem; }
.pipeline-step {
  display: flex; align-items: center; gap: 12px;
  padding: 9px 13px; border-radius: var(--radius-sm); font-size: 0.82rem;
}
.step-done    { background:rgba(34,197,94,0.09);  border:1px solid rgba(34,197,94,0.25);  color:#86EFAC; }
.step-active  { background:rgba(255,107,53,0.09); border:1px solid rgba(255,107,53,0.4);  color:var(--accent2); }
.step-pending { background:var(--card2); border:1px solid var(--border); color:var(--txt3); }
.step-icon { width: 20px; text-align: center; }

/* Knowledge base */
.kb-panel {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.2rem; margin-bottom: 1rem;
}
.plan-card {
  background: var(--card2); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 13px; margin-bottom: 9px;
}
.plan-name  { font-family:'Syne',sans-serif; font-weight:700; font-size:0.92rem; margin-bottom:3px; }
.plan-price { font-family:'JetBrains Mono',monospace; font-size:1.05rem; color:var(--accent); margin-bottom:7px; }
.plan-feat  { font-size:0.77rem; color:var(--txt2); margin-bottom:3px; padding-left:12px; position:relative; }
.plan-feat::before { content:'▸'; color:var(--accent); position:absolute; left:0; }

/* Chat box — fully self-contained HTML block */
.chat-box {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; margin-bottom: 0.75rem;
}
.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.9rem 1.2rem; border-bottom: 1px solid var(--border);
  background: var(--card2);
}
.chat-title {
  font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.97rem;
  display: flex; align-items: center; gap: 8px; color: var(--txt);
}
.chat-title-sub { font-weight: 400; color: var(--txt2); font-size: 0.78rem; }
.agent-dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--green);
  box-shadow: 0 0 10px var(--green); animation: pulse 1.8s ease-in-out infinite;
  flex-shrink: 0;
}

/* Messages */
.msg-list {
  padding: 1.1rem; display: flex; flex-direction: column; gap: 13px;
  min-height: 320px; max-height: 420px; overflow-y: auto;
}
.msg-row       { display: flex; gap: 10px; align-items: flex-end; }
.msg-row.user  { flex-direction: row-reverse; }
.msg-col {
  max-width: 82%; display: flex; flex-direction: column;
}
.msg-row.user .msg-col { align-items: flex-end; }
.msg-row:not(.user) .msg-col { align-items: flex-start; }

.avatar {
  width: 31px; height: 31px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; font-family: 'Syne', sans-serif;
}
.avatar.agent { background: var(--accent); color: #fff; }
.avatar.user  { background: var(--card2); border: 1px solid var(--border2); color: var(--txt2); }
.bubble {
  padding: 9px 13px;
  font-size: 0.865rem; line-height: 1.56; border-radius: 13px;
}
.bubble.agent {
  background: var(--card2); border: 1px solid var(--border);
  color: var(--txt); border-bottom-left-radius: 3px;
}
.bubble.user {
  background: linear-gradient(135deg, rgba(255,107,53,0.22), rgba(255,107,53,0.08));
  border: 1px solid rgba(255,107,53,0.38);
  color: var(--txt); border-bottom-right-radius: 3px;
}
.bubble.system {
  background: rgba(0,217,255,0.05); border: 1px dashed rgba(0,217,255,0.2);
  color: var(--cyan); font-family: 'JetBrains Mono', monospace; font-size: 0.73rem;
  border-radius: 8px; padding: 7px 11px; max-width: 100%;
}
.msg-time { font-size: 0.62rem; color: var(--txt3); margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

/* Input */
div[data-testid="stTextInput"] input {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 99px !important;
  color: var(--txt) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.88rem !important;
  padding: 0.6rem 1.2rem !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(255,107,53,0.14) !important;
  outline: none !important;
}
div[data-testid="stTextInput"] input::placeholder { color: var(--txt3) !important; }
div[data-testid="stTextInput"] label { display: none !important; }

/* Primary buttons */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, var(--accent), #E05A18) !important;
  color: #fff !important; border: none !important;
  border-radius: 99px !important; font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important; font-size: 0.83rem !important;
  letter-spacing: 0.04em !important; padding: 0.5rem 1.3rem !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 14px rgba(255,107,53,0.28) !important;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 7px 20px rgba(255,107,53,0.42) !important;
}

/* Chip buttons — override the orange */
.chip-btn div[data-testid="stButton"] > button {
  background: var(--card2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--txt2) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 400 !important;
  font-size: 0.77rem !important;
  padding: 3px 10px !important;
  box-shadow: none !important;
}
.chip-btn div[data-testid="stButton"] > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Lead success */
.lead-success {
  background: linear-gradient(135deg, rgba(34,197,94,0.1), rgba(34,197,94,0.04));
  border: 1px solid rgba(34,197,94,0.32);
  border-radius: var(--radius); padding: 1.2rem; margin-bottom: 1rem;
}
.lead-success-title {
  font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1rem;
  color: var(--green); margin-bottom: 8px;
}
.lead-detail {
  font-size: 0.79rem; color: var(--txt2); line-height: 1.75;
  font-family: 'JetBrains Mono', monospace;
}

/* Tool log */
.tool-log {
  background: rgba(34,197,94,0.05); border: 1px solid rgba(34,197,94,0.18);
  border-radius: var(--radius-sm); padding: 11px 15px; margin-bottom: 1rem;
  font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--green);
  line-height: 1.6;
}
.tool-log-title { font-weight: 600; margin-bottom: 5px; letter-spacing: 0.04em; }

/* Footer */
.footer-block {
  margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);
  text-align: center; font-size: 0.66rem; color: var(--txt3);
  font-family: 'JetBrains Mono', monospace; line-height: 1.9;
}
.footer-block span { color: var(--accent); }

/* Hide Streamlit chrome */
#MainMenu, .stDeployButton { display: none !important; }
[data-testid="stVerticalBlock"] > * + * { margin-top: 0 !important; }
</style>
""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_state() -> None:
    from agent_graph import AutoStreamAgent
    if "agent" not in st.session_state:
        st.session_state["agent"] = AutoStreamAgent()

    defaults = {
        "messages":         [],
        "intent":           "neutral",
        "confidence":       0,
        "reason":           "",
        "stage":            0,      # 0=greeting 1=inquiry 2=high_intent 3=collecting 4=captured
        "turn_count":       0,
        "msgs_sent":        0,
        "tool_log":         None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
#  MOCK LEAD CAPTURE TOOL
# ══════════════════════════════════════════════════════════════════════════════



# ══════════════════════════════════════════════════════════════════════════════
#  RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _md_to_html(text: str) -> str:
    """Convert **bold** and `code` markdown to safe inline HTML."""
    out = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    out = re.sub(
        r"`(.*?)`",
        r"<code style='background:rgba(255,255,255,0.08);padding:1px 5px;"
        r"border-radius:4px;font-family:JetBrains Mono,monospace;font-size:0.85em'>\1</code>",
        out,
    )
    out = out.replace("\n", "<br>")
    return out


def render_chat_box() -> None:
    """Render full chat box in ONE self-contained st.markdown call (fixes broken div issue)."""
    msgs      = st.session_state["messages"]
    rows_html = ""

    for m in msgs:
        role = m["role"]
        ts   = m["ts"]
        text = _md_to_html(m["text"])

        if role == "system":
            rows_html += f'<div class="bubble system">{text}</div>'
            continue

        avatar_lbl   = "AS" if role == "agent" else "You"
        row_extra    = " user" if role == "user" else ""
        bubble_class = "agent" if role == "agent" else "user"

        rows_html += (
            f'<div class="msg-row{row_extra}">'
            f'<div class="avatar {bubble_class}">{avatar_lbl}</div>'
            f'<div class="msg-col">'
            f'<div class="bubble {bubble_class}">{text}</div>'
            f'<div class="msg-time">{ts}</div>'
            f"</div></div>"
        )

    return f"""
<div class="chat-box">
  <div class="chat-header">
    <div class="chat-title">
      <div class="agent-dot"></div>
      Inflx Agent
      <span class="chat-title-sub">&nbsp;·&nbsp; RAG + Intent Detection</span>
    </div>
    <span style="font-size:0.68rem;color:var(--txt3);font-family:'JetBrains Mono',monospace;">v1.0.0</span>
  </div>
  <div class="msg-list" id="msg-list">{rows_html}</div>
</div>
<img src="empty" onerror="var el = document.getElementById('msg-list'); if (el) el.scrollTop = el.scrollHeight;" style="display:none;">
"""


def render_intent_panel() -> None:
    ss = st.session_state
    intent = ss.get("intent", "neutral")
    conf = ss.get("confidence", 0)
    reason = ss.get("reason", "Waiting...")
    
    intent_map = {
        "greeting":    ("💬", "Casual Greeting",  "intent-greeting", "#C084FC"),
        "product_inquiry": ("🔍", "Product Inquiry", "intent-inquiry", "#00D9FF"),
        "high_intent_lead": ("🔥", "High Intent Lead", "intent-high", "#FF9A6C"),
        "neutral":     ("⚪", "Awaiting Input",    "intent-neutral",  "#55556A"),
    }
    icon, label, css, color = intent_map.get(intent, intent_map["neutral"])

    st.markdown(
        f"""
<div class="intent-panel">
  <div class="intent-label">&#9658; LIVE INTENT DETECTION CARD</div>
  <div style="background: var(--card2); padding: 12px; border-radius: 8px; border: 1px solid var(--border); font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; line-height: 1.6; color: var(--txt);">
    <span style="color: var(--txt2);">Detected Intent:</span> <span style="color: {color}; font-weight: 600;">{label}</span><br>
    <span style="color: var(--txt2);">Confidence:</span> <span style="color: {color};">{conf}%</span><br>
    <span style="color: var(--txt2);">Reason:</span> {reason if reason else "Waiting..."}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_pipeline() -> None:
    stage = st.session_state["stage"]

    def cls(i: int) -> str:
        if stage > i:  return "step-done"
        if stage == i: return "step-active"
        return "step-pending"

    steps = [
        ("👋", "Greeting",           0),
        ("🔍", "Product Inquiry",    1),
        ("🔥", "High Intent Signal", 2),
        ("📋", "Lead Collection",    3),
        ("✅", "Lead Captured",      4),
    ]
    rows = "".join(
        f'<div class="pipeline-step {cls(i)}">'
        f'<span class="step-icon">{icon}</span>{label}</div>'
        for icon, label, i in steps
    )
    st.markdown(
        f"""
<div class="pipeline-panel">
  <div class="section-label">&#9658; LEAD PIPELINE</div>
  <div class="pipeline-steps">{rows}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kb() -> None:
    kb   = KNOWLEDGE_BASE
    b, p = kb["plans"]["basic"], kb["plans"]["pro"]

    def feats(lst: list) -> str:
        return "".join(f'<div class="plan-feat">{f}</div>' for f in lst)

    st.markdown(
        f"""
<div class="kb-panel">
  <div class="section-label">&#9658; KNOWLEDGE BASE (RAG)</div>
  <div class="plan-card">
    <div class="plan-name">&#127919; {b['name']}</div>
    <div class="plan-price">{b['price']}</div>
    {feats(b['features'])}
  </div>
  <div class="plan-card">
    <div class="plan-name">&#128640; {p['name']}</div>
    <div class="plan-price">{p['price']}</div>
    {feats(p['features'])}
  </div>
  <div style="font-size:0.73rem;color:var(--txt3);margin-top:8px;
              font-family:'JetBrains Mono',monospace;line-height:1.7;">
    &#128203; No refunds after 7 days<br>
    &#128172; 24/7 support &#8212; Pro plan only
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_lead_success() -> None:
    ss = st.session_state
    if ss["stage"] < 4 or not ss["tool_log"]:
        return
    r = ss["tool_log"]
    st.markdown(
        f"""
<div class="lead-success">
  <div class="lead-success-title">&#127881; Lead Captured Successfully!</div>
  <div class="lead-detail">
    ID &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#8594; {r['lead_id']}<br>
    Name &nbsp;&nbsp;&nbsp;&#8594; {r['name']}<br>
    Email &nbsp;&nbsp;&#8594; {r['email']}<br>
    Platform&#8594; {r['platform']}<br>
    Time &nbsp;&nbsp;&nbsp;&#8594; {r['captured_at']}<br>
    Owner &nbsp;&nbsp;&#8594; {r['assigned_to']}
  </div>
</div>
<div class="tool-log">
  <div class="tool-log-title">&#9881; mock_lead_capture() &#8594; executed</div>
  name="{r['name']}" &nbsp;email="{r['email']}" &nbsp;platform="{r['platform']}"<br>
  &#8594; status="{r['status']}" &nbsp;lead_id="{r['lead_id']}"
</div>
""",
        unsafe_allow_html=True,
    )


def render_metrics() -> None:
    ss  = st.session_state
    stage_labels = {0: "Greeting", 1: "Inquiry", 2: "Intent", 3: "Collecting", 4: "Captured"}
    lbl = stage_labels.get(ss["stage"], "-")
    st.markdown(
        f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-val">{ss['turn_count']}</div>
    <div class="metric-lbl">Turns</div>
  </div>
  <div class="metric-card">
    <div class="metric-val" style="font-size:1.05rem;padding-top:6px;">{lbl}</div>
    <div class="metric-lbl">Stage</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    init_state()
    inject_css()
    ss = st.session_state

    # Top Bar
    st.markdown(
        """
<div class="topbar">
  <div class="topbar-logo">Auto<span>Stream</span> &nbsp;&middot;&nbsp; AI Lead Agent</div>
  <div class="topbar-badge"><div class="pulse-dot"></div>AGENT ONLINE</div>
</div>
<div class="glow-line"></div>
""",
        unsafe_allow_html=True,
    )

    # Welcome message — added once
    if not ss["messages"]:
        ss["messages"].append({
            "role": "agent",
            "text": (
                "👋 Hey! I'm the AutoStream AI Agent.\n\n"
                "I can answer questions about our **pricing plans**, **features**, "
                "and **policies** — and when you're ready, help you sign up in seconds.\n\n"
                "What brings you here today?"
            ),
            "ts": datetime.now().strftime("%H:%M"),
        })

    # Process pending quick reply (set by button click, consumed here)

    # Two-column layout
    left, right = st.columns([2, 1], gap="medium")

    # ── LEFT: Chat ──────────────────────────────────────────────────────────
    with left:
        import time
        chat_placeholder = st.empty()
        chat_placeholder.markdown(render_chat_box(), unsafe_allow_html=True)

        # Input form
        with st.form("chat_form", clear_on_submit=True):
            c_inp, c_btn = st.columns([5, 1])
            with c_inp:
                user_input = st.text_input(
                    "msg",
                    placeholder="Ask about pricing, features, or say 'I want to sign up'…",
                    label_visibility="collapsed",
                )
            with c_btn:
                submitted = st.form_submit_button("Send ↗", use_container_width=True)

        if submitted and user_input.strip():
            ts = datetime.now().strftime("%H:%M")
            ss["messages"].append({"role": "user",  "text": user_input.strip(), "ts": ts})
            ss["msgs_sent"] += 1
            ss["turn_count"] += 1
            
            # Create an empty agent message first so the callback can fill it in
            ss["messages"].append({"role": "agent", "text": "", "ts": datetime.now().strftime("%H:%M")})
            chat_placeholder.markdown(render_chat_box(), unsafe_allow_html=True)
            
            from langchain_core.callbacks.base import BaseCallbackHandler
            class StreamlitChatCallback(BaseCallbackHandler):
                def __init__(self, placeholder, render_func, session_state):
                    self.placeholder = placeholder
                    self.render_func = render_func
                    self.ss = session_state
                def on_llm_new_token(self, token: str, **kwargs) -> None:
                    self.ss["messages"][-1]["text"] += token
                    self.placeholder.markdown(self.render_func(), unsafe_allow_html=True)

            callback = StreamlitChatCallback(chat_placeholder, render_chat_box, ss)
            
            response = ss["agent"].chat(user_input.strip(), stream_callback=callback)
            
            # Ensure final text is set (in case of lead capture node which doesn't stream)
            ss["messages"][-1]["text"] = response
            chat_placeholder.markdown(render_chat_box(), unsafe_allow_html=True)
            
            # Map agent state to UI state
            agent_state = ss["agent"].state
            ss["intent"] = agent_state.get("intent", "neutral")
            ss["confidence"] = agent_state.get("confidence", 0)
            ss["reason"] = agent_state.get("reason", "")
            
            mode = agent_state.get("mode")
            field = agent_state.get("collecting_field")
            if ss["intent"] == "greeting" and mode != "lead_capture":
                ss["stage"] = 0
            elif ss["intent"] == "product_inquiry" and mode != "lead_capture":
                ss["stage"] = 1
            elif ss["intent"] == "high_intent_lead" and mode != "lead_capture":
                ss["stage"] = 2
            elif mode == "lead_capture" and field != "done":
                ss["stage"] = 3
            elif field == "done":
                ss["stage"] = 4
                
            if agent_state.get("tool_log"):
                ss["tool_log"] = agent_state["tool_log"]
                
            st.rerun()

    # ── RIGHT: Context Panel ────────────────────────────────────────────────
    with right:
        render_metrics()
        render_intent_panel()
        render_pipeline()

        if ss["stage"] == 4:
            render_lead_success()
        else:
            render_kb()

        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
        if st.button("🔄  Reset Conversation", use_container_width=True):
            for k in list(ss.keys()):
                del st.session_state[k]
            st.rerun()

        st.markdown(
            """
<div class="footer-block">
  AutoStream &middot; Inflx AI Agent<br>
  ServiceHive ML Intern Assignment<br>
  <span>Streamlit + RAG + LangGraph</span>
</div>
""",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()