import streamlit as st
from app.graph import app

st.title("Gemini Interview Coach")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.state = {"messages": [], "level": "beginner", "score": 0, "skill_gap": [], "tech_context": ""}

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Run the Graph
    inputs = {"messages": [("user", prompt)], "level": st.session_state.state["level"], "score": st.session_state.state["score"]}
    config = {"configurable": {"thread_id": "1"}}
    
    # Get the latest state from the graph
    output = app.invoke(inputs, config)
    ai_msg = output["messages"][-1].content
    
    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
    st.chat_message("assistant").write(ai_msg)