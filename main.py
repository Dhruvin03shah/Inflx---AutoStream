"""
AutoStream AI Agent - CLI Chat Interface
Run this script to interact with the conversational agent in your terminal.

Usage:
    python main.py
"""

import sys
import logging

from config import GROQ_API_KEY
from agent_graph import AutoStreamAgent

logger = logging.getLogger("autostream.main")

# ── ANSI colors for pretty terminal output ────────────────────────────────
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


BANNER = f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      🎬  AutoStream AI Assistant  🎬                         ║
║      Your AI-powered video editing companion                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}

{DIM}Type your message and press Enter. Type 'quit' or 'exit' to leave.{RESET}
"""


def main():
    """Run the interactive CLI chat loop."""

    # -- Preflight check -----------------------------------------------------
    if not GROQ_API_KEY:
        print(f"\n{RED}❌  GROQ_API_KEY is not set!{RESET}")
        print(f"{YELLOW}Set it before running:{RESET}")
        print(f"  PowerShell:  $env:GROQ_API_KEY='your-key-here'")
        print(f"  Bash/Zsh:    export GROQ_API_KEY='your-key-here'")
        sys.exit(1)

    print(BANNER)

    # -- Initialize agent ----------------------------------------------------
    try:
        agent = AutoStreamAgent()
    except Exception as exc:
        logger.exception("Failed to initialize agent")
        print(f"{RED}❌  Agent initialization failed: {exc}{RESET}")
        sys.exit(1)

    # -- Chat loop -----------------------------------------------------------
    while True:
        try:
            user_input = input(f"\n{GREEN}{BOLD}You ▶ {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{CYAN}Goodbye! 👋{RESET}")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "bye", "q"}:
            print(f"\n{CYAN}Thanks for chatting with AutoStream! See you soon 🎬{RESET}")
            break

        try:
            reply = agent.chat(user_input)
            print(f"\n{CYAN}{BOLD}AutoStream ▶{RESET} {reply}")
        except Exception as exc:
            logger.exception("Error processing message")
            print(f"\n{RED}⚠️  Something went wrong: {exc}{RESET}")
            print(f"{DIM}Please try again or type 'quit' to exit.{RESET}")


if __name__ == "__main__":
    main()
