import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖"
)

st.title("🤖 AI Chat Assistant")
st.caption("Gemini LLM Chat Application")

# Get API key from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    system_prompt = st.text_area(
        "Custom Instructions",
        value="You are a helpful AI assistant.",
        height=120
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
        500,
        100
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
user_input = st.chat_input("Type your message...")


if user_input:

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Build conversation
    conversation = []

    conversation.append({
        "role": "user",
        "parts": [
            {
                "text": (
                    f"System instructions: {system_prompt}\n\n"
                    "User conversation:\n"
                )
            }
        ]
    })

    for message in st.session_state.messages:
        conversation.append({
            "role": message["role"],
            "parts": [
                {
                    "text": message["content"]
                }
            ]
        })

    try:

        with st.chat_message("assistant"):

            with st.spinner("Gemini is thinking..."):

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=conversation,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )

                answer = response.text

                st.markdown(answer)

        # Save AI response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:

        st.error(
            "Something went wrong. "
            "Please check your API key and try again."
        )