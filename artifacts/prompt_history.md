# Prompt History

This file logs the evolution of my prompts and design instructions.

---

### Early Exploration
- Started with basic prompts like:  
  *“Tell me about Samukelo’s strongest skills”*  
  Response was generic and not grounded in documents.

- Added explicit instruction:  
  *“Answer as Samukelo (first-person). If info not in context, say so briefly and avoid making things up.”*  
  → Prevented hallucination.

---

### Refining Context Usage
- Initial prompt injected the whole retrieved chunk directly.
- Refined with sections:

STYLE: <mode>
CONTEXT: """<docs>"""
QUESTION: <user question>

→ Model stuck closer to context.

---

### Modes / Tones
- Added selectable modes in `prompts.py`:
- Interview (short, professional)
- Storytelling (longer, anecdotal)
- Fast Facts (bullet-pointed)
- Humble Brag (playful, confident)

---

### Final Template
