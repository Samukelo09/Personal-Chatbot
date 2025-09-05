# How to Learn & Debug Something New

Whether you're exploring a new library or chasing down a stubborn bug, this guide helps you stay focused, efficient, and adaptable.

---

## 1. Understand the Big Picture
- Grasp the purpose of the tool or concept.
- Skim official docs, architecture diagrams, or README files.
- Ask: “What problem does this solve?” and “Where does it fit in my workflow?”

## 2. Run a Minimal Example
- Build or find the smallest working snippet.
- Strip away complexity to isolate core behavior.
- Helps you learn the API surface and spot errors early.

## 3. Reproduce the Issue
- Make the bug appear consistently.
- Use controlled inputs and log outputs.
- Confirm whether the issue is in your code, the library, or the environment.

## 4. Trace the Flow
- Use print statements, breakpoints, or logging.
- Track variable states and function calls.
- Tools like `pdb`, VSCode debugger, or `streamlit.logger` are invaluable.

## 5. Decode Error Messages
- Read carefully—don’t skim.
- Look for:
  - Type of error (`AttributeError`, `ImportError`, etc.)
  - Line number and stack trace
  - Keywords that hint at root cause

## 6. Google Strategically
- Search the exact error message + context.
- Add tags like `[python]`, `[streamlit]`, `[openai]`, etc.
- GitHub issues, Stack Overflow, and blog posts are gold mines.

## 7. Rubber Duck or Ask for Help
- Explain your logic out loud—even to a duck 🦆.
- Or better: ask your crew (Ndishi Boys, Izimpisi, or Codex collaborators).
- Teaching forces clarity and often reveals the bug.

## 8. Refactor & Document
- Once fixed, clean up the code.
- Add comments or update your README.
- Future-you (or your team) will thank you.

## 9. Use AI
- Ask AI model for suggestions
- Create simila scenario

---

> “Debugging isn’t just fixing errors—it’s learning how the system *really* works.”
