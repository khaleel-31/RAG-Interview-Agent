from app.utils.models import get_model
from langchain_core.messages import SystemMessage

def interviewer_node(state):
    model = get_model()
    
    # Logic: Switch between Teaching and Interviewing
    if state.get("skill_gap"):
        system_content = f"You are a teacher. Explain these topics: {state['skill_gap']}. Then ask if they are ready for a question."
    else:
        system_content = f"You are a technical interviewer at {state['level']} level. Use this context: {state['tech_context']}. Ask ONE challenging question."

    messages = [SystemMessage(content=system_content)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}