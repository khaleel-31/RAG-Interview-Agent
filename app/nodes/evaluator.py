from app.utils.models import get_model

def evaluator_node(state):
    # We use a lower temperature for consistent grading
    model = get_model(temperature=0.1)
    user_answer = state["messages"][-1].content
    
    prompt = f"Grade this answer on a scale of 0-10. Answer with JUST the number: {user_answer}"
    response = model.invoke(prompt)
    
    try:
        score = int(response.content.strip())
    except:
        score = 0

    # Logic for skill gaps
    gaps = []
    if score < 7:
        gaps.append("Current Topic") # In a real app, use an LLM to identify the specific topic

    return {"score": state["score"] + score, "skill_gap": gaps}