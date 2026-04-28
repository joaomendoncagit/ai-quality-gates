# This file is just to test if the API key is working. We have to add billing to the account
# $ export OPENAI_API_KEY="..."
# $ python test_api.py

from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say OK"}]
)

print(response.choices[0].message.content)