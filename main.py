__import__('pysqlite3')
import sys
sys.modules['sqlite3']=sys.modules.pop('pysqlite3')
import streamlit as st
import uuid
from app.graph import app
from langchain_core.messages import HumanMessage

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Adaptive AI Interviewer", page_icon="🤖", layout="wide")
st.title("🤖 Adaptive Technical Interview Coach")
st.caption("Conceptual & Architectural Evaluation Mode")

# --- 2. INITIALIZE SESSION STATE ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# Global config for LangGraph persistence
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# --- 3. SIDEBAR: STATS & PROGRESS ---
with st.sidebar:
    st.header("📋 Interview Context")
    jd_text = st.text_area(
        "Job Description:", 
        height=200, 
        placeholder="Paste JD here...",
        disabled=st.session_state.interview_started
    )
    
    st.divider()
    st.header("📈 Live Progress")
    
    # FETCH REAL-TIME STATE FROM GRAPH
    try:
        # This pulls the actual accumulated score from MemorySaver
        current_state = app.get_state(config).values
        level = current_state.get("level", "beginner").capitalize()
        score = current_state.get("score", 0)
        gaps = current_state.get("skill_gap", [])
    except Exception:
        level = "Beginner"
        score = 0
        gaps = []

    # Visual indicators for the user
    col1, col2 = st.columns(2)
    col1.metric("Score", f"{score} pts")
    col2.metric("Level", level)
    
    st.progress(min(score / 50, 1.0), text=f"Progress to Intermediate: {score}/50")
    
    if gaps:
        with st.expander("🎯 Focus Areas"):
            for gap in list(set(gaps)): # Unique gaps
                st.write(f"- {gap}")

# --- 4. CHAT DISPLAY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. INTERVIEW LOGIC ---

# A. START BUTTON
if not st.session_state.interview_started:
    if st.button("Start Interview", use_container_width=True):
        if not jd_text:
            st.warning("Please provide a Job Description first.")
        else:
            st.session_state.interview_started = True
            # Initial payload to trigger the Researcher -> Interviewer flow
            initial_input = {
                "messages": [HumanMessage(content="Initialize interview.")],
                "level": "beginner",
                "score": 0,
                "skill_gap": [],
                "job_description": jd_text
            }
            
            # Run graph until it hits the first 'interviewer' interrupt
            for event in app.stream(initial_input, config, stream_mode="values"):
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    if last_msg.type == "assistant":
                        # We don't append to st.messages here, we let the rerun handle display
                        pass
            st.rerun()

# B. CHAT INPUT
user_input = st.chat_input("Explain your architectural approach...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # 1. DO NOT pass a new input dictionary like {"messages": ...}
        # Instead, pass NONE as the first argument. 
        # This tells LangGraph to "Resume where you left off"
        # We use st.session_state.thread_id to find the paused state.
        
        # First, we need to provide the user's answer to the paused state
        app.update_state(config, {"messages": [HumanMessage(content=user_input)]})
        
        # 2. Resume the stream
        for msg, metadata in app.stream(None, config, stream_mode="messages"):
            if metadata["langgraph_node"] in ["interviewer", "evaluator"]:
                full_response += msg.content
                placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    st.rerun()