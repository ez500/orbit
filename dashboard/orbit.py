from openai import OpenAI
from google import genai


client = genai.Client(api_key="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write an email to a customer updating them on our updated shipment."
)

response2 = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=["Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"]
)

# Task.objects.create(
#     name="Email Update",
#     description=response.choices[0].message["content"],
#     status="in_progress",
#     assigned_to="user123"
# )

print(response.text)

for part in response2.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("../media/generated_test_image.png")
