import os


def generate_ai_response(message: str) -> str:
    """
    Generate an AI response using Groq.

    Provider:
    - Groq
    - Model: llama3-70b-8192
    - Env var: GROQ_API_KEY
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY")

    from groq import Groq

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are Synzept, an AI thinking partner helping users organize ideas and goals.",
            },
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content