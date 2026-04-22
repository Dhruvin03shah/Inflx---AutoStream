import os
# Ensure GROQ_API_KEY is set in your environment before running this script
# os.environ["GROQ_API_KEY"] = "your-api-key"

from agent_graph import AutoStreamAgent

print("Initializing Agent...")
agent = AutoStreamAgent()

print("--- Test 1: Greeting ---")
print("Agent:", agent.chat("Hi there!"))

print("\n--- Test 2: RAG Q&A ---")
print("Agent:", agent.chat("What are your plans and pricing?"))

print("\n--- Test 3: RAG Q&A 2 ---")
print("Agent:", agent.chat("Do you have a refund policy?"))

print("\n--- Test 4: High Intent Trigger ---")
print("Agent:", agent.chat("I'm ready to buy the Pro plan."))

print("\n--- Test 5: Collecting Name ---")
print("Agent:", agent.chat("John Doe"))

print("\n--- Test 6: Collecting Email ---")
print("Agent:", agent.chat("john.doe@example.com"))

print("\n--- Test 7: Collecting Platform ---")
print("Agent:", agent.chat("YouTube"))

print("\n--- Test 8: Back to Answering ---")
print("Agent:", agent.chat("What video formats do you support?"))
