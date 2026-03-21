# 🍳 AI Cooking Assistant

An intelligent multilingual cooking assistant powered by **Groq AI (Llama 3.3)** and built with **Streamlit**. Ask anything about cooking in your own language — recipes, techniques, substitutions & more!

---

## 🌐 Live Demo
👉 https://cooking-assistant-tprgtyk486t7cnz9evcpxu.streamlit.app/

## ✨ Features

### 🤖 AI Powered
- Instant answers to any cooking question
- Step-by-step recipes with ingredients & instructions
- Ingredient substitution suggestions
- Cooking techniques explained for all skill levels
- Sarcastic responses for non-cooking questions 😄

### 🌍 Multilingual Support
- English
- Telugu (తెలుగు)
- Hindi (हिंदी)
- Tamil (தமிழ்)
- French (Français)
- Spanish (Español)
- Full UI translation in selected language

### 🎯 Personalization
- Cuisine filter — Indian, Italian, Mexican, Chinese & more
- Diet filter — Vegetarian, Vegan, Keto, Gluten-Free & more
- Cooking time filter — Under 15 mins to 1+ hour
- Skill level — Beginner to Professional

### 💬 Chat Features
- Persistent chat history within session
- New Chat button to start fresh
- Quick prompt buttons for common questions
- Random Recipe generator based on preferences

### 📊 Analytics
- Every user question logged to Google Sheets
- Timestamp, language, question, cuisine & diet tracked
- Real-time monitoring of user activity

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Streamlit | Frontend UI |
| Groq API (Llama 3.3 70B) | AI responses |
| Python | Backend logic |
| Google Sheets API | User query logging |
| gspread | Google Sheets integration |
| python-dotenv | Environment variables |

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/R-Yashwanth/cooking-assistant.git
cd cooking-assistant
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API keys
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Add Google credentials
Place your `credentials.json` file in the root folder.

### 6. Run the app
```bash
streamlit run app/main.py
```

---

## 📁 Project Structure
```
cooking-assistant/
├── app/
│   └── main.py                 ← Main Streamlit UI
├── utils/
│   ├── __init__.py
│   ├── openai_helper.py        ← Groq AI API calls
│   ├── history.py              ← Chat history management
│   └── logger.py               ← Google Sheets logging
├── .streamlit/
│   └── config.toml             ← App theme & settings
├── .env                        ← API keys (never commit!)
├── credentials.json            ← Google credentials (never commit!)
├── requirements.txt
└── README.md
```

---

## 🔑 Get Free API Keys

### Groq API (Free)
1. Go to https://console.groq.com
2. Sign up for free
3. Create an API key
4. No credit card needed!

### Google Sheets API (Free)
1. Go to https://console.cloud.google.com
2. Create a project
3. Enable Google Sheets API & Google Drive API
4. Create a Service Account
5. Download JSON credentials

---

## 🌟 How It Works
```
User selects language & preferences
        ↓
User types a cooking question
        ↓
Groq AI (Llama 3.3) processes the question
        ↓
Response generated in selected language
        ↓
Question & response logged to Google Sheets
        ↓
User sees the answer in the chat
```

---

## 📊 Analytics Dashboard
Every user interaction is automatically logged to Google Sheets with:
- ⏰ Timestamp
- 🌍 Language used
- ❓ Question asked
- 🍽️ Cuisine preference
- 🥗 Diet preference
- 💬 AI Response

---

## 👨‍💻 Author
**Yashwanth R**
- GitHub: [@R-Yashwanth](https://github.com/R-Yashwanth)

---

## 🚀 Deployment
This app is deployed for free on **Streamlit Cloud**.
- Auto-deploys on every GitHub push
- Secrets managed via Streamlit Cloud secrets
- No server management needed

---

⭐ If you found this useful, please give it a star on GitHub!
