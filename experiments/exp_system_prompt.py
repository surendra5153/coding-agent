from llm import chat
 
task = {"role": "user", "content": "How do I check if a number is prime?"}
 
styles = {
    "code-only": "Reply ONLY with a Python code block. No explanation.",
    "teacher": "You are a patient teacher. Explain step by step for a beginner, then show code.",
}
 
for name, system_text in styles.items():
    reply, usage, _ = chat([{"role": "system", "content": system_text}, task])
    print(f"===== {name}  ({usage['completion_tokens']} output tokens) =====")
    print(reply, "\n")