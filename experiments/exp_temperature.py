from llm import chat
 
prompt = [{"role": "user", "content": "Suggest a one-word name for a pet robot. Reply with the word only."}]
 
for temp in (0.0, 1.2):
    answers = [chat(prompt, temperature=temp)[0].strip() for _ in range(5)]
    print(f"temperature={temp}: {answers}")