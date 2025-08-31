# Ane Personal AI Agent - Samukelo Mkhize

A conversational AI agent that can answer questions about my professional background, skills, and projects. Built with Streamlit, LangChain, and OpenAI's GPT model.

## Features

- **Document Intelligence**: Processes PDF and Markdown documents to create a knowledge base
- **Multiple Conversation Modes**: 
  - Default mode: Factual Q&A about my background
  - Interview mode: Professional responses suitable for job interviews
  - Storytelling mode: Engaging narrative-style answers
  - Creative mode: More imaginative responses
- **Chat Memory**: Maintains conversation context across questions
- **Vector Search**: Uses ChromaDB for efficient document retrieval
- **Easy Deployment**: Ready for deployment on Streamlit Cloud

##  Project Structure
PersonalCodexAgent/

  ├── data/
  
  │ ├── Samukelo_Mkhize_Resume.pdf
  
  │ ├── projects_detail.md
  
  │ └── academic_background.md
  
  ├── src/
  
  │ ├── init.py
  
  │ ├── qa_agent.py
  
  │ └── document_processor.py

  
  ├── artifacts/
  
  │ ├── prompts/
  
  │ └── sub_agents.md
  
  ├── app.py
  
  ├── requirements.txt
  
  ├── .env
  
  ├── .gitignore
  
  └── README.md

  
## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git

### 1. Clone the Repository
git clone https://github.com/Samukelo09/Personal-Chatbot.git
cd Personal-Chatbot

### 2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Configure Environment Variable
Create a .env file in the root directory:
OPENAI_API_KEY=your_openai_api_key_here

### 5. Add Your Documents
Place your resume and supporting files in the data/ folder:
- Resume (PDF or Markdown)
- Project details (Markdown)

### 6. Launch the App
streamlit run app.py

### How to Use
1. Open the app in your browser (usually http://localhost:8501)
2. Click Process Documents to build the knowledge base
3. Click Initialize AI Agent to activate the assistant
4. Choose a conversation mode
5. Sart chatting

### Example Questions
- "What machine learning frameworks am I experienced with?"
- "Tell me about my coin recognition project."
- "What subjects do I tutor at UKZN?"
- "What are my strongest programming skills?"
- "Describe my cloud computing ontology project"

### Technical Overview
**Built With**
- **Streamlit** — UI framework
- **LangChain** — Conversational AI framework
- **OpenAI GPT** — Language model
- **ChromaDB** — Vector store for document retrieval
- **PyPDF** — PDF parsing

### Architecture
1. **Document Processing**: PDFs and Markdown files are chunked and embedded
2. **Vector Storage**: Stored in ChromaDB using OpenAI embeddings
3. **Retrival QA**: Matches questions with relevant chunks
4. **Response Generations**: GPT generates answers using context
5. **Memory**: Maintains chat history for continuity

### Feature Highlights
#### Conversation Modes

- **Default**: Fact-based answers with citations  
- **Interview**: Professional tone for job prep  
- **Storytelling**: Narrative-style responses  
- **Creative**: Imaginative and expressive replies  

#### Document Support
- **PDF** (resumes, certificates)  
- **Markdown** (project details)  
- **Plain text files**  

#### Memory Management
- Tracks multi-turn conversations  
- Option to clear chat history  

### Deployment
#### Streamlit Cloud
1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo
4. Set app.py as the main file
5. Add your OpenAI API key as a secret

#### Secrets Configuration
OPENAI_API_KEY=your_actual_api_key

### Sample Q&A
**Q:** What machine learning frameworks am I experienced with?
**A:** Based on your resume, you’ve worked with TensorFlow, PyTorch, Scikit-learn, NumPy, OpenCV, Pandas, Matplotlib, and Seaborn.

**Q:** Tell me about my coin recognition project
**A:** You built a computer vision system using CNNs to identify South African coins. It achieved 83% accuracy and was implemented in Python with Scikit-learn.

### Contributing
This is a personal portfolio project, but suggestions are welcome!
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### License
This project is licensed under the MIT License.

### About Me
I'm **Samukelo Mkhize**, a Computer Science Honours student at the University of KwaZulu-Natal. My expertise includes:
- Machine Learning & AI
- Software Engineering
- Data Science
- Internet of Things

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
