from llm import chat
 
first = [{"role": "user", "content": "My name is Asha. Please remember it."}]
reply1, _, _ = chat(first)
print("Call 1:", reply1)
 
# A brand-new request with NO history
reply2, _, _ = chat([{"role": "user", "content": "What is my name?"}])
print("\nCall 2 (no history):", reply2)
 
# Same question, but we resend the earlier turns ourselves
with_history = first + [
    {"role": "assistant", "content": reply1},
    {"role": "user", "content": "What is my name?"},
]
reply3, usage3, _ = chat(with_history)
print("\nCall 3 (with history):", reply3)
print("Prompt tokens for call 3:", usage3["prompt_tokens"])
