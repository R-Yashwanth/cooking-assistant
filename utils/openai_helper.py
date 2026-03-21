import os
import json
import pycountry
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Load .env file for local development
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

SYSTEM_PROMPT = """
You are Chef AI, a friendly and expert cooking assistant. You help users with:
- Step-by-step recipes with clear instructions
- Cooking techniques and tips
- Ingredient substitutions
- Meal planning and suggestions
- Nutritional information
- Food safety and storage tips

Guidelines:
- Always be warm, encouraging and easy to understand
- Format recipes with clear sections: Ingredients, Instructions, Tips
- For beginners, explain techniques in simple terms
- Suggest alternatives for hard-to-find ingredients
- Keep health and dietary restrictions in mind
- Use emojis to make responses fun and readable

STRICT RULE - NON COOKING QUESTIONS:
If the user asks ANYTHING that is NOT related to cooking, food, recipes, ingredients,
kitchen techniques, or nutrition — you MUST follow these steps:
STEP 1: Detect the topic (politics, sports, movies, technology, news, relationships, etc.)
STEP 2: Create a SHORT sarcastic funny response that compares their topic to food
STEP 3: Refuse to answer the actual question
STEP 4: End with a funny nudge to ask a cooking question instead

Sarcastic response examples (use as inspiration, be creative):
- Politics/PM/Government: "The only PM I know is Paneer Makhani! Politicians come and go but good recipes are forever!"
- Sports/Cricket/Football: "The only match I care about is matching spices! Score a recipe instead!"
- Movies/Entertainment: "The only blockbuster I know is a perfectly puffed roti! Let's talk food!"
- Technology/AI/Coding: "The only coding I do is cracking eggs! Ask me a recipe!"
- News/Current Events: "Breaking news: Your kitchen needs more love! What shall we cook today?"
- Love/Relationships: "The only relationship I believe in is between garlic and butter! Ask me about food!"
- History/Geography: "The only history I know is how biryani was invented! Want that story with the recipe?"
- Anything else: Create a funny food comparison and redirect to cooking

CRITICAL: This sarcastic response rule MUST be applied BEFORE the language rule.
The sarcastic response MUST ALSO be in the language specified in User Preferences.
NEVER answer the non-cooking question. ALWAYS redirect to cooking.

LANGUAGE RULE - THIS IS MANDATORY AND OVERRIDES EVERYTHING:
You MUST respond in the EXACT language specified in the User Preferences.
- If preferences say "Telugu" - respond 100% in Telugu script only
- If preferences say "Hindi" - respond 100% in Hindi script only
- If preferences say "Tamil" - respond 100% in Tamil script only
- If preferences say "French" - respond 100% in French only
- If preferences say "Spanish" - respond 100% in Spanish only
- If preferences say "Japanese" - respond 100% in Japanese only
- For ANY other language specified - respond ONLY in that language
- NEVER mix English with another language
- NEVER respond in English if another language is specified
- This language rule applies to BOTH cooking answers AND sarcastic responses
"""


def get_client():
    """Get Groq client using Streamlit secrets or environment variable."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key)


def batch_translate_ui(texts: list, language: str) -> dict:
    """
    Translate ALL UI texts in a SINGLE Groq API call.
    Returns a dict mapping original English text to translated text.
    This is the fastest possible approach — one call for everything.
    """
    try:
        client = get_client()
        numbered = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])
        prompt = (
            f"Translate the following numbered list of UI texts to {language}.\n"
            f"Return ONLY a JSON object where keys are the original English texts "
            f"and values are the {language} translations.\n"
            f"Do not add any explanation, just return valid JSON.\n\n"
            f"{numbered}"
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a translator. Translate UI texts to {language}. Return only valid JSON with original English as keys and {language} translations as values. No markdown, no explanation."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        # Clean up markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()
        translations = json.loads(result_text)
        # Fill in any missing keys with originals
        for text in texts:
            if text not in translations:
                translations[text] = text
        return translations
    except Exception as e:
        print(f"batch_translate_ui error: {e}")
        return {text: text for text in texts}


def get_cooking_response(question: str, chat_history: list, preferences: str = "") -> str:
    """Send user question to Groq AI and return response."""
    try:
        client = get_client()
        messages = [
            {
                "role": "system",
                "content": f"{SYSTEM_PROMPT}\n\nUser Preferences: {preferences}"
            }
        ]
        messages.extend(chat_history[-10:])
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I ran into an issue: {str(e)}"


def get_recipe_suggestion(cuisine: str = "Any", diet: str = "No Restriction", cook_time: str = "Any", language: str = "English", already_suggested: str = "none") -> str:
    """Generate a surprising unique recipe — avoids already suggested dishes."""
    try:
        import random
        client = get_client()
        random_seed = random.randint(1, 99999)

        avoid = f" STRICTLY avoid these already suggested dishes: {already_suggested}." if already_suggested != "none" else ""

        prompt = (
            f"[Seed: {random_seed}] "
            f"Surprise me with ONE completely unique and unexpected recipe from {cuisine}. "
            f"Diet: {diet}, Cook Time: {cook_time}. "
            f"{avoid} "
            f"Do NOT suggest obvious popular dishes like Biryani, Butter Chicken, Pizza, Pasta. "
            f"Suggest something authentic but lesser known and surprising. "
            f"Give: recipe name on first line, 2-line description, key ingredients. "
            f"Respond in {language} language."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a creative adventurous chef. Every suggestion must be unique. NEVER repeat a dish that was already suggested. Be bold and surprising."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=1.0,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not fetch suggestion: {str(e)}"


def get_popular_dishes(country: str, state: str) -> list:
    """Get 5 popular dishes from a country/state using AI."""
    try:
        client = get_client()
        location = f"{state}, {country}" if state != "Any" else country
        prompt = (
            f"List exactly 5 most famous and popular traditional dishes from {location}. "
            f"Return ONLY a comma-separated list of dish names, nothing else. "
            f"No numbering, no descriptions, just dish names separated by commas."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a food expert. Return only comma-separated dish names, nothing else."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        dishes_text = response.choices[0].message.content.strip()
        dishes = [d.strip() for d in dishes_text.split(",") if d.strip()]
        return dishes[:5]
    except Exception as e:
        print(f"get_popular_dishes error: {e}")
        return []


def get_country_languages(country: str) -> list:
    """Get ALL official and major languages of a country using AI."""
    try:
        client = get_client()
        prompt = (
            f"List ALL official and major regional languages spoken in {country}. "
            f"Include ALL significant languages. "
            f"Return ONLY a comma-separated list of language names in English. "
            f"Maximum 10 languages. No numbering, no extra text."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a linguistics expert. List ALL official and major languages. Return only comma-separated names in English."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.1
        )
        langs_text = response.choices[0].message.content.strip()
        langs = [l.strip().title() for l in langs_text.split(",") if l.strip()]
        if "English" not in langs:
            langs.insert(0, "English")
        return langs[:10]
    except Exception as e:
        print(f"get_country_languages error: {e}")
        return ["English"]


def get_country_states(country: str) -> list:
    """
    Get states/regions using pycountry subdivisions first.
    Falls back to AI if pycountry has no data.
    """
    # ── Try pycountry first ────────────────────────────────────────────────────
    try:
        results = pycountry.countries.search_fuzzy(country)
        if results:
            alpha2 = results[0].alpha_2
            subdivisions = list(pycountry.subdivisions.get(country_code=alpha2) or [])
            if subdivisions:
                top_level_types = {
                    "State", "Province", "Region", "Prefecture", "Emirate",
                    "Canton", "County", "Department", "Governorate", "Oblast",
                    "Territory", "Division", "District", "Municipality",
                    "Autonomous region", "Federal subject", "City",
                }
                top = [s.name for s in subdivisions if s.type in top_level_types]
                if not top:
                    top = [s.name for s in subdivisions]
                if top:
                    return ["Any"] + sorted(top)
    except Exception as e:
        print(f"pycountry states error: {e}")

    # ── Fall back to AI ────────────────────────────────────────────────────────
    try:
        client = get_client()
        prompt = (
            f"List ALL states, provinces or major regions of {country}. "
            f"Include ALL of them. "
            f"Return ONLY a comma-separated list of names. "
            f"No numbering, no descriptions."
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a geography expert. List ALL states or provinces. Return only comma-separated names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )
        states_text = response.choices[0].message.content.strip()
        states = [s.strip() for s in states_text.split(",") if s.strip()]
        return ["Any"] + sorted(states)
    except Exception as e:
        print(f"get_country_states AI error: {e}")
        return ["Any"]
