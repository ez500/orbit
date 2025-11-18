from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Write an email to a customer updating them on our updated shipment."}
    ]
)

response2 = client.images.generate(
    model="gpt-image-1",
    messages=[
        {"role": "user", "content": "Create an image of a futuristic cityscape at sunset."}
    ]
)

print(response.choices[0].message["content"])
