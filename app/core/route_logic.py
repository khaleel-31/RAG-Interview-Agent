def route_logic(state) -> str:
    # This function encapsulates the routing decisions based on current state
    current_score = state.get("score", 0)
    # Level up check
    if current_score >= 50 and state.get("level") == "beginner":
        return "level_up"
    # Skill gap check
    if state.get("skill_gap") and len(state["skill_gap"]) > 0:
        return "teach"
    # Default continuation
    return "continue"
