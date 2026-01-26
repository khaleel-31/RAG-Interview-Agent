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


⚙️ Setup & Installation
1. Clone the repository
Bash
git clone [https://github.com/your-username/RAG-Interview-Agent.git](https://github.com/your-username/RAG-Interview-Agent.git)
cd RAG-Interview-Agent
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Configure Secrets
Create a .streamlit/secrets.toml file (for local dev) or add these to your Streamlit Cloud Secrets dashboard:

Ini, TOML
GROQ_API_KEY = "your_groq_key"
HUGGINGFACEHUB_API_TOKEN = "your_hf_token"
LANGCHAIN_API_KEY = "your_langsmith_key"
LANGCHAIN_TRACING_V2 = "true"
# If in Europe/UK:
# LANGCHAIN_ENDPOINT = "[https://eu.api.smith.langchain.com](https://eu.api.smith.langchain.com)"
4. Run the App
Bash
streamlit run main.py
🧠 Challenges & Lessons Learned
1. SQLite Versioning & ChromaDB
Streamlit Cloud runs on an older version of SQLite (3.31), while ChromaDB requires 3.35+. I implemented a Monkey Patch using pysqlite3-binary by remapping sys.modules['sqlite3'] at the top of main.py to ensure cloud compatibility.

2. RAG Authentication Protocols
Resolved 401 Unauthorized (Hugging Face) and 403 Forbidden (LangSmith) errors by migrating to Read-Only tokens and configuring specific Regional Endpoints for tracing in the cloud environment.

3. Stateful UI Sync
To keep the Streamlit frontend in sync with the LangGraph backend, I implemented a post-stream state retrieval pattern that forces the UI to rerun and update metrics (like scores) immediately after the graph finishes a turn.

🛤️ Future Roadmap
Phase 1: Automatic PDF parsing for Resumes and JDs using PyPDF2.

Phase 2: Multi-Agent coordination with a "Reviewer Agent" to critique and diversify questions.

Phase 3: Detailed performance dashboards using Plotly to visualize candidate growth over time.

📄 License
Distributed under the MIT License. See LICENSE for more information.


---

### **How to Update your GitHub Repository**
1.  **Open terminal:** Go to your project folder.
2.  **Paste content:** Paste the text above into your `README.md`.
3.  **Sync:**
    ```bash
    git add README.md
    git commit -m "docs: finalized unified readme with roadmap and challenges"
    git push origin main
    ```

[This tutorial on creating professional GitHub READMEs](https://www.youtube.com/watch?v=rCt9DatF63I) is helpful for learning how to add badges and icons to make your repository even more visually appealing to recruiters.


http://googleusercontent.com/youtube_content/7

