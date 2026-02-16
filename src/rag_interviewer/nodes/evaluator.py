import json
import re
from rag_interviewer.utils.models import get_model
from langchain_core.messages import AIMessage
from rag_interviewer.logging import get_logger

log = get_logger(__name__)


def evaluator_node(state):
    log.info("\n--- ⚖️ CONCEPTUAL EVALUATION START ---")
    model = get_model()
    messages = state.get("messages", [])
    if not messages or messages[-1].type != "human":
        return {"score": 0}
    user_answer = messages[-1].content
    last_question = "No previous question found."
    for msg in reversed(messages[:-1]):
        if msg.type == "assistant" and "**Assessment:**" not in msg.content:
            last_question = msg.content
            break
    eval_prompt = f"""
    You are a Senior Technical Architect grading a candidate.
    Current Level: {state.get('level', 'beginner')}
    
    Question: {last_question}
    Answer: {user_answer}
    
    --- 🛡️ GRADING RULES ---
    - Focus on technical theory and architecture.
    - Provide a 1-sentence concise critique.
    
    CRITICAL: Output ONLY a plain JSON object. 
    DO NOT use markdown code blocks (```json). DO NOT add preamble text.
    {{
        "points": (integer 0-10),
        "missed_topics": ["topic1"],
        "feedback": "critique text"
    }}
    """
    try:
        response = model.invoke(eval_prompt)
        content = response.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found")
        data = json.loads(json_match.group())
        awarded_points = int(data.get("points", 0))
        missed_topics = data.get("missed_topics", [])
        current_total_score = int(state.get("score", 0))
        new_cumulative_total = current_total_score + awarded_points
        current_level = state.get("level", "beginner")
        new_level = current_level
        level_up_msg = ""
        if new_cumulative_total >= 50 and current_level == "beginner":
            new_level = "intermediate"
            level_up_msg = "\n\n🚀 **LEVEL UP!** Shifting to Intermediate System Design."
        elif new_cumulative_total >= 100 and current_level == "intermediate":
            new_level = "advanced"
            level_up_msg = "\n\n🏆 **LEVEL UP!** Moving to Advanced AI Architecture."
        clean_feedback = data.get('feedback', '').replace('`', '').strip()
        feedback_msg = f"**Assessment:** {awarded_points}/10\n\n{clean_feedback}{level_up_msg}"
        return {
            "score": awarded_points,
            "skill_gap": missed_topics if awarded_points < 7 else [],
            "level": new_level,
            "messages": [AIMessage(content=feedback_msg)]
        }
    except Exception as e:
        log.error(f"!!! EVALUATOR ERROR: {e}")
        return {"score": 0, "messages": [AIMessage(content="Response noted. Let's move on.")]}
