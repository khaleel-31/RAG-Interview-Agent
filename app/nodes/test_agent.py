import uuid
from app.graph import app
from langchain_core.messages import HumanMessage

# 1. Setup session config
config = {"configurable": {"thread_id": str(uuid.uuid4())}}

# 2. Define initial state
initial_state = {
    "messages": [HumanMessage(content="I want to start the interview for a Python Developer role.")],
    "level": "beginner",
    "score": 0,
    "tech_context": "",
    "skill_gap": []
}

print("--- 🚀 STARTING TEST ---")

# 3. Stream the graph execution
for event in app.stream(initial_state, config):
    for node_name, output in event.items():
        print(f"\n--- 🤖 Node: {node_name} ---")
        
        # Check if researcher found context
        if "tech_context" in output:
            print(f"Context Found: {output['tech_context'][:200]}...")
            
        # Print the last message if it's from the interviewer or evaluator
        if "messages" in output:
            print(f"Response: {output['messages'][-1].content}")

print("\n--- ✅ TEST COMPLETE ---")