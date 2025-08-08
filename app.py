import streamlit as st 
import requests
from transformers import pipeline
import json

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MCP_SERVER_URL = "http://mcp-server:8080/mcp"

INTENTS = {
    "system_usage": "Ask for system informations",
    "general_question": "Ask a general question",
    "chitchat": "Casual small talk",
}

@st.cache_resource
def load_classifier():
    model_path = "/app/model"
    classifier = pipeline(
        "zero-shot-classification",
        model=model_path,
        tokenizer=model_path,
        local_files_only=True
    )
    return classifier

classifier = load_classifier()

def classify_intent(text: str) -> str:
    result = classifier(text, list(INTENTS.values()))
    return result['labels'][0]

def query_mcp_agent(host, username, password):
    payload = {
        "host": host,
        "username": username,
        "password": password,
        "command": "system_info"  
    }
    try:
        response = requests.post(MCP_SERVER_URL, json=payload)
        response.raise_for_status()
        return response.json().get("result", "No result from MCP.")
    except Exception as e:
        return f"[SSH Error] {e}"

def generate_response(prompt: str, history: list, max_turns: int = 4) -> str:
    trimmed = history[-max_turns*2:]
    chat_context = ""
    for msg in trimmed:
        role = msg["role"]
        content = msg["content"]
        chat_context += f"{'User' if role == 'user' else 'Assistant'}: {content}\n"
    chat_context += f"User: {prompt}\nAssistant:"

    payload = {
        "model": "llama3.2:1b",
        "prompt": chat_context,
        "stream": True
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        full_response = ""
        for chunk in response.iter_lines(decode_unicode=True):
            if chunk:
                data = json.loads(chunk)
                full_response += data.get("response", "")
                if data.get("done", False):
                    break
        return full_response if full_response else "[Error: Empty response from model.]"
    except Exception as e:
        return f"[Error contacting LLaMA model: {e}]"

st.title("🤖 Offline Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

if "awaiting_system_name" not in st.session_state:
    st.session_state.awaiting_system_name = False

if "awaiting_credentials" not in st.session_state:
    st.session_state.awaiting_credentials = False

if "system_name" not in st.session_state:
    st.session_state.system_name = None

if "credentials" not in st.session_state:
    st.session_state.credentials = {"host": None, "username": None, "password": None}

def reset_context():
    st.session_state.awaiting_system_name = False
    st.session_state.awaiting_credentials = False
    st.session_state.system_name = None
    st.session_state.credentials = {"host": None, "username": None, "password": None}

if st.button("Clear chat"):
    st.session_state.history = []
    reset_context()
    st.success("Chat history cleared.")

if st.session_state.awaiting_credentials:
    with st.form("ssh_form"):
        st.markdown(f"🔐 Please enter SSH credentials for `{st.session_state.system_name}`")
        host = st.text_input("Host")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Connect")

    if submitted:
        if not all([host, username, password]):
            st.warning("❗ Please fill in all fields.")
        else:
            st.session_state.credentials = {"host": host, "username": username, "password": password}
            result = query_mcp_agent(host, username, password)
            if "[SSH Error]" in result:
                st.session_state.history.append({
                    "role": "assistant",
                    "content": f"❗ Connection failed: {result}"
                })
            else:
                st.session_state.history.append({
                    "role": "assistant",
                    "content": result
                })
                reset_context()
            st.rerun()

if not st.session_state.awaiting_credentials:
    user_input = st.chat_input("Send a message...", key="main_input")
    if user_input:
        if st.session_state.awaiting_system_name:
            st.session_state.system_name = user_input.strip()
            st.session_state.awaiting_system_name = False
            st.session_state.awaiting_credentials = True
            st.rerun()
        else:
            st.session_state.history.append({"role": "user", "content": user_input})
            intent = classify_intent(user_input)

            if intent == INTENTS["system_usage"]:
                if st.session_state.system_name:
                    st.session_state.awaiting_credentials = True
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": f"Please enter SSH credentials for `{st.session_state.system_name}` below."
                    })
                    st.experimental_rerun()
                else:
                    st.session_state.awaiting_system_name = True
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": "Which system/server do you want the system information for? Please type the system name."
                    })
            else:
                response = generate_response(user_input, st.session_state.history)
                st.session_state.history.append({"role": "assistant", "content": response})

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])