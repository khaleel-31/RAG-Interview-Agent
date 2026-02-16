def debug_node(state):
    print("\n" + "="*40)
    print("DEBUG: CURRENT GRAPH STATE")
    print(f"Total Score: {state.get('score')}")
    print(f"Current Level: {state.get('level')}")
    print(f"Messages Count: {len(state.get('messages', []))}")
    print(f"Skill Gaps: {state.get('skill_gap')}")
    print("="*40 + "\n")
    return {}
