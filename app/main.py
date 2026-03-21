import sys
import os
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openai_helper import get_cooking_response, get_recipe_suggestion
from utils.history import save_message, get_history, clear_history
from utils.logger import log_question

# ─── Language Config ─────────────────────────────────────────────────────────
LANGUAGES = {
    "English": {
        "title": "AI Cooking Assistant",
        "subtitle": "Ask me anything about cooking — recipes, techniques, substitutions & more!",
        "settings": "Settings",
        "cuisine": "Cuisine",
        "diet": "Diet",
        "cook_time": "Cooking Time",
        "skill": "Skill Level",
        "quick_prompts": "Quick Prompts",
        "new_chat": "New Chat",
        "chat_title": "Chat with your Cooking Assistant",
        "chat_placeholder": "Ask me anything about cooking...",
        "random_recipe": "Random Recipe",
        "surprise": "Surprise Me!",
        "tips": "Tips",
        "language": "Language",
        "previous_chats": "Previous Chats",
        "thinking": "Chef AI is thinking...",
        "finding": "Finding a recipe...",
        "you": "You",
        "chef": "Chef AI",
        "prompts": [
            "How do I make fluffy scrambled eggs?",
            "Give me a quick pasta recipe",
            "What can I cook with chicken and rice?",
            "How do I bake a simple chocolate cake?",
            "How do I chop onions without crying?",
        ],
        "tips_list": [
            "Always taste as you cook",
            "Sharp knives are safer",
            "Let meat rest before cutting",
            "Mise en place — prep first!",
            "Salt your pasta water well",
        ]
    },
    "Telugu": {
        "title": "AI వంట సహాయకుడు",
        "subtitle": "వంట గురించి ఏదైనా అడగండి!",
        "settings": "సెట్టింగ్లు",
        "cuisine": "వంట శైలి",
        "diet": "ఆహార నియమం",
        "cook_time": "వంట సమయం",
        "skill": "నైపుణ్య స్థాయి",
        "quick_prompts": "త్వరిత ప్రశ్నలు",
        "new_chat": "కొత్త చాట్",
        "chat_title": "వంట సహాయకుడితో చాట్",
        "chat_placeholder": "వంట గురించి ఏదైనా అడగండి...",
        "random_recipe": "యాదృచ్ఛిక రెసిపీ",
        "surprise": "ఆశ్చర్యపరచండి!",
        "tips": "చిట్కాలు",
        "language": "భాష",
        "previous_chats": "మునుపటి చాట్లు",
        "thinking": "Chef AI ఆలోచిస్తోంది...",
        "finding": "రెసిపీ వెతుకుతోంది...",
        "you": "మీరు",
        "chef": "Chef AI",
        "prompts": [
            "మెత్తని స్క్రాంబుల్డ్ గుడ్లు ఎలా చేయాలి?",
            "త్వరిత పాస్తా రెసిపీ ఇవ్వండి",
            "చికెన్ మరియు అన్నంతో ఏమి వండవచ్చు?",
            "సాధారణ చాకొలేట్ కేక్ ఎలా చేయాలి?",
            "ఉల్లిపాయలు కన్నీళ్లు లేకుండా ఎలా కోయాలి?",
        ],
        "tips_list": [
            "వంట చేస్తున్నప్పుడు రుచి చూడండి",
            "పదునైన కత్తులు సురక్షితమైనవి",
            "మాంసం కోయడానికి ముందు విశ్రాంతి ఇవ్వండి",
            "ముందే సిద్ధం చేయండి!",
            "పాస్తా నీటిలో బాగా ఉప్పు వేయండి",
        ]
    },
    "Hindi": {
        "title": "AI खाना पकाने का सहायक",
        "subtitle": "खाना पकाने के बारे में कुछ भी पूछें!",
        "settings": "सेटिंग्स",
        "cuisine": "व्यंजन",
        "diet": "आहार",
        "cook_time": "खाना पकाने का समय",
        "skill": "कौशल स्तर",
        "quick_prompts": "त्वरित प्रश्न",
        "new_chat": "नई चैट",
        "chat_title": "खाना पकाने के सहायक से चैट करें",
        "chat_placeholder": "खाना पकाने के बारे में कुछ भी पूछें...",
        "random_recipe": "यादृच्छिक रेसिपी",
        "surprise": "मुझे आश्चर्यचकित करें!",
        "tips": "सुझाव",
        "language": "भाषा",
        "previous_chats": "पिछली चैट",
        "thinking": "Chef AI सोच रहा है...",
        "finding": "रेसिपी ढूंढ रहा है...",
        "you": "आप",
        "chef": "Chef AI",
        "prompts": [
            "फूली हुई स्क्रैम्बल्ड एग्स कैसे बनाएं?",
            "जल्दी पास्ता रेसिपी दें",
            "चिकन और चावल से क्या बना सकते हैं?",
            "साधारण चॉकलेट केक कैसे बनाएं?",
            "प्याज बिना आंसू के कैसे काटें?",
        ],
        "tips_list": [
            "खाना पकाते समय चखते रहें",
            "तेज चाकू सुरक्षित होते हैं",
            "काटने से पहले मांस को आराम दें",
            "पहले से तैयारी करें!",
            "पास्ता के पानी में अच्छे से नमक डालें",
        ]
    },
    "Tamil": {
        "title": "AI சமையல் உதவியாளர்",
        "subtitle": "சமையலைப் பற்றி எதையும் கேளுங்கள்!",
        "settings": "அமைப்புகள்",
        "cuisine": "உணவு வகை",
        "diet": "உணவு முறை",
        "cook_time": "சமையல் நேரம்",
        "skill": "திறன் நிலை",
        "quick_prompts": "விரைவு கேள்விகள்",
        "new_chat": "புதிய அரட்டை",
        "chat_title": "சமையல் உதவியாளருடன் அரட்டை",
        "chat_placeholder": "சமையலைப் பற்றி கேளுங்கள்...",
        "random_recipe": "சீரற்ற சமையல்",
        "surprise": "என்னை ஆச்சரியப்படுத்து!",
        "tips": "குறிப்புகள்",
        "language": "மொழி",
        "previous_chats": "முந்தைய அரட்டைகள்",
        "thinking": "Chef AI யோசிக்கிறது...",
        "finding": "சமையல் தேடுகிறது...",
        "you": "நீங்கள்",
        "chef": "Chef AI",
        "prompts": [
            "பஞ்சுபோன் scrambled eggs எப்படி செய்வது?",
            "விரைவான pasta recipe கொடுங்கள்",
            "கோழி மற்றும் சோறு வைத்து என்ன சமைக்கலாம்?",
            "எளிய சாக்லேட் கேக் எப்படி செய்வது?",
            "வெங்காயம் கண்ணீர் இல்லாமல் எப்படி நறுக்குவது?",
        ],
        "tips_list": [
            "சமைக்கும்போது சுவை பாருங்கள்",
            "கூர்மையான கத்திகள் பாதுகாப்பானவை",
            "இறைச்சியை வெட்டுவதற்கு முன் ஓய்வு கொடுங்கள்",
            "முன்கூட்டியே தயாரிக்கவும்!",
            "பாஸ்தா தண்ணீரில் நன்றாக உப்பு போடுங்கள்",
        ]
    },
    "French": {
        "title": "Assistant Culinaire IA",
        "subtitle": "Posez-moi des questions sur la cuisine!",
        "settings": "Parametres",
        "cuisine": "Cuisine",
        "diet": "Regime",
        "cook_time": "Temps de cuisson",
        "skill": "Niveau de competence",
        "quick_prompts": "Questions rapides",
        "new_chat": "Nouveau chat",
        "chat_title": "Chattez avec votre assistant culinaire",
        "chat_placeholder": "Posez des questions sur la cuisine...",
        "random_recipe": "Recette aleatoire",
        "surprise": "Surprenez-moi!",
        "tips": "Conseils",
        "language": "Langue",
        "previous_chats": "Chats precedents",
        "thinking": "Chef AI reflechit...",
        "finding": "Recherche d'une recette...",
        "you": "Vous",
        "chef": "Chef AI",
        "prompts": [
            "Comment faire des oeufs brouilles moelleux?",
            "Donnez-moi une recette de pates rapide",
            "Que cuisiner avec du poulet et du riz?",
            "Comment faire un gateau au chocolat simple?",
            "Comment couper des oignons sans pleurer?",
        ],
        "tips_list": [
            "Goutez toujours en cuisinant",
            "Les couteaux tranchants sont plus surs",
            "Laissez reposer la viande avant de couper",
            "Mise en place - preparez d'abord!",
            "Salez bien l'eau des pates",
        ]
    },
    "Spanish": {
        "title": "Asistente de Cocina IA",
        "subtitle": "Preguntame cualquier cosa sobre cocina!",
        "settings": "Configuracion",
        "cuisine": "Cocina",
        "diet": "Dieta",
        "cook_time": "Tiempo de coccion",
        "skill": "Nivel de habilidad",
        "quick_prompts": "Preguntas rapidas",
        "new_chat": "Nuevo chat",
        "chat_title": "Chatea con tu asistente de cocina",
        "chat_placeholder": "Pregunta sobre cocina...",
        "random_recipe": "Receta aleatoria",
        "surprise": "Sorprendeme!",
        "tips": "Consejos",
        "language": "Idioma",
        "previous_chats": "Chats anteriores",
        "thinking": "Chef AI esta pensando...",
        "finding": "Buscando una receta...",
        "you": "Tu",
        "chef": "Chef AI",
        "prompts": [
            "Como hacer huevos revueltos esponjosos?",
            "Dame una receta rapida de pasta",
            "Que puedo cocinar con pollo y arroz?",
            "Como hacer un pastel de chocolate simple?",
            "Como cortar cebollas sin llorar?",
        ],
        "tips_list": [
            "Siempre prueba mientras cocinas",
            "Los cuchillos afilados son mas seguros",
            "Deja reposar la carne antes de cortar",
            "Mise en place - prepara primero!",
            "Sala bien el agua de la pasta",
        ]
    }
}

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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []

with st.sidebar:
    st.title("🌐 Language")
    selected_language = st.selectbox("", list(LANGUAGES.keys()))
    L = LANGUAGES[selected_language]

    st.divider()
    st.title(f"⚙️ {L['settings']}")
    cuisine = st.selectbox(f"🌍 {L['cuisine']}", ["Any", "Indian", "Italian", "Mexican", "Chinese", "Continental", "Japanese", "Mediterranean"])
    diet = st.selectbox(f"🥗 {L['diet']}", ["No Restriction", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Low-Calorie"])
    cook_time = st.selectbox(f"⏱️ {L['cook_time']}", ["Any", "Under 15 mins", "Under 30 mins", "Under 1 hour", "More than 1 hour"])
    skill = st.selectbox(f"👨‍🍳 {L['skill']}", ["Beginner", "Intermediate", "Advanced", "Professional"])

    st.divider()
    st.markdown(f"### 💡 {L['quick_prompts']}")
    for prompt in L["prompts"]:
        if st.button(prompt, use_container_width=True):
            st.session_state["quick_prompt"] = prompt

    st.divider()
    if st.button(f"➕ {L['new_chat']}", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

    if st.session_state.saved_chats:
        st.markdown(f"### 💬 {L['previous_chats']}")
        for i, chat in enumerate(reversed(st.session_state.saved_chats)):
            if st.button(f"🗨️ {chat['title']}", use_container_width=True, key=f"chat_{i}"):
                st.session_state.messages = chat["messages"]
                st.session_state.chat_history = chat["history"]
                st.rerun()

st.markdown(f"""
<div class="main-header">
    <h1>🍳 {L['title']}</h1>
    <p>{L['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### 💬 {L['chat_title']}")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message-user">👤 <strong>{L["you"]}:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-ai">🍳 <strong>{L["chef"]}:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

    if "quick_prompt" in st.session_state:
        user_input = st.session_state.pop("quick_prompt")
    else:
        user_input = None

    user_question = st.chat_input(L["chat_placeholder"])

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
        context = f"Cuisine: {cuisine}, Diet: {diet}, Cooking Time: {cook_time}, Skill Level: {skill}. IMPORTANT: Respond only in {selected_language} language."

        with st.spinner(L["thinking"]):
            response = get_cooking_response(
                question=question,
                chat_history=st.session_state.chat_history,
                preferences=context
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        log_question(question, response, selected_language, cuisine, diet)
        st.rerun()

with col2:
    st.markdown(f"### 🎲 {L['random_recipe']}")
    if st.button(f"{L['surprise']} 🎉", use_container_width=True):
        with st.spinner(L["finding"]):
            suggestion = get_recipe_suggestion(cuisine=cuisine, diet=diet, cook_time=cook_time, language=selected_language)
        st.info(suggestion)

    st.markdown(f"### 📌 {L['tips']}")
    for tip in L["tips_list"]:
        st.markdown(f"- {tip}")