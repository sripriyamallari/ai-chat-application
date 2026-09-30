import streamlit as st
import time
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖"
)

st.title("🤖 AI Chat Assistant")
st.caption("Gemini LLM Chat Application")

# ---------------- API KEY ----------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("⚙️ Settings")

    system_prompt = st.text_area(
        "Custom Instructions",
        value="""You are a helpful and knowledgeable AI assistant.

Give clear, detailed, and beginner-friendly answers.

When explaining programming concepts, include:
- A simple definition
- How it works
- A practical example
- Code examples when useful
- Important points or common mistakes

Use headings, bullet points, and code blocks.
Do not make answers unnecessarily short.""",
        height=180
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    max_tokens = st.slider(
        "Max Output Tokens",
        min_value=100,
        max_value=2000,
        value=1500,
        step=100
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------- USER INPUT ----------------

user_input = st.chat_input("Type your message...")

if user_input:

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Convert history to Gemini format
    history = []

    for message in st.session_state.messages:

        gemini_role = (
            "model"
            if message["role"] == "assistant"
            else "user"
        )

        history.append(
            types.Content(
                role=gemini_role,
                parts=[
                    types.Part(
                        text=message["content"]
                    )
                ]
            )
        )

    # ---------------- API CALL WITH RETRY ----------------

    try:

        with st.chat_message("assistant"):

            with st.spinner("Gemini is thinking..."):

                response = None

                for attempt in range(3):

                    try:

                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=history,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt,
                                temperature=temperature,
                                max_output_tokens=max_tokens
                            )
                        )

                        break

                    except Exception as api_error:

                        error_text = str(api_error)

                        if (
                            "503" in error_text
                            or "UN