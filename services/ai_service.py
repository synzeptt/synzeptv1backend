import os


def generate_ai_response(message: str) -> str:
    """
    Generate an AI response using Groq.

    Provider:
    - Groq
    - Model: llama-3.3-70b-versatile
    - Env var: GROQ_API_KEY
    """
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Missing GROQ_API_KEY")

    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are Synzept, an AI thinking partner that helps users organize ideas and goals.",
            },
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content