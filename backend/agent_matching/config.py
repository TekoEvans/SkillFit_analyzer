# agent_matching/config.py
import os

# Configuration LLM Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
#MODEL_NAME = "llama-3.1-70b-versatile"  # Modèle Groq gratuit et performant
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0
