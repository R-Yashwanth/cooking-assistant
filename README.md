# 🍳 AI Cooking Assistant

An intelligent cooking assistant powered by **Groq AI (Llama 3)** and built with **Streamlit**.
Ask anything about cooking — recipes, techniques, substitutions & more!

---

## 🌐 Live Demo
👉 [Click here to try the app]https://cooking-assistant-tprgtyk486t7cnz9evcpxu.streamlit.app/)

---

## ✨ Features
- 💬 **Chat Interface** — Ask any cooking question and get instant answers
- 🎲 **Random Recipe Generator** — Get surprise recipes based on your preferences
- 🌍 **Cuisine Filter** — Indian, Italian, Mexican, Chinese & more
- 🥗 **Diet Filter** — Vegetarian, Vegan, Keto, Gluten-Free & more
- ⏱️ **Cooking Time Filter** — Under 15 mins to over 1 hour
- 👨‍🍳 **Skill Level** — Beginner to Professional
- 💡 **Quick Prompts** — One click to ask common cooking questions
- ➕ **New Chat** — Start fresh conversations anytime

---

## 🛠️ Tech Stack
| Technology | Purpose |
|---|---|
| Streamlit | Frontend UI |
| Groq API (Llama 3) | AI responses |
| Python | Backend logic |
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

### 4. Add your API key
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app
```bash
streamlit run app/main.py
```

---

## 📁 Project Structure
```
cooking-assistant/
├── app/
│   └── main.py            
├── utils/
│   ├── __init__.py
│   ├── openai_helper.py   
│   └── history.py         
├── .streamlit/
│   └── config.toml        
├── .env                   
├── requirements.txt
└── README.md
```

---

## 🔑 Get Free Groq API Key
1. Go to https://console.groq.com
2. Sign up for free
3. Create an API key
4. No credit card needed!

---

## 👨‍💻 Author
**Yashwanth R**
- GitHub: [@R-Yashwanth](https://github.com/R-Yashwanth)

---

⭐ If you found this useful, please give it a star on GitHub!
