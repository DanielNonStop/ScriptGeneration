import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title("AI Script Generator")

st.sidebar.header("Configuration")

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

if "history" not in st.session_state:
    st.session_state["history"] = []


def build_system_prompt():
    return f"""
        You are an assistant for generating engaging video scripts.
        
        Requirements:
        1. Generate a complete video script in {language}.
        2. Use a {tone_of_voice} tone of voice.
        3. If keywords are provided, make sure they are naturally included.
        4. The script should be concise, engaging, and ready to be spoken in a video.
        5. Return only the script text, no explanations.
    """


def build_user_prompt():
    return f"""
        User script idea: {input_text}
        
        Keywords: {keywords or 'None'}  
    """


# Generate button
if st.button("Generate Script"):

    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": build_user_prompt()},
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        output = response.choices[0].message.content
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

    except Exception as e:
        st.error(f"An error occurred: {e}")

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
        st.markdown(f"**Generated Script:**\n\n{entry['output']}")
        st.write(f"**Total Tokens Used:** {entry['total_tokens']}")
        st.write("---")
