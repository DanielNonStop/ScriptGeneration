import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title("AI Script Generator")

st.sidebar.header("Configuration")

st.session_state["script_count"] = 0

# Choose model
model = st.sidebar.selectbox(
    "Choose a model",
    options=["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]
)

# Tone of voice selection
tone_of_voice = st.sidebar.selectbox(
    "Tone of voice",
    options=["casual", "professional", "humorous", "inspirational", "dramatic"],
    index=0
)

# Language selection
language = st.sidebar.selectbox(
    "Script language",
    options=["English", "Ukrainian", "Spanish", "French", "German", "Italian", "Portuguese"],
    index=0
)

platform = st.sidebar.selectbox(
    "Target platform",
    options=["Instagram", "YouTube", "TikTok"],
    index=0
)

# Temperature and tokens
temperature = st.sidebar.slider("Creativity (Temperature)", 0.0, 1.0, 0.7, 0.01)
max_tokens = st.sidebar.slider("Max Tokens", 200, 1200, 700, 50)

input_text = st.text_area(
    "Describe your script idea",
    "A motivational video about staying strong after failure.",
    height=150
)

keywords = st.text_input(
    "Optional keywords (comma separated)",
    "resilience, success, persistence"
)

default_instruction = """You are an AI assistant specialized in creating engaging video scripts for content creators and related industries.
    
    Requirements:
        1. Generate a complete, polished video script in language, provided by user.
        2. Adopt a tone throughout the script to the one provided by user.
        3. If keywords are provided, integrate them seamlessly and naturally into the text.
        4. The script must be concise, fluid, and designed for spoken delivery in a short-form video. Avoid dividing the
        content into separate scenes or parts—the output should be a continuous narrative.
        5. Ensure the script captures attention quickly, maintains viewer engagement, and ends with a clear, impactful
        closing line.
        6.The output should be only the final script text, without explanations, notes, or formatting beyond the natural
        flow of the script.
        7. (Optional, if input is provided) Adapt the script to the target audience, platform
        (e.g., YouTube Shorts, TikTok, Instagram Reels), or subject matter.
    """

input_instruction = st.text_area(
    "Input Prompt",
    default_instruction,
    height=350
)

if "history" not in st.session_state:
    st.session_state["history"] = []


def build_system_prompt():
    if input_instruction == '':
        return default_instruction
    return input_instruction


def build_user_prompt():
    return f"""
        User script idea: {input_text}
        
        Keywords: {keywords or 'None'}
        
        Target platform: {platform or 'None'}

        Language: {language}

        Tone of voice: {tone_of_voice}
    """


# Generate button
if st.button("Generate Script"):

    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": build_user_prompt()},
    ]

    additional_kwargs = (
        {"max_completion_tokens": max_tokens, "temperature": 1}
        if model in {"gpt-5", "gpt-5-mini", "gpt-5-nano"}
        else {"max_tokens": max_tokens, "temperature": temperature}
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **additional_kwargs
    )

    output = response.choices[0].message.content
    print(f"Output: {output}")
    total_tokens = response.usage.total_tokens

    st.session_state["script_count"] += 1
    st.session_state["history"].append({
        "model": model,
        "tone_of_voice": tone_of_voice,
        "language": language,
        "input_text": input_text,
        "keywords": keywords,
        "output": output,
        "total_tokens": total_tokens,
        "temperature": temperature,
        "max_tokens": max_tokens
    })

# Display history
if st.session_state["history"]:
    st.subheader("Script History")
    for idx, entry in enumerate(reversed(st.session_state["history"])):
        st.write(f"### Script {len(st.session_state['history']) - idx}")
        st.write(f"**Model:** {entry['model']}")
        st.write(f"**Language:** {entry['language']}")
        st.write(f"**Tone of voice:** {entry['tone_of_voice']}")
        st.write(f"**Keywords:** {entry['keywords']}")
        st.write(f"**Input Idea:** {entry['input_text']}")
        st.write(f"**Temperature:** {entry['temperature']}")
        st.write(f"**Max Tokens:** {entry['max_tokens']}")
        st.write(f"**Generated Script:**\n\n{entry['output']}")
        st.write(f"**Total Tokens Used:** {entry['total_tokens']}")
        st.write("---")
