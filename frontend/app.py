import streamlit as st
import requests
import os
import uuid
import json
from datetime import datetime

# Configuration: Pointing to n8n's local Production Webhooks
N8N_WEBHOOK_INGEST = os.getenv("N8N_WEBHOOK_INGEST", "http://localhost:5678/webhook/ingest")
N8N_WEBHOOK_CHAT = os.getenv("N8N_WEBHOOK_CHAT", "http://localhost:5678/webhook/chat")

# Setup local storage for chat history
CHAT_DIR = os.path.join(os.path.dirname(__file__), "chats")
os.makedirs(CHAT_DIR, exist_ok=True)

# -----------------------------------------
# Page Configuration & Polished UI
# -----------------------------------------
st.set_page_config(
    page_title="Intelligent Document RAG", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner, modern app-like feel
st.markdown("""
    <style>
    /* Hide Streamlit default branding & the sidebar toggle arrows */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stSidebarCollapseButton"] {display: none;}
    
    /* Remove the entire sidebar header block that holds the arrow */
    [data-testid="stSidebarHeader"] {display: none !important;}
    
    /* Polished Headers */
    h1 {
        font-weight: 600 !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--secondary-background-color);
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--background-color);
        border-right: 1px solid var(--secondary-background-color);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------
# Chat History Helper Functions
# -----------------------------------------
def save_chat():
    """Saves the current session messages to a local JSON file."""
    if len(st.session_state.messages) > 1: # Only save if user actually typed something
        filepath = os.path.join(CHAT_DIR, f"{st.session_state.session_id}.json")
        
        # Derive a title from the first user message
        title = "New Chat"
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                title = msg["content"][:28] + "..." if len(msg["content"]) > 28 else msg["content"]
                break
                
        data = {
            "id": st.session_state.session_id,
            "title": title,
            "updated_at": datetime.now().isoformat(),
            "messages": st.session_state.messages
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

def load_chat(session_id):
    """Loads a specific chat session from JSON."""
    filepath = os.path.join(CHAT_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            st.session_state.session_id = data["id"]
            st.session_state.messages = data["messages"]
        st.rerun()

def get_chat_list():
    """Returns a sorted list of saved chats."""
    chats = []
    for filename in os.listdir(CHAT_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CHAT_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    chats.append({
                        "id": data["id"],
                        "title": data.get("title", "Saved Chat"),
                        "updated_at": data.get("updated_at", "")
                    })
            except:
                pass
    # Sort by newest first
    chats.sort(key=lambda x: x["updated_at"], reverse=True)
    return chats

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your intelligent document assistant. Upload a file on the left, and ask me anything about it!"}
    ]

# -----------------------------------------
# LEFT SIDEBAR: Document Upload & History
# -----------------------------------------
with st.sidebar:
    st.title("📚 Knowledge Base")
    st.markdown("Upload documents to train your assistant instantly.")
    
    uploaded_file = st.file_uploader("Select a PDF or TXT file", type=["pdf", "txt"], label_visibility="collapsed")
    
    if st.button("📤 Ingest Document", type="primary", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    files = {"data": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(N8N_WEBHOOK_INGEST, files=files)
                    if response.status_code == 200:
                        st.toast(f"✅ Successfully added {uploaded_file.name} to memory!", icon="🎉")
                    else:
                        st.error(f"Ingestion failed (Status: {response.status_code})")
                except Exception as e:
                    st.error(f"Network error: {e}")
        else:
            st.toast("⚠️ Please select a file first before clicking Ingest.", icon="⚠️")
    
    st.divider()
    
    # Custom Chat History Section
    st.caption("💬 **Chat History**")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your intelligent document assistant. Upload a file on the left, and ask me anything about it!"}
        ]
        st.rerun()
        
    st.write("") # Tiny spacer
    
    # Render the list of past chats
    past_chats = get_chat_list()
    for chat in past_chats:
        # Visually indicate the active chat
        is_active = (chat["id"] == st.session_state.session_id)
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(f"🗨️ {chat['title']}", key=chat["id"], type=btn_type, use_container_width=True):
            if not is_active:
                load_chat(chat["id"])

# -----------------------------------------
# MAIN AREA: Chat Interface
# -----------------------------------------
st.title("🧠 Intelligent Document Assistant")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to UI
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat() # Save immediately so the title updates in the sidebar

    # Process the Assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Searching documents..."):
            try:
                payload = {
                    "query": prompt,
                    "sessionId": st.session_state.session_id
                }
                response = requests.post(N8N_WEBHOOK_CHAT, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("output", data.get("text", str(data)))
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    save_chat() # Save final assistant response
                else:
                    st.error(f"Backend error: {response.status_code}. Make sure your n8n workflows are active.")
            except Exception as e:
                st.error(f"Could not reach n8n. Is Docker running? Error: {e}")