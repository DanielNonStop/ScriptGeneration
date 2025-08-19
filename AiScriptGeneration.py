import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

client_input_text = "A story about starting a small business with no budget."
keywords = ["entrepreneurship", "motivation", "social media growth"]
tone_of_voice = "casual"
language = "English"

temperature = 0.8
model = "gpt-4o-mini"
max_output_tokens = 700

system_prompt = f"""
You are an assistant for generating engaging video scripts.

Requirements:
1. Generate a complete video script in {language}.
2. Use a {tone_of_voice} tone of voice.
3. If keywords are provided, make sure they are naturally included.
4. The script should be concise, engaging, and ready to be spoken in a video.
5. Return only the script text, no explanations.
"""

user_prompt = f"""
User request: {client_input_text}

Keywords: {", ".join(keywords) if keywords else "None"}
"""

response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    model=model,
    max_tokens=max_output_tokens,
    temperature=temperature
)

output_script = response.choices[0].message.content
print("Generated Script:\n")
print(output_script)

print("\n--- Debug Info ---")
print("Total tokens used:", response.usage.total_tokens)
