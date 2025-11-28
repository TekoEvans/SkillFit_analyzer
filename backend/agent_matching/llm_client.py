# agent_matching/llm_client.py
import json
from groq import Groq
from backend.agent_matching.config import *
from backend.agent_matching.prompts import *
# from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from dotenv import load_dotenv
load_dotenv()




def call_llm(offer: dict, cv: dict) -> dict:
    """
    Appelle le LLM Groq pour comparer un CV à une offre.
    Retourne un dict avec : matching_score, matching_level, rationale, key_points
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY non défini !")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Construire le prompt
    user_content = USER_PROMPT_TEMPLATE.format(
        offer_json=json.dumps(offer, indent=2, ensure_ascii=False),
        cv_json=json.dumps(cv, indent=2, ensure_ascii=False)
    )
    
    # Appel API Groq
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]
    )
    
    # Parser la réponse
    result = json.loads(response.choices[0].message.content)
    return result
