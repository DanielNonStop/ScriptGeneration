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
model = "gpt-5"
max_output_tokens = 1500
platform = "Instagram"

system_prompt = f"""
You are an AI assistant specialized in creating engaging video scripts for content creators and related industries.

Requirements:
    1. Generate a complete, polished video script in {language}.
    2. Adopt a {tone_of_voice} tone throughout the script.
    3. If keywords are provided, integrate them seamlessly and naturally into the text.
    4. The script must be concise, fluid, and designed for spoken delivery in a single video. Avoid dividing the
    content into separate scenes or parts - the output should be a continuous narrative.
    5. Ensure the script captures attention quickly, maintains viewer engagement, and ends with a clear, impactful
    closing line.
    6.The output should be only the final script text, without explanations, notes, or formatting beyond the natural
    flow of the script.
    7. (Optional, if input is provided) Adapt the script to the target audience, platform
    (e.g., YouTube Shorts, TikTok, Instagram Reels), or subject matter.
"""

user_prompt = f"""
User request: {client_input_text}

Keywords: {", ".join(keywords) if keywords else "None"}

Target platform: {platform if platform else "None"}
"""

additional_kwargs = (
    {"max_completion_tokens": max_output_tokens, "temperature": 1}
    if model in {"gpt-5", "gpt-5-mini", "gpt-5-nano"}
    else {"max_tokens": max_output_tokens, "temperature": temperature}
)

response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    model=model,
    **additional_kwargs
)

output_script = response.choices[0].message.content
print("Generated Script:\n")
print(output_script)

print("\n--- Debug Info ---")
print("Total tokens used:", response.usage.total_tokens)
