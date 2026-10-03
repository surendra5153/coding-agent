import openai
from openai import OpenAI
 
from llm import BASE_URL, client
 
# 1) Wrong API key -> 401
bad_client = OpenAI(api_key="gsk_this_is_wrong", base_url=BASE_URL, max_retries=0)
try:
    bad_client.chat.completions.create(model="any", messages=[{"role": "user", "content": "hi"}])
except openai.AuthenticationError as e:
    print("AuthenticationError, status", e.status_code)
 
# 2) Model that does not exist -> 404 (or 400, depending on provider)
try:
    client.chat.completions.create(model="no-such-model", messages=[{"role": "user", "content": "hi"}])
except (openai.NotFoundError, openai.BadRequestError) as e:
    print(type(e).__name__, "status", e.status_code)
 
# 3) Catch-all for anything the API rejects
try:
    client.chat.completions.create(model="no-such-model", messages=[])
except openai.APIStatusError as e:
    print("APIStatusError, status", e.status_code)