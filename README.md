## 💬 Samukelo’s Personal Codex Agent

A lightweight, retrieval-augmented chatbot that answers questions about me as a candidate.  
It uses my CV and supporting documents—personal stories, honours journey, projects, and more—as its knowledge base.  
The agent supports multiple answer “modes” (Interview, Storytelling, Fast Facts, Humble Brag) so responses adapt to context.

---

## Overview

### Why This Project?
This trial asked for a **Personal Codex Agent**, a chatbot that feels like “me.”  
It had to be context-aware, grounded in my own materials, and able to handle interview-style questions with personality.

### How It Works (At a Glance)
- **Docs Ingestion** — CV + Markdown files stored in `/data/`
- **Index Build** — Documents split into chunks, embedded, and stored in FAISS
- **Query** — User asks a question via the Streamlit app
- **Retrieve** — Top-k most relevant chunks pulled from the index
- **Generate** — Local Ollama LLM (e.g. Mistral) generates an answer, shaped by a tone/mode template
- **Respond** — Answer shown in my “voice,” with context snippets available

---

## Tech Stack

| Tool        | Role                                  |
|-------------|----------------------------------------|
| **Streamlit** | Simple UI (sidebar + chat interface) |
| **FAISS**      | Local vector search engine           |
| **MiniLM**     | Embedding model for semantic search |
| **Ollama**     | Free local LLMs (Mistral, LLaMA3.1, Qwen2.5) |
| **LangChain**  | Retrieval + prompt orchestration     |

---

##  Project Structure
PersonalCodexAgent/

  ├── data/
  
    ├── Samukelo_Mkhize_Resume.pdf
    ├── projects_detail.md
    ├── academic_background.md
    ├── honours_journey.md
    ├── final_year_undergrad.md
    ├── ndishi_boys.md
    ├── academic_background.md
    ├── izimpisi.md
    ├── funny_secret.md
    ├── ndishi_boys.md
    ├── personal_life.md
  ├── rag/
  
    ├── build_index.py
    ├── retriever.py
    └── prompts.py

  
  ├── artifacts/
  
    ├── prompt_history.md
    ├── sub_agents.md
    ├── ai_vs_human_commits.md
  
  ├── requirements.txt
  
  └── README.md

---
  
## Setup & Run
1. Install Ollama & pull a model
  - download: https://ollama.com/download
  - ollama serve
  - ollama pull mistral
2. Create a Virtual Environment
  - python -m venv venv
  - source venv/bin/activate  **On Windows**: venv\Scripts\activate
  - pip install -r requirements.txt
3. Run the app
  - streamlit run app.py

---

## Demo Workflow
1. Select an **answer mode** (e.g., Interview).
2. Ask a question like:
  - "What kind of engineer are you?"
  - "Tell me about your strongest technical skills."
  - "What challenges did you face in final year?"
3. View the Codex answer in my voice.
4. Expand **Retrieved Context** to check the exact snippets used.
5. Try **Clear chat**, or **Regenerate answer** for extra features.
[Video Demo](http://localhost:8501)

---

## Design Chieces
- **Local LLM (Ollama)**: avoids API costs and privacy issues.
- **Multi-mode outputs**: answers can adapt for interviews vs storytelling.
- **RAG grounding**: prevents hallucinations, ensures answers come from my own docs.
- **Auto-refresh index**: adding new .md files auto-updates without restart.
- **Transparency**: retrieved context always shown; artifacts folder captures how I worked with AI tools.

 ---

## Sample Q&A
**Q**: What kind of engineer are you?
**Interview mode**: "As Samukelo, I am a Computer Science and IT graduate with a focus on Artificial Intelligence, Cybersecurity, and Internet of Things (IoT), as mentioned in Doc 1. My academic background includes an Honours Degree in Computer Science and an Undergraduate Degree in Computer Science & IT from the University of KwaZulu-Natal (Doc 2). I have also gained tutoring experience teaching programming fundamentals, data structures, and AI concepts to undergraduate students (Doc 2). My technical approach involves using deep learning models such as Long Short-Term Memory (LSTM) networks and Convolutional Neural Network (CNN) variants for problem-solving (Doc 4). However, the context does not specify a particular engineering discipline"

**Q**: Tell me about the Ndishi Boys.
**Storytelling mode**: "The Ndishi Boys were my close circle — me, Gagashe, and Ndishi. We even had a WhatsApp group. Zolile, though not part of the ‘boys’, was our honorary sister. We supported each other through final-year challenges and even boycotted the graduation ceremony to attend together next year."

**Q**: What challenges did you face in your final year?
**Fast Facts mode**:
  - In my final year of undergraduate studies at the University of KwaZulu-Natal (Doc 4), I faced several challenges:
    - The COMP315 group project (Doc 4) was particularly difficult. Our team, RALLSMOH, had to build a quiz game in C++ and were criticized by our lecturer Yuvika for not following the rubric properly. We initially received a poor grade of 4/100, but eventually managed to improve it (Doc 5).
- Additionally, I struggled with stress during this period and turned to Ballantine's whiskey as a coping mechanism (Doc 2), which I later stopped using in May 2024 (Doc 2).
- Despite these challenges, I was admitted to the honours program, which I saw as a significant milestone in my academic journey (Doc 3).

 ---

## Artifacts
- prompt_history.md → logs of prompts & refinements during development.  
- sub_agents.md → notes on helper roles (TonePolisher, CiteGuard).
-  ai_vs_human_commits.md → tracks which edits were AI-assisted vs manual.

---

## Improvements With More Time
- Live footnote citations in answers (e.g., "Doc2").
- Topic filters (#friends, #projects, #family).
- Resume summarizer mode.
- Deployment on Streamlit Cloud with easy sharing link.
- Token-streaming for real-time typing effect.

## Deplyment
### Streamlit Cloud
1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo
4. Set app.py as the main file

---

### Contributing
This is a personal portfolio project, but suggestions are welcome!
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

### License
This project is licensed under the MIT License.

---

### About Me
I'm **Samukelo Mkhize**, a Computer Science Honours student at the University of KwaZulu-Natal. My expertise includes:
- Machine Learning & AI
- Software Engineering
- Data Science
- Internet of Things

---

Connect with me:
- [GitHub](https://github.com/Samukelo09)
- [LinkedIn](www.linkedin.com/in/samukelo-mkhize-a83156253)
- [Instagram](https://www.instagram.com/samkelo_m_/)
- [ X](https://x.com/samkelo_m_)

### Future Plans
- Add web search for external context
- Implement user authentication
- Support more document types (Word, HTML)
- Improve UI with custom themes
- Add conversation export
- Track usage and rate limits
