
from rag_interviewer.core.route_logic import route_logic


def test_route_logic_level_up():
    state = {
        "score": 60,
        "level": "beginner",
        "skill_gap": [],
    }
    assert route_logic(state) == "level_up"


def test_route_logic_teach_when_skill_gap():
    state = {
        "score": 30,
        "level": "beginner",
        "skill_gap": ["topic1"],
    }
    assert route_logic(state) == "teach"


def test_route_logic_continue_default():
    state = {
        "score": 20,
        "level": "beginner",
        "skill_gap": [],
    }
    assert route_logic(state) == "continue"
