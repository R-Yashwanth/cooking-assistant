import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Chef AI, a friendly and expert cooking assistant.
Help users with recipes, techniques, substitutions, and cooking tips.
Always be warm and encouraging. Use emojis. Format recipes clearly.
"""

def get_cooking_response(question: str, chat_history: list, preferences: str = "") -> str:
    try:
        messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nUser Preferences: {preferences}"}]
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

def get_recipe_suggestion(cuisine: str = "Any", diet: str = "No Restriction", cook_time: str = "Any") -> str:
    try:
        prompt = f"Suggest ONE random recipe. Cuisine: {cuisine}, Diet: {diet}, Cook Time: {cook_time}. Give name, 3-line description, key ingredients."
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a creative chef who suggests exciting recipes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not fetch suggestion: {str(e)}"
