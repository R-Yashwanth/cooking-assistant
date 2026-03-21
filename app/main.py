import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from utils.openai_helper import get_cooking_response, get_recipe_suggestion
from utils.history import save_message, get_history, clear_history


st.set_page_config(
    page_title="🍳 AI Cooking Assistant",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .chat-message-user {
        background: #000000;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #4FC3F7;
        color: #FFFFFF;
    }
    .chat-message-ai {
        background: #000000;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #FF6B35;
        color: #FFFFFF;
    }
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("""
<div class="main-header">
    <h1>🍳 AI Cooking Assistant</h1>
    <p>Ask me anything about cooking — recipes, techniques, substitutions & more!</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    cuisine = st.selectbox("🌍 Cuisine", ["Any", "Indian", "Italian", "Mexican", "Chinese", "Continental", "Japanese", "Mediterranean"])
    diet = st.selectbox("🥗 Diet", ["No Restriction", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Low-Calorie"])
    cook_time = st.selectbox("⏱️ Cooking Time", ["Any", "Under 15 mins", "Under 30 mins", "Under 1 hour", "More than 1 hour"])
    skill = st.selectbox("👨‍🍳 Skill Level", ["Beginner", "Intermediate", "Advanced", "Professional"])

    st.divider()
    st.markdown("### 💡 Quick Prompts")
    quick_prompts = [
        "🍳 How do I make fluffy scrambled eggs?",
        "🍝 Give me a quick pasta recipe",
        "🥘 What can I cook with chicken and rice?",
        "🧁 How do I bake a simple chocolate cake?",
        "🔪 How do I chop onions without crying?",
    ]
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state["quick_prompt"] = prompt

    st.divider()
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.chat_title = f"Chat {len(st.session_state.get('saved_chats', [])) + 1}"
        if "saved_chats" not in st.session_state:
            st.session_state.saved_chats = []
        st.rerun()

    st.markdown("### 💬 Previous Chats")
    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = []

    for i, chat in enumerate(reversed(st.session_state.saved_chats)):
        if st.button(f"🗨️ {chat['title']}", use_container_width=True, key=f"chat_{i}"):
            st.session_state.messages = chat["messages"]
            st.session_state.chat_history = chat["history"]
            st.rerun()

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 💬 Chat with your Cooking Assistant")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message-user">👤 <strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-ai">🍳 <strong>Chef AI:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

    if "quick_prompt" in st.session_state:
        user_input = st.session_state.pop("quick_prompt")
    else:
        user_input = None

    user_question = st.chat_input("Ask me anything about cooking... e.g. 'How do I make biryani?'")

    if user_question or user_input:
        question = user_question or user_input

        # Save current chat before adding new message
        if "saved_chats" not in st.session_state:
            st.session_state.saved_chats = []
        if len(st.session_state.messages) == 0:
            chat_title = question[:30] + "..." if len(question) > 30 else question
            st.session_state.saved_chats.append({
                "title": chat_title,
                "messages": [],
                "history": []
            })

        st.session_state.messages.append({"role": "user", "content": question})
        context = f"Cuisine: {cuisine}, Diet: {diet}, Cooking Time: {cook_time}, Skill Level: {skill}"

        with st.spinner("🍳 Chef AI is thinking..."):
            response = get_cooking_response(
                question=question,
                chat_history=st.session_state.chat_history,
                preferences=context
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    st.markdown("### 🎲 Random Recipe")
    if st.button("Surprise Me! 🎉", use_container_width=True):
        with st.spinner("Finding a recipe..."):
            suggestion = get_recipe_suggestion(cuisine=cuisine, diet=diet, cook_time=cook_time)
        st.info(suggestion)

    st.markdown("### 📌 Tips")
    for tip in ["🧂 Always taste as you cook", "🔪 Sharp knives are safer", "🌡️ Let meat rest before cutting", "🧄 Mise en place — prep first!", "💧 Salt your pasta water well"]:
        st.markdown(f"- {tip}")