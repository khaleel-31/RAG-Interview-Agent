def route_logic(state) -> str:
    # Pure core routing logic extracted for modular testing
    current_score = state.get("score", 0)
    if current_score >= 50 and state.get("level") == "beginner":
        return "level_up"
    if state.get("skill_gap") and len(state["skill_gap"]) > 0:
        return "teach"
    return "continue"
