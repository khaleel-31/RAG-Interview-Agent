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
            # Skip evaluation feedback messages to find the actual interview question
            if "**Assessment:**" not in msg.content:
                last_question = msg.content
                break

    eval_prompt = f"""
    You are a Senior Technical Architect grading a candidate's conceptual understanding.
    Current Candidate Level: {state.get('level', 'beginner')}
    
    Question Asked: {last_question}
    Candidate Answer: {user_answer}
    
    --- 🛡️ GRADING GUARDRAILS ---
    - Focus on technical theory, logic, and architecture.
    - Award points based on the depth and accuracy of the explanation.
    
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
        
        # Robust JSON extraction
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError(f"LLM Response missing JSON: {content}")
            
        data = json.loads(json_match.group())
        
        # Force integer casting for operator.add compatibility
        awarded_points = int(data.get("points", 0))
        missed_topics = data.get("missed_topics", [])
        
        # 3. Cumulative Level-Up Logic
        # We need the current total from state to see if they cross the threshold
        current_total_score = int(state.get("score", 0))
        new_cumulative_total = current_total_score + awarded_points
        
        current_level = state.get("level", "beginner")
        new_level = current_level
        
        level_up_msg = ""
        # Check against the NEW cumulative total, not just the single turn points
        if new_cumulative_total >= 50 and current_level == "beginner":
            new_level = "intermediate"
            level_up_msg = "\n\n🚀 **LEVEL UP!** You've cleared the fundamentals. Shifting focus to Intermediate System Design."
        elif new_cumulative_total >= 100 and current_level == "intermediate":
            new_level = "advanced"
            level_up_msg = "\n\n🏆 **LEVEL UP!** You are moving into Advanced AI Architecture."

        feedback_msg = f"**Assessment:** {awarded_points}/10\n{data.get('feedback', '')}{level_up_msg}"

        # --- DEBUG LOGGING ---
        print(f"Points This Turn: {awarded_points}")
        print(f"Total Score (In State): {new_cumulative_total}")
        print(f"Current Level: {new_level}")
        print("--- ⚖️ EVALUATION COMPLETE ---\n")

        # 4. Return updates
        # 'score' will be added to existing state score via operator.add
        return {
            "score": awarded_points, 
            "skill_gap": missed_topics if awarded_points < 7 else [],
            "level": new_level,
            "messages": [AIMessage(content=feedback_msg)]
        }

    except Exception as e:
        print(f"!!! EVALUATOR ERROR: {e}")
        return {
            "score": 0, 
            "messages": [AIMessage(content="I've noted your response. Let's proceed to the next topic.")]
        }