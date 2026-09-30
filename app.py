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
        value=(
            "You are a helpful and knowledgeable AI assistant. "
            "Give clear, detailed, beginner-friendly answers. "
            "Use headings, bullet points, examples, and code when useful. "
            "Do not make answers unnecessarily short."
        ),
        height=150
    )

    temperature = st.slider(
        "Temperature",
        0.0,
        2.0,
        0.7,
        0.1
    )

    max_tokens = st.slider(
        "Max Output Tokens",
        100,
        2000,
        1500,
        100
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

        role = (
            "model"
            if message["role"] == "assistant"
            else "user"
        )

        history.append(
            types.Content(
                role=role,
                parts=[
                    types.Part(
                        text=message["content"]
                    )
                ]
            )
        )

    # ---------------- GEMINI API ----------------

    try:

        with st.chat_message("assistant"):

            with st.spinner("Gemini is thinking..."):

                response = None

                # Automatic retry for temporary 503 errors
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

                    except Exception as error:

                        if "503" in str(error):

                            if attempt < 2:
                                time.sleep(2 ** attempt)
                            else:
                                raise

                        else:
                            raise

                # ---------------- RESPONSE ----------------

                answer = response.text

                if not answer:
                    answer = (
                        "I could not generate a response. "
                        "Please try again."
                    )

                st.markdown(answer)

                # ---------------- TOKEN USAGE ----------------

                usage = response.usage_metadata

                if usage:

                    input_tokens = usage.prompt_token_count or 0
                    output_tokens = usage.candidates_token_count or 0
                    total_tokens = usage.total_token_count or 0

                    st.caption(
                        f"📊 Tokens — "
                        f"Input: {input_tokens} | "
                        f"Output: {output_tokens} | "
                        f"Total: {total_tokens}"
                    )

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    # ---------------- ERROR HANDLING ----------------

    except Exception as error:

        st.error(
            "⚠️ Gemini is temporarily unavailable. "
            "Please try again in a few seconds."
        )

        st.caption(
            "Technical details: " + str(error)
        )