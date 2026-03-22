import sys
import os
import streamlit as st
import pycountry
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openai_helper import (
    get_cooking_response,
    get_recipe_suggestion,
    get_popular_dishes,
    get_country_languages,
    get_country_states,
    batch_translate_ui,
)
from utils.logger import log_question
from deep_translator import GoogleTranslator

# ─── All UI texts to translate ────────────────────────────────────────────────
UI_TEXTS = [
    "State / Region",
    "Settings",
    "Diet",
    "Cooking Time",
    "Skill Level",
    "Quick Prompts",
    "New Chat",
    "Previous Chats",
    "Popular Dishes",
    "Famous dishes from",
    "Click a dish to get its recipe!",
    "Chat with your Cooking Assistant",
    "Random Recipe",
    "From",
    "Surprise Me!",
    "Tips",
    "You",
    "Chef AI is thinking...",
    "Finding a recipe...",
    "Ask me anything about cooking!",
    "Ask me anything about cooking...",
    "No Restriction",
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Keto",
    "Low-Calorie",
    "Any",
    "Under 15 mins",
    "Under 30 mins",
    "Under 1 hour",
    "More than 1 hour",
    "Beginner",
    "Intermediate",
    "Advanced",
    "Professional",
    "Always taste as you cook",
    "Sharp knives are safer",
    "Let meat rest before cutting",
    "Mise en place — prep first!",
    "Salt your pasta water well",
    "AI Cooking Assistant",
    "Country",
    "Language",
]

# ─── All Countries from pycountry ────────────────────────────────────────────
@st.cache_data
def get_all_countries():
    countries = [c.name for c in sorted(pycountry.countries, key=lambda x: x.name)]
    return ["Any"] + countries

# ─── All Languages from deep_translator ──────────────────────────────────────
@st.cache_data
def get_all_languages():
    try:
        langs = GoogleTranslator.get_supported_languages(as_dict=True)
        return {lang.title(): code for lang, code in langs.items()}
    except Exception:
        return {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "French": "fr", "Spanish": "es"}

# ─── Get all translations in ONE Groq API call ────────────────────────────────
@st.cache_data
def get_translations(lang_code: str, language_name: str) -> dict:
    """
    Translate ALL UI texts in a single Groq API call.
    Cached per language — runs only once per language ever.
    Returns English dict if lang is English.
    """
    if lang_code == "en":
        return {t: t for t in UI_TEXTS}
    return batch_translate_ui(UI_TEXTS, language_name)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Cooking Assistant",
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

# ─── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []
if "suggested_dishes" not in st.session_state:
    st.session_state.suggested_dishes = []
if "off_topic_count" not in st.session_state:
    st.session_state.off_topic_count = 0

ALL_COUNTRIES = get_all_countries()
ALL_LANGUAGES = get_all_languages()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── 1. Country ────────────────────────────────────────────────────────────
    st.markdown("### 🌍 Country")
    selected_country = st.selectbox("country", ALL_COUNTRIES, label_visibility="collapsed")
    country_name = selected_country

    # ── 2. Language ───────────────────────────────────────────────────────────
    # When Any → show ALL languages, else AI generates for country
    if selected_country == "Any":
        lang_options = ALL_LANGUAGES  # All 100+ languages
    else:
        lang_cache_key = f"langs_{selected_country}"
        if lang_cache_key not in st.session_state:
            with st.spinner("Loading languages..."):
                st.session_state[lang_cache_key] = get_country_languages(country_name)
        country_langs = st.session_state[lang_cache_key]
        lang_options = {}
        for lang in country_langs:
            code = ALL_LANGUAGES.get(lang, "en")
            lang_options[lang] = code
        if "English" not in lang_options:
            lang_options["English"] = "en"

    st.markdown("### 🌐 Language")
    lang_list = list(lang_options.keys())
    default_idx = lang_list.index("English") if "English" in lang_list else 0
    selected_language = st.selectbox("language", lang_list, index=default_idx, label_visibility="collapsed")
    lang_code = lang_options[selected_language]

    # ── Load ALL translations in ONE call (cached) ────────────────────────────
    with st.spinner(f"Loading {selected_language} translations..." if lang_code != "en" else ""):
        translations = get_translations(lang_code, selected_language)

    def T(text: str) -> str:
        """Get translated text from cache."""
        return translations.get(text, text)

    # ── 3. State ──────────────────────────────────────────────────────────────
    # When Any → hide state dropdown completely
    if selected_country == "Any":
        selected_state = "Any"
    else:
        states_cache_key = f"states_{selected_country}"
        if states_cache_key not in st.session_state:
            with st.spinner("Loading regions..."):
                st.session_state[states_cache_key] = get_country_states(country_name)
        states = st.session_state.get(states_cache_key) or ["Any"]

        st.markdown(f"### 🗺️ {T('State / Region')}")
        selected_state = st.selectbox("state", states, label_visibility="collapsed")

    # ── 4. Popular Dishes ─────────────────────────────────────────────────────
    dishes_cache_key = f"dishes_{selected_country}_{selected_state}"
    if dishes_cache_key not in st.session_state:
        with st.spinner("Loading popular dishes..."):
            st.session_state[dishes_cache_key] = get_popular_dishes(country_name, selected_state)
    popular_dishes = st.session_state.get(dishes_cache_key) or []

    location_name = f"{selected_state}, {country_name}" if selected_state != "Any" else country_name

    if popular_dishes:
        st.markdown(f"### 🍽️ {T('Popular Dishes')}")
        st.caption(f"📍 {T('Famous dishes from')} {location_name}")
        cols = st.columns(2)
        for idx, dish in enumerate(popular_dishes):
            with cols[idx % 2]:
                if st.button(dish, key=f"dish_{idx}", use_container_width=True):
                    st.session_state["quick_prompt"] = f"Give me the complete recipe for {dish} with ingredients and step by step instructions"
        st.caption(T("Click a dish to get its recipe!"))

    st.divider()

    # ── 5. Settings ───────────────────────────────────────────────────────────
    st.markdown(f"### ⚙️ {T('Settings')}")

    diet = st.selectbox(
        f"🥗 {T('Diet')}",
        [T(x) for x in ["No Restriction", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Low-Calorie"]]
    )
    cook_time = st.selectbox(
        f"⏱️ {T('Cooking Time')}",
        [T(x) for x in ["Any", "Under 15 mins", "Under 30 mins", "Under 1 hour", "More than 1 hour"]]
    )
    skill = st.selectbox(
        f"👨‍🍳 {T('Skill Level')}",
        [T(x) for x in ["Beginner", "Intermediate", "Advanced", "Professional"]]
    )

    st.divider()

    # ── 6. Quick Prompts ──────────────────────────────────────────────────────
    st.markdown(f"### 💡 {T('Quick Prompts')}")

    if popular_dishes and selected_state != "Any":
        dynamic_prompts = [
            f"How do I make {popular_dishes[0]}?",
            f"Give me an authentic {popular_dishes[1]} recipe" if len(popular_dishes) > 1 else "Give me a quick recipe",
            f"What are the key ingredients in {popular_dishes[2]}?" if len(popular_dishes) > 2 else "What spices are used?",
            f"How do I make {popular_dishes[3]} at home?" if len(popular_dishes) > 3 else "What is a popular technique?",
            f"What makes {selected_state} cuisine unique?",
        ]
    elif popular_dishes:
        dynamic_prompts = [
            f"How do I make {popular_dishes[0]}?",
            f"Give me a famous {country_name} recipe",
            f"What are the most popular {country_name} dishes?",
            "How do I make fluffy scrambled eggs?",
            "How do I chop onions without crying?",
        ]
    else:
        dynamic_prompts = [
            "How do I make fluffy scrambled eggs?",
            "Give me a quick pasta recipe",
            "What can I cook with chicken and rice?",
            "How do I bake a simple chocolate cake?",
            "How do I chop onions without crying?",
        ]

    # Translate prompts using Groq in one batch
    @st.cache_data
    def translate_prompts(prompts: tuple, lang_name: str, lcode: str) -> tuple:
        if lcode == "en":
            return prompts
        from utils.openai_helper import batch_translate_ui
        result = batch_translate_ui(list(prompts), lang_name)
        return tuple(result.get(p, p) for p in prompts)

    translated_prompts = translate_prompts(tuple(dynamic_prompts), selected_language, lang_code)

    for i, (original, translated) in enumerate(zip(dynamic_prompts, translated_prompts)):
        if st.button(translated, key=f"qp_{i}", use_container_width=True):
            st.session_state["quick_prompt"] = original

    st.divider()

    # ── 7. New Chat + Previous Chats ──────────────────────────────────────────
    if st.button(f"➕ {T('New Chat')}", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.suggested_dishes = []
        st.session_state.off_topic_count = 0
        st.rerun()

    if st.session_state.saved_chats:
        st.markdown(f"### 💬 {T('Previous Chats')}")
        for i, chat in enumerate(reversed(st.session_state.saved_chats)):
            if st.button(f"🗨️ {chat['title']}", use_container_width=True, key=f"chat_{i}"):
                st.session_state.messages = chat["messages"]
                st.session_state.chat_history = chat["history"]
                st.rerun()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>🍳 {T('AI Cooking Assistant')}</h1>
    <p>📍 {location_name} | {T('Ask me anything about cooking!')}</p>
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### 💬 {T('Chat with your Cooking Assistant')}")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-message-user">👤 <strong>{T("You")}:</strong> {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-message-ai">🍳 <strong>Chef AI:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )

    if "quick_prompt" in st.session_state:
        user_input = st.session_state.pop("quick_prompt")
    else:
        user_input = None

    user_question = st.chat_input(T("Ask me anything about cooking..."))

    if user_question or user_input:
        question = user_question or user_input

        if len(st.session_state.messages) == 0:
            chat_title = question[:30] + "..." if len(question) > 30 else question
            st.session_state.saved_chats.append({
                "title": chat_title,
                "messages": [],
                "history": []
            })

        st.session_state.messages.append({"role": "user", "content": question})

        context = (
            f"Country: {country_name}, "
            f"State/Region: {selected_state}, "
            f"Diet: {diet}, "
            f"Cooking Time: {cook_time}, "
            f"Skill Level: {skill}. "
            f"IMPORTANT: Respond only in {selected_language} language. "
            f"If relevant, focus on authentic {location_name} cuisine and cooking methods. "
            f"OFF_TOPIC_COUNT: {st.session_state.off_topic_count}"
        )

        with st.spinner(T("Chef AI is thinking...")):
            response = get_cooking_response(
                question=question,
                chat_history=st.session_state.chat_history,
                preferences=context
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append({"role": "user", "content": question})
        # Detect off-topic BEFORE calling AI
        # If question has NO cooking words = off topic, increment counter
        # If question HAS cooking words = reset counter to 0
        cooking_keywords = [
            "recipe", "cook", "food", "dish", "ingredient", "kitchen", "bake",
            "fry", "boil", "grill", "spice", "meal", "eat", "taste", "flavor",
            "cuisine", "chef", "oven", "pan", "pot", "knife", "vegetable",
            "fruit", "meat", "chicken", "fish", "rice", "bread", "curry",
            "soup", "salad", "dessert", "breakfast", "lunch", "dinner", "snack",
            "biryani", "pasta", "pizza", "burger", "noodle", "roti", "dosa",
            "idli", "samosa", "sushi", "taco", "sandwich", "cake", "sweet",
            "how do i make", "how to make", "how to cook", "what can i cook",
            "substitute", "replace", "instead of", "without", "calories",
            "nutrition", "protein", "healthy", "diet", "weight", "boil",
            "steam", "roast", "marinate", "sauce", "gravy", "masala", "spicy",
            "restaurant", "chop", "slice", "dice", "mince", "blend", "mix"
        ]
        is_cooking = any(kw.lower() in question.lower() for kw in cooking_keywords)
        if is_cooking:
            st.session_state.off_topic_count = 0  # Reset when cooking question asked
        else:
            st.session_state.off_topic_count += 1  # Increment for ANY non-cooking question
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        log_question(question, response, selected_language, country_name, selected_state)
        st.rerun()

with col2:
    st.markdown(f"### 🎲 {T('Random Recipe')}")
    st.caption(f"📍 {T('From')} {location_name}")
    if st.button(f"🎉 {T('Surprise Me!')}", use_container_width=True):
        with st.spinner(T("Finding a recipe...")):
            already_suggested = ", ".join(st.session_state.suggested_dishes) if st.session_state.suggested_dishes else "none"
            suggestion = get_recipe_suggestion(
                cuisine=f"{country_name} - {selected_state}" if selected_state != "Any" else country_name,
                diet=diet,
                cook_time=cook_time,
                language=selected_language,
                already_suggested=already_suggested
            )
        dish_name = suggestion.split("\n")[0].strip()
        st.session_state.suggested_dishes.append(dish_name)
        st.info(suggestion)
        st.caption(f"🎯 {len(st.session_state.suggested_dishes)} unique dishes suggested this session")

    st.markdown(f"### 📌 {T('Tips')}")
    for tip in [
        "Always taste as you cook",
        "Sharp knives are safer",
        "Let meat rest before cutting",
        "Mise en place — prep first!",
        "Salt your pasta water well",
    ]:
        st.markdown(f"- {T(tip)}")
