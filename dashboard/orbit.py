from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Write an email to a customer updating them on our updated shipment."}
    ]
)

print(response.choices[0].message["content"])
