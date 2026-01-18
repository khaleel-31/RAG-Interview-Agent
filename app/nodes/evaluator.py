import json
import re
from app.utils.models import get_model
from langchain_core.messages import AIMessage

def evaluator_node(state):
    print("\n--- ⚖️ CONCEPTUAL EVALUATION START ---")
    
    model = get_model() 
    messages = state.get("messages", [])
    
    # 1. Validation: Ensure there is a user message to evaluate
    if not messages or messages[-1].type != "human":
        print("No human message found to evaluate.")
        return {"score": 0}

    user_answer = messages[-1].content
    
    # 2. Identify the last question asked by the assistant
    last_question = "No previous question found."
    for msg in reversed(messages[:-1]):
        if msg.type == "assistant":
            # Skip feedback messages, look for the actual question
            if "Assessment:" not in msg.content:
                last_question = msg.content
                break

    eval_prompt = f"""
    You are a Senior Technical Architect grading a candidate's conceptual understanding.
    Current Candidate Level: {state.get('level', 'beginner')}
    
    Question Asked: {last_question}
    Candidate Answer: {user_answer}
    
    --- 🛡️ GRADING GUARDRAILS ---
    - Focus on technical theory, logic, and architecture.
    - Ignore lack of code snippets or minor syntax errors.
    
    CRITICAL: Return ONLY a raw JSON object.
    {{
        "points": (integer 0-10),
        "missed_topics": ["topic1", "topic2"],
        "feedback": "1-sentence critique of their logic"
    }}
    """
    
    try:
        response = model.invoke(eval_prompt)
        content = response.content
        
        # Robust JSON extraction (removes markdown backticks if present)
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError(f"LLM Response missing JSON: {content}")
            
        data = json.loads(json_match.group())
        
        # FORCE CASTING TO INTEGER (Critical for operator.add)
        awarded_points = int(data.get("points", 0))
        missed_topics = data.get("missed_topics", [])
        
        # 3. Level-Up Check
        # We calculate projected total just for the Level-Up logic
        current_total = int(state.get("score", 0))
        projected_total = awarded_points
        current_level = state.get("level", "beginner")
        new_level = current_level
        
        level_up_msg = ""
        if projected_total >= 50 and current_level == "beginner":
            new_level = "intermediate"
            level_up_msg = "\n\n🚀 **LEVEL UP!** You've demonstrated strong fundamentals. Shifting focus to Intermediate System Design."

        feedback_msg = f"**Assessment:** {awarded_points}/10\n{data.get('feedback', '')}{level_up_msg}"

        # --- DEBUG LOGGING ---
        print(f"Points Awarded: {awarded_points}")
        print(f"New Projected Total: {projected_total}")
        print(f"Current Level: {new_level}")
        print("--- ⚖️ EVALUATION COMPLETE ---\n")

        # 4. Return updates
        # 'score' is ADDED because of Annotated[int, operator.add] in state.py
        return {
            "score": awarded_points, 
            "skill_gap": missed_topics if awarded_points < 7 else [],
            "level": new_level,
            "messages": [AIMessage(content=feedback_msg)]
        }

    except Exception as e:
        print(f"!!! EVALUATOR ERROR: {e}")
        # Return neutral 0 to avoid crashing the graph
        return {
            "score": 0, 
            "messages": [AIMessage(content="I've noted your response. Let's move on to the next concept.")]
        }