import os
from groq import Groq
import re 

def analyze_offer(text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, "prompt.txt")

    with open(prompt_path, "r", encoding="utf8") as f:
        base_prompt = f.read()

    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": text}
        ]
    )

    # Nettoyage du contenu avant conversion en JSON
    raw_content = res.choices[0].message.content
    raw_content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_content)

    return raw_content
