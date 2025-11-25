# Agent Matching - SKILLFIT ANALYZER

## Installation

```bash
pip install groq
```

## Configuration

Définir ta clé API Groq :

**Windows (CMD):**
```cmd
set GROQ_API_KEY=gsk_ta-clef-ici
```

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="gsk_ta-clef-ici"
```

**Mac/Linux:**
```bash
export GROQ_API_KEY="gsk_ta-clef-ici"
```

## Utilisation

```bash
cd agent_matching
python run_matching.py --offer data/offer.json --cvs data/cvs.json --top_n 3 --output_dir outputs/
```

## Fichiers de sortie

- `candidates_retained.json` - Candidats retenus (VERY_HIGH)
- `candidates_non_retained.json` - Candidats non retenus
- `candidates_retained.csv` - Pour Excel
- `candidates_non_retained.csv` - Pour Excel
- `fiches_candidats/` - Une fiche par candidat retenu

## Structure

```
agent_matching/
├── config.py        # Configuration API Groq
├── prompts.py       # Prompts LLM
├── llm_client.py    # Appel Groq
├── matcher.py       # Logique matching
├── run_matching.py  # Script principal
└── data/
    ├── offer.json   # Exemple offre
    └── cvs.json     # Exemple CV
```

## Modèle utilisé

- **llama-3.1-70b-versatile** (gratuit sur Groq)
