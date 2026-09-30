import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖"
)

st.title("🤖 AI Chat Assistant")
st.caption("LLM API Chat Application")

# Get API key securely from Streamlit Secrets
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key is not configured.")
    st.stop()

client = OpenAI(api_key=api_key)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    system_prompt = st.text_area(
        "Custom Instructions",
        value="You are a helpful AI assistant.",
        height=120
    )

    model = st.selectbox(
        "Model",
        ["gpt-5-mini"]
    )

    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        0.7,
        0.1
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat history
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

    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(st.session_state.messages)

    # Get AI response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )

                answer = response.choices[0].message.content

                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")