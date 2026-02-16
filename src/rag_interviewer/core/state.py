import operator
from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages


class InterviewState(TypedDict):
    messages: Annotated[list, add_messages]
    score: Annotated[int, operator.add]
    skill_gap: Annotated[List[str], operator.add]
    level: str
    tech_context: str
    job_description: str
