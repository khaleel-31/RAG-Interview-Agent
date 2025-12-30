from langgraph.graph import StateGraph, START, END
from app.state import InterviewState
from app.nodes.interviewer import interviewer_node
from app.nodes.evaluator import evaluator_node
from langgraph.checkpoint.memory import MemorySaver

def route_next(state):
    if state["score"] > 50 and state["level"] == "beginner":
        return "upgrade"
    return "continue"

workflow = StateGraph(InterviewState)
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("evaluator", evaluator_node)

workflow.add_edge(START, "interviewer")
workflow.add_edge("interviewer", "evaluator")

workflow.add_conditional_edges(
    "evaluator",
    route_next,
    {"upgrade": "interviewer", "continue": "interviewer"}
)
memory = MemorySaver()

app = workflow.compile(checkpointer=memory)

config ={"configurable": {"thread_id": "user_123"}}
output = app.invoke(inputs, config=config)

def route_logic(state):
    # If there are gaps, force a teaching moment
    if state.get("skill_gap"):
        return "teach"
    # If score is high enough, level up
    if state["score"] > 50 and state["level"] == "beginner":
        return "level_up"
    return "continue"

workflow.add_conditional_edges(
    "evaluator",
    route_logic,
    {
        "teach": "interviewer",
        "level_up": "researcher", # Re-scrape for harder level content
        "continue": "interviewer"
    }
)
