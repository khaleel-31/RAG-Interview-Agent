from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.state import InterviewState
from app.nodes.interviewer import interviewer_node
from app.nodes.evaluator import evaluator_node
from app.nodes.researcher import researcher_node
from app.nodes.debug import debug_node

# --- 1. ROUTING LOGIC ---
def route_logic(state: InterviewState):
    # This will now show the REAL accumulated score from the state
    current_score = state.get("score", 0)
    print(f"--- 🚦 ROUTING LOGIC (Score: {current_score}) ---")
    
    # 1. Level Up Check
    if current_score >= 50 and state.get("level") == "beginner":
        return "level_up"
    
    # 2. Skill Gap Check
    if state.get("skill_gap") and len(state["skill_gap"]) > 0:
        return "teach"
    
    # 3. Default
    return "continue"

# --- 2. GRAPH ASSEMBLY ---
workflow = StateGraph(InterviewState)

workflow.add_node("researcher", researcher_node)
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("debug", debug_node) # Debug node registered

# --- 3. EDGES & FLOW ---
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "interviewer")
workflow.add_edge("interviewer", "evaluator")

# ✅ CRITICAL CHANGE: Connect Evaluator to Debug
workflow.add_edge("evaluator", "debug")

# ✅ CRITICAL CHANGE: Conditional edges now trigger AFTER Debug
workflow.add_conditional_edges(
    "debug", 
    route_logic,
    {
        "teach": "interviewer",
        "level_up": "researcher",
        "continue": "interviewer",
        "end": END
    }
)

# --- 4. PERSISTENCE & COMPILATION ---
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_after=["interviewer"])

print("--- ✅ GRAPH COMPILED SUCCESSFULLY ---")