## 💬 Samukelo’s Personal Codex Agent

A lightweight, retrieval-augmented chatbot that answers questions about **me** as a candidate.  
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
- **Retrieve** — Top-k relevant chunks pulled from the FAISS index
- **Generate** — A hosted LLM Gemini generates an answer, guided by tone/mode templates
- **Respond** — Answer shown in my “voice” in a chat interface

---

## Tech Stack

| Tool             | Role                                  |
|------------------|---------------------------------------|
| **Streamlit**    | Simple UI (sidebar + chat interface)  |
| **FAISS**        | Local vector search engine            |
| **MiniLM**       | Embedding model for semantic search   |
| **Gemini API**   | Primary hosted LLM (free dev tier)    |
| **LangChain**    | Retrieval + prompt orchestration      |

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

    ## Setup & Run (Local)
    
    1. Clone repo & create venv
     ```bash
     git clone <repo-url>
     cd PersonalCodexAgent
     python -m venv venv
     source venv/bin/activate   # On Windows: venv\Scripts\activate

     2. Install dependencies
     Install dependencies

     3. Add your API key to the environment
     export GEMINI_API_KEY=your_key_here

     4. Run the app
     streamlit run app.py
    

---


## Deployment (Streamlit Cloud)
1. Push your code to GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo and select **app.py** as the entry point.
4. In **Settings** → **Secrets**, add: GEMINI_API_KEY = your_key_here
5. Deploy! You’ll get a public link to share.

---

## Demo Workflow
1. Select an **answer mode** (e.g., Interview).
2. Ask a question like:
  - "What kind of engineer are you?"
  - "Tell me about your strongest technical skills."
  - "What challenges did you face in your final year?"
3. View the Codex answer in my voice.
4. Use **Clear Chat** or **Regenerate Answer** features as needed.
[Video Demo](https://photos.app.goo.gl/ruL92zW29vtxtA7A8)

---

## Design Chieces
- **Hosted LLM (Gemini)**: reliable APIs, avoids local setup hassles.
- **Multi-mode outputs**: answers can adapt for interviews vs storytelling.
- **RAG grounding**: prevents hallucinations, ensures answers come from my own docs.
- **Auto-refresh index**: adding new .md files auto-updates without restart.
- **Polished UI**: clean chat interface without extra doc references.

 ---

## Sample Q&A
**Q**: What kind of engineer are you?
**Interview mode**: "I'm passionate about AI, Software Engineering, Data, and IoT. I want to leverage technology to solve technical problems and positively impact people's lives. The documents don't state a specific type of engineer."

**Q**: Tell me about the Ndishi Boys.
**Storytelling mode**: "The Ndishi Boys are a campus crew consisting of me, Gagashe, and Ndishi. We formed our group during our undergraduate studies. Ndishi was our leader for Applied Systems Implementation. The three of us even have a WhatsApp group. Zolile, who's very close to us, is like our honorary sister. We're a tight-knit group, and we even boycotted our graduation ceremony together so we could attend the honours ceremony next year."

**Q**: What challenges did you face in your final year?
**Fast Facts mode**:
- My final year had its fair share of challenges, especially regarding the COMP315 group project.
- My team, RALLSMOH, led by Mhlongo, was tasked with building a quiz game in C++.
- We didn't follow the rubric correctly, which led to a harsh critique from our lecturer, Yuvika. She even threatened to give us a 4/100!
- Since that project counted for 50% of my grade, I was extremely stressed, fearing I wouldn't qualify for the exam.
- I even resorted to drinking Ballantine's whiskey mixed with Monster energy drink, which I jokingly called isikhuthazi, as a coping mechanism during that time.
- In the end, Yuvika gave us a 45%, so I qualified for the exam—thank goodness for that!

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
- More deployment options (Hugging Face Spaces).
- Real-time token streaming.

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
- [Facebook](https://www.facebook.com/samkelo.mkhize.3363334)
- [Reddit](https://www.reddit.com/user/samkelo_m_/)

### Future Plans
- Add web search for external context
- Implement user authentication
- Support more document types (Word, HTML)
- Improve UI with custom themes
- Add conversation export
- Track usage and rate limits
