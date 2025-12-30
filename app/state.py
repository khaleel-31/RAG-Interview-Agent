from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    # 'add_messages' ensures chat history is appended, not overwritten
    messages: Annotated[list, add_messages]
    level: str             # "beginner", "intermediate", "advanced"
    score: int             # Tracks performance for level-up logic
    skill_gap: List[str]   # Topics to teach the user
    tech_context: str      # Latest scraped tech news