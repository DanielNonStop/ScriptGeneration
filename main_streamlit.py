import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title("AI Script Generator")

st.sidebar.header("Configuration")

# --- Initialize session state ---
if "script_count" not in st.session_state:
    st.session_state["script_count"] = 0
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Model selection ---
model = st.sidebar.selectbox(
    "Choose a model",
    options=["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]
)

# --- Tone of voice ---
tone_of_voice = st.sidebar.selectbox(
    "Tone of voice",
    options=["casual", "professional", "humorous", "inspirational", "dramatic"],
    index=0
)

# --- Language ---
language = st.sidebar.selectbox(
    "Script language",
    options=["English", "Ukrainian", "Spanish", "French", "German", "Italian", "Portuguese"],
    index=0
)

# --- Platform ---
platform = st.sidebar.selectbox(
    "Target platform",
    options=["Instagram", "YouTube", "TikTok"],
    index=0
)

# --- Temperature ---
if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
    st.sidebar.write("Creativity (Temperature): fixed at 1.0 for gpt-5 models")
    temperature = 1.0
else:
    temperature = st.sidebar.slider(
        "Creativity (Temperature)", 
        0.0, 
        1.0, 
        0.7, 
        0.01
    )

# --- Duration ---
speech_duration = st.sidebar.slider("Duration of speech (seconds)", 20, 180, 60, 5)

# --- Input fields ---
input_text = st.text_area(
    "Describe your script idea",
    "A motivational video about staying strong after failure.",
    height=150
)

keywords = st.text_input(
    "Optional keywords (comma separated)",
    "resilience, success, persistence"
)

# --- Default system instruction ---
default_instruction = """
    You are an AI assistant specialized in creating video scripts for content creators and related industries.
        
    Task:
        - Generate a complete, polished video script which reveals the topic provided by user
        - Script must be generated in the language provided by user
        - If keywords are provided, integrate them seamlessly and naturally into the video script 
        - Adopt a tone throughout the script to the one provided by user.
        - If video script is big enough, try to split it on meaningful paragraphs.

    Requirements:
        1. The script must be concise, fluid, and designed for spoken delivery in a short-form video. Avoid dividing the content into separate scenes — the output should be a continuous narrative.
        2. Ensure the script captures attention quickly, maintains viewer engagement, and ends with a clear, impactful closing line.
        3. Output should be only the final script text, without explanations, notes, or formatting beyond the natural flow of the script.
        4. The length of output text should match the length of speech requested by user.
        5. (Optional, if input is provided) Adapt the script to the target audience, platform
        (e.g., YouTube Shorts, TikTok, Instagram Reels), or subject matter.
    """

input_instruction = st.text_area(
    "Input Prompt",
    default_instruction,
    height=350
)

# --- Reference options ---
use_history_as_reference = st.sidebar.checkbox("Use previous scripts as style reference", value=False)

selected_refs = []
if use_history_as_reference and st.session_state["history"]:
    options = [f"Script {i+1}: {entry['input_text'][:40]}..." 
               for i, entry in enumerate(st.session_state["history"])]
    selected_refs = st.sidebar.multiselect(
        "Select past scripts to use as reference",
        options=options,
        default=[]
    )


# --- Prompt builders ---
def build_system_prompt():
    if input_instruction.strip() == '':
        return default_instruction
    return input_instruction

def build_user_prompt():
    return f"""
        User script idea: {input_text}
        
        Keywords: {keywords or 'None'}
        
        Target platform: {platform or 'None'}

        Language: {language}

        Tone of voice: {tone_of_voice}

        Speech duration: {speech_duration} seconds
    """

def build_reference_messages():
    reference_messages = []
    if use_history_as_reference and selected_refs:
        for ref_label in selected_refs:
            idx = int(ref_label.split()[1].replace(":", "")) - 1
            if 0 <= idx < len(st.session_state["history"]):
                example = st.session_state["history"][idx]
                reference_messages.append({
                    "role": "user",
                    "content": f"(Example) Script idea: {example['input_text']}"
                })
                reference_messages.append({
                    "role": "assistant",
                    "content": example['output']
                })
    return reference_messages


# --- Generate button ---
if st.button("Generate Script"):
    messages = [{"role": "system", "content": build_system_prompt()}]

    # Add past style references
    messages.extend(build_reference_messages())

    # Add new request
    messages.append({"role": "user", "content": build_user_prompt()})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
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
        "speech_duration": speech_duration
    })

# --- Display history ---
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
        st.write(f"**Speech duration:** {entry['speech_duration']}")
        st.write(f"**Generated Script:**\n\n{entry['output']}")
        st.write(f"**Total Tokens Used:** {entry['total_tokens']}")
        st.write("---")
