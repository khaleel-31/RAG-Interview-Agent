import uuid
from app.graph import app
from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "session_1"}}

def run_test():
    # START THE GRAPH
    print("--- 🚀 STARTING INTERVIEW ---")
    inputs = {"messages": [HumanMessage(content="Start")], "level": "beginner", "score": 0}
    
    # Run until the first interrupt (The first question)
    for event in app.stream(inputs, config):
        for node, values in event.items():
            if "messages" in values:
                print(f"\n🤖 {node.upper()}: {values['messages'][-1].content}")

    # THE LOOP: Mimic a real conversation
    while True:
        user_input = input("\n👤 YOU: ")
        if user_input.lower() in ["quit", "exit"]: break

        # Resume the graph with the user's answer
        for event in app.stream({"messages": [HumanMessage(content=user_input)]}, config):
            for node, values in event.items():
                if "messages" in values:
                    print(f"\n🤖 {node.upper()}: {values['messages'][-1].content}")

run_test()