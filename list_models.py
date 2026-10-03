import os
 
from dotenv import load_dotenv
from openai import OpenAI
 
load_dotenv()  # reads .env and puts its values into os.environ
 
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
)
 
for model in client.models.list().data:
    print(model.id)
