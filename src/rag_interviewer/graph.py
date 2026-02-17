from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from rag_interviewer.core.route_logic import route_logic as _core_route_logic
from rag_interviewer.core.state import InterviewState
from rag_interviewer.logging import get_logger
from rag_interviewer.nodes.debug import debug_node
from rag_interviewer.nodes.evaluator import evaluator_node
from rag_interviewer.nodes.interviewer import interviewer_node
from rag_interviewer.nodes.researcher import researcher_node

# --- 1. ROUTING LOGIC ---
log = get_logger(__name__)

def route_logic(state: InterviewState) -> str:
    result = _core_route_logic(state)
    log.info(f"Routing decision: {result}")
    return result

# --- 2. GRAPH ASSEMBLY ---
workflow = StateGraph(InterviewState)

workflow.add_node("researcher", researcher_node)
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("debug", debug_node)

# --- 3. EDGES & FLOW ---
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "interviewer")
workflow.add_edge("interviewer", "evaluator")
workflow.add_edge("evaluator", "debug")
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

log.info("--- ✅ GRAPH COMPILED SUCCESSFULLY ---")
