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
If the user asks ANYTHING not related to cooking, food, recipes, ingredients,
kitchen techniques, or nutrition — check OFF_TOPIC_COUNT in User Preferences:

If OFF_TOPIC_COUNT is 0 (first time):
- Tone: Funny, witty, playful
- Style: Make a clever unexpected joke connecting their topic to food
- Keep it short — 1-2 sentences max
- End with a question to redirect to cooking
- DO NOT use "The only X I know is..." pattern
- Think of something completely original and funny every single time

If OFF_TOPIC_COUNT is 1 (second time):
- Tone: Clearly irritated, passive aggressive, exasperated
- Style: Express genuine frustration in a funny way
- Keep it short — 2-3 sentences max
- Show you are fed up but still redirect to cooking
- DO NOT repeat anything from previous responses
- Be unpredictable — vary your frustration style every time

If OFF_TOPIC_COUNT is 2 or more (third time and beyond):
- Tone: FULL MELTDOWN — dramatic, hilarious, over the top anger
- Style: Completely lose it in a funny dramatic way using food references
- Use CAPS for emphasis on key words
- Be theatrical and exaggerated
- Each meltdown must be COMPLETELY different from previous ones
- The angrier and more dramatic the better
- Still redirect to cooking at the end

ABSOLUTE RULES:
- If user greets you greet them back with warming message
- Your name is Chef AI — if asked just say that and what you do
- NEVER use example phrases from instructions — create 100% original responses
- NEVER start with "The only" — that pattern is forbidden
- NEVER repeat a response style you already used in this conversation
- Every single response MUST be completely unique and original
- Respond in the language specified in User Preferences
- NEVER answer the actual non-cooking question
- ALWAYS end with cooking redirect
- Strictly Follow off set rules when greater than one you should be irritated and angry
- Use the CREATIVITY SEED in preferences to generate something completely new

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
    Uses small fast model to save tokens.
    Returns dict mapping English text to translated text.
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
            model="llama-3.1-8b-instant",
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
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()
        translations = json.loads(result_text)
        for text in texts:
            if text not in translations:
                translations[text] = text
        return translations
    except Exception as e:
        print(f"batch_translate_ui error: {e}")
        return {text: text for text in texts}


def get_cooking_response(question: str, chat_history: list, preferences: str = "") -> str:
    """Send user question to Groq AI and return response."""
    import random
    client = get_client()
    random_seed = random.randint(1, 99999)

    # Extract language from preferences
    current_language = "English"
    for pref in preferences.split(","):
        if "Respond only in" in pref:
            current_language = pref.split("Respond only in")[-1].replace("language.", "").strip()
            break

    messages = [
        {
            "role": "system",
            "content": (
                f"{SYSTEM_PROMPT}\n\n"
                f"User Preferences: {preferences}\n\n"
                f"CREATIVITY SEED: {random_seed}\n\n"
                f"⚠️ CURRENT LANGUAGE OVERRIDE: You MUST respond in {current_language} ONLY. "
                f"This overrides ALL previous conversation history. "
                f"Even if previous messages were in a different language, "
                f"YOU MUST NOW RESPOND IN {current_language.upper()} ONLY. "
                f"Do not use any other language under any circumstances."
            )
        }
    ]
    messages.extend(chat_history[-6:])
    
    # Add explicit language reminder as last system message
    messages.append({
        "role": "system",
        "content": f"REMINDER: Respond to the next message in {current_language} ONLY. No other language."
    })
    
    messages.append({"role": "user", "content": question})

    off_topic_count = int(preferences.split("OFF_TOPIC_COUNT:")[-1].strip()) if "OFF_TOPIC_COUNT:" in preferences else 0
    temperature = 0.7 if off_topic_count == 0 else 0.95

    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=3000,  # Increased from 1000 to handle non-English scripts
                temperature=temperature
            )
            # Track tokens
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "rate_limit_exceeded" in error_str or "429" in error_str:
                print(f"Rate limit hit on {model}, trying next...")
                continue
            else:
                return f"Sorry, I ran into an issue: {error_str}"

    return "Sorry, all models are currently rate limited. Please try again in a few minutes!"


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
            model="llama-3.1-8b-instant",
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
    # If no country selected, return global popular dishes without API call
    if country == "Any":
        return ["Biryani", "Pizza", "Sushi", "Tacos", "Pad Thai"]
    try:
        client = get_client()
        location = f"{state}, {country}" if state != "Any" else country
        prompt = (
            f"List exactly 5 famous traditional dishes from {location}. "
            f"Rules: Return ONLY dish names. No sentences. No explanations. "
            f"No 'Here are' or 'I assume' or any other text. "
            f"Just 5 dish names separated by commas. Nothing else. "
            f"Example format: Biryani, Dosa, Idli, Vada, Sambar"
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a food expert. Return ONLY comma-separated dish names. No sentences, no explanations, no extra text. Just dish names separated by commas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.1
        )
        dishes_text = response.choices[0].message.content.strip()
        # Clean up any accidental sentences — only keep short items
        dishes = [d.strip() for d in dishes_text.split(",") if d.strip() and len(d.strip()) < 40]
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
            model="llama-3.1-8b-instant",
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

    try:
        client = get_client()
        prompt = (
            f"List ALL states, provinces or major regions of {country}. "
            f"Include ALL of them. "
            f"Return ONLY a comma-separated list of names. "
            f"No numbering, no descriptions."
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
