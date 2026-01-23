import os
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from app.graph import app  # Ensure your LangGraph is exported as 'app'

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Adaptive AI Interviewer", page_icon="🤖", layout="wide")

# Custom CSS to force the chat to expand and prevent nested scrollbars
st.markdown("""
    <style>
        .stChatMessage { overflow-wrap: break-word !important; }
        .main .block-container { max-width: 95% !important; padding-top: 2rem !important; }
        /* This prevents the code/text blocks from creating weird internal scrolls */
        .stMarkdown div { overflow: visible !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Adaptive Technical Interview Coach")
st.caption("Conceptual & Architectural Evaluation Mode")

# --- 2. INITIALIZE SESSION STATE ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# Configuration for LangGraph persistence
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
    
    if st.session_state.interview_started:
        if st.button("🔄 Reset Interview", use_container_width=True):
            # Clear everything to start fresh
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    st.divider()
    st.header("📈 Live Progress")
    
    # FETCH REAL-TIME STATE FROM GRAPH MEMORY
    try:
        current_state = app.get_state(config).values
        level = current_state.get("level", "beginner").capitalize()
        score = current_state.get("score", 0)
        # Handle skill gaps as unique items to avoid list bloating in UI
        gaps = list(set(current_state.get("skill_gap", [])))
    except Exception:
        level, score, gaps = "Beginner", 0, []

    col1, col2 = st.columns(2)
    col1.metric("Score", f"{score} pts")
    col2.metric("Level", level)
    
    # Dynamic progress bar based on current level threshold
    threshold = 50 if level == "Beginner" else 100
    st.progress(min(score / threshold, 1.0), text=f"Progress: {score}/{threshold}")
    
    if gaps:
        with st.expander("🎯 Identified Skill Gaps"):
            for gap in gaps:
                st.write(f"• {gap}")

# --- 4. CHAT DISPLAY ---
# Display historical messages from session state
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. INTERVIEW LOGIC ---

# A. START BUTTON
if not st.session_state.interview_started:
    if st.button("🚀 Start Interview", use_container_width=True):
        if not jd_text:
            st.warning("Please provide a Job Description first.")
        else:
            st.session_state.interview_started = True
            initial_input = {
                "messages": [HumanMessage(content="Initialize interview.")],
                "level": "beginner",
                "score": 0,
                "skill_gap": [],
                "job_description": jd_text
            }
            
            # Initial run to trigger Researcher -> Interviewer
            # We catch the first assistant message to show it in UI
            init_msg = ""
            for event in app.stream(initial_input, config, stream_mode="values"):
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    if last_msg.type == "assistant":
                        init_msg = last_msg.content
            
            if init_msg:
                st.session_state.messages.append({"role": "assistant", "content": init_msg})
            st.rerun()

# B. CHAT INPUT
user_input = st.chat_input("Discuss your architectural approach...")

if user_input:
    # 1. Immediately display user message in UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. Process Assistant Response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Pass the human answer to the paused graph state
        app.update_state(config, {"messages": [HumanMessage(content=user_input)]})
        
        # Stream the new tokens from the Evaluator and next Interviewer question
        # stream_mode="messages" allows us to see node transitions
        for msg, metadata in app.stream(None, config, stream_mode="messages"):
            if msg.content:
                # OPTIONAL: Add a visual break if moving from evaluation to a new question
                if metadata["langgraph_node"] == "interviewer":
                    if "---" not in full_response:
                        full_response += "\n\n---\n\n"
                
                full_response += msg.content
                placeholder.markdown(full_response + "▌") # Animated cursor
        
        placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Final rerun to refresh Sidebar Metrics (Score/Level) based on the new evaluation
    st.rerun()