
    
        import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖"
)

st.title("🤖 AI Chat Assistant")
st.caption("Gemini LLM Chat Application")

# Get Gemini API key securely
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
        value="You are a helpful AI assistant.",
        height=120
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
        value=500,
        step=100
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------- USER INPUT ----------------

user_input = st.chat_input("Type your message...")

if user_input:

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Convert our history into Gemini format
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

    try:

        with st.chat_message("assistant"):

            with st.spinner("Gemini is thinking..."):

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )

                answer = response.text

                st.markdown(answer)

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:

        st.error(
            f"Gemini API error: {str(e)}"
        )