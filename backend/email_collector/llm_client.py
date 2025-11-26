import os
import json
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key)


def load_prompt(prompt_file="prompts/prompt.txt"):
    script_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(script_dir, prompt_file)
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "{cv_text}"


def extract_cv_data_with_llm(cv_text):
    client = _get_client()
    prompt_template = load_prompt()
    prompt = prompt_template.replace("{cv_text}", cv_text)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)
    except Exception:
        return None
