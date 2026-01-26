# 🤖 Adaptive RAG Interview Agent

An intelligent, context-aware interview preparation tool built with **LangGraph**, **Groq**, and **ChromaDB**. This agent doesn't just ask questions; it adapts to your skill level and provides real-time feedback based on specific Job Descriptions (JD).

---

## 🚀 Features

* **Adaptive Learning Path:** The agent uses conditional routing to adjust difficulty. If a skill gap is detected, it triggers a "Teacher Mode" to help you improve.
* **RAG-Powered Context:** Uses a **Researcher Node** to query a ChromaDB vector store, ensuring questions are grounded in actual technical documentation.
* **Live Assessment:** An **Evaluator Node** grades your responses on a scale of 1-10 and tracks your progress via a persistent score.
* **Stateful Conversations:** Built with **LangGraph Memory**, allowing the agent to remember your previous answers even after a page refresh.

---

## 🛠️ Tech Stack

* **Orchestration:** [LangGraph](https://github.com/langchain-ai/langgraph) (Stateful Multi-Agent workflows)
* **LLM:** [Groq](https://groq.com/) (Llama 3.3 70B for ultra-fast inference)
* **Vector Database:** [ChromaDB](https://www.trychroma.com/)
* **Embeddings:** Hugging Face (`all-MiniLM-L6-v2`)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Monitoring:** LangSmith

---

## 📂 Project Structure

```text
├── app/
│   ├── nodes/          # LangGraph Node definitions (Researcher, Interviewer, Evaluator)
│   ├── utils/          # LLM configurations and helper functions
│   └── state.py        # Graph state and schema definitions
├── chroma_db/          # Persistent vector store (Context data)
├── main.py             # Streamlit UI and Graph execution logic
├── requirements.txt    # Project dependencies
└── .streamlit/         # Local secrets (ignored by git)
