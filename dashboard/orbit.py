from openai import OpenAI
import os

from dashboard.models import Task

client = OpenAI(api_key="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")

response = client.chat.completions.create(
    model="gpt-5-nano",
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

Task.objects.create(
    name="Email Update",
    description=response.choices[0].message["content",
    status="todo",
    assigned_to="user123"
)

print(response.choices[0].message["content"])
