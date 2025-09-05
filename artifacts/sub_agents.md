# Sub-Agent Roles

While I built a single Streamlit agent, I conceptually used “sub-agent roles” during development:

---

### Retriever
- Role: given a query, fetch top-k chunks from FAISS index.
- Constraint: return only text from my documents, no external sources.

### Tone Polisher
- Role: adjust the same answer into different tones (Interview, Storytelling, Fast Facts, Humble Brag).
- Helps tailor responses to the setting (recruiter vs friend vs demo).

### CiteGuard
- Role: ensure the agent either uses the retrieved context or explicitly says "not in context".
- Prevents hallucination, ensures transparency.

---

This “sub-agent” framing helped me keep prompts modular and design choices clear.
