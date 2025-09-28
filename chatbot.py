import streamlit as st
import ollama

st.set_page_config(page_title="Simple Local Chaty", layout="wide")
st.title("Chat with Ollama")

# --- Session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful and concise assistant."}
    ]

if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = "gemma3:4b"

# Sidebar with model selection
with st.sidebar:
    st.header("Model Selection")
    try:
        # List all pulled models
        models = ollama.list()

        model_names = []
        for m in models['models']:
            if isinstance(m['model'], str):
                model_names.append(m['model'])
        if not model_names:
            model_names = ["(no models found)"]
        st.session_state["ollama_model"] = st.selectbox(
            "Choose Model", model_names,
            index=max(0, model_names.index(st.session_state["ollama_model"]))
                  if st.session_state["ollama_model"] in model_names else 0
        )
    except Exception as e:
        st.error("Could not reach Ollama server. Make sure `ollama serve` is running.")
        st.caption(f"Error: {e}")

# Render chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message…"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant reply (with streaming)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        assistant_text = ""

        try:
            stream = ollama.chat(
                model=st.session_state["ollama_model"],
                messages=st.session_state["messages"],
                stream=True,
            )

            for chunk in stream:
                delta = chunk.get("message", {}).get("content", "")
                assistant_text += delta
                placeholder.markdown(assistant_text)

        except Exception as e:
            placeholder.markdown(f"**Error from Ollama:** {e}")
            assistant_text = f"Error: {e}"

    st.session_state["messages"].append({"role": "assistant", "content": assistant_text})
