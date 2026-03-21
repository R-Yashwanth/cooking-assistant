import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
If the user asks ANYTHING not related to cooking, food, recipes, or ingredients,
respond with a short sarcastic funny response and DO NOT answer their question.

Examples:
- Politics/PM/Politicians → "The only PM I know is Paneer Makhani! 🧀 Want that recipe instead?"
- Sports → "The only sport I play is speed chopping onions! 🔪 Ask me something about food!"
- Movies → "The only blockbuster I know is a perfectly risen soufflé! 🍮 Stick to cooking!"
- Technology → "The only tech I trust is my pressure cooker! 🫕 Ask me a recipe!"
- News → "Breaking news: Your biryani needs more saffron! 🍚 Ask me about food!"
- Anything else → Make a funny food-related sarcastic comparison and redirect to cooking.

Always end with a nudge to ask a cooking question. Never answer non-cooking topics.
"""

def get_cooking_response(question: str, chat_history: list, preferences: str = "") -> str:
    """
    Get a cooking-related response from OpenAI GPT.
    
    Args:
        question: User's cooking question
        chat_history: Previous conversation history
        preferences: User's cuisine/diet preferences
    
    Returns:
        AI response string
    """
    try:
        messages = [
            {
                "role": "system",
                "content": f"{SYSTEM_PROMPT}\n\nUser Preferences: {preferences}"
            }
        ]

        # Add chat history (last 10 messages to manage tokens)
        messages.extend(chat_history[-10:])

        # Add current question
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Free tier friendly
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
            stream=False
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Sorry, I ran into an issue: {str(e)}. Please try again!"


def get_recipe_suggestion(cuisine: str = "Any", diet: str = "No Restriction", cook_time: str = "Any") -> str:
    """
    Get a random recipe suggestion based on preferences.
    
    Args:
        cuisine: Preferred cuisine type
        diet: Dietary restriction
        cook_time: Maximum cooking time
    
    Returns:
        Recipe suggestion string
    """
    try:
        prompt = f"""Suggest ONE random recipe that fits:
        - Cuisine: {cuisine}
        - Diet: {diet}
        - Cook Time: {cook_time}
        
        Give just the recipe name, 3-line description, and key ingredients. Keep it short!"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative chef who suggests exciting recipes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.9
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Could not fetch suggestion: {str(e)}"
