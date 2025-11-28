# SkillFit_analyzer


## Description 
Assistant Multi-Agents de Screening Automatisé de Candidats - SkillFit_analyzer

Résumé rapide
----------------
Ce dépôt contient une application Streamlit et plusieurs modules Python pour :
- extraire et analyser des offres (PDF) (`backend/agent_offres`),
- extraire des données de CV via un client LLM (`backend/email_collector`),
- effectuer un matching entre offres et CVs en appelant un LLM (`backend/agent_matching`),
- stocker les offres dans une base SQLite (`backend/service_database.py`).

Remarque importante : la structure décrite dans l'ancienne version du README (microservices FastAPI, MCP, LangChain, etc.) n'est pas implémentée dans ce dépôt. Le projet fonctionne en tant qu'application locale (Streamlit + scripts) et utilise l'API Groq pour les appels LLM.

Fonctionnalités réelles implémentées
-----------------------------------
- Interface Streamlit interactive : `app.py` (upload d'offres, affichage, analyses basiques).
- Extraction et parsing d'annonces PDF : `backend/agent_offres/annonces_extractor.py`.
- Extraction de données depuis des CV / emails : `backend/email_collector` (script CLI et modules).
- Matching via LLM : `backend/agent_matching` (client Groq, prompts, `run_matching.py`).
- Persistance simple : SQLite géré par `backend/service_database.py` (fichier `rh_jobs.db`).

Arborescence pertinente
-----------------------
`/` (racine)
- `app.py` - interface Streamlit
- `main.py` - script léger/utilitaire
- `requirements.txt`
- `rh_jobs.db` - base SQLite (générée à l'exécution)
- `offres_pdf/` - dossier attendu pour les PDF d'offres
- `outputs/` - dossier où les scripts écrivent des JSON/CSV
- `backend/`
	- `service_database.py`
	- `agent_offres/` (annonces_extractor.py, prompt.txt)
	- `agent_matching/` (config.py, llm_client.py, matcher.py, run_matching.py, data/)
	- `agent_interview/` (prompts / utilitaires pour entretiens)
	- `email_collector/` (processor, llm_client, utils, etc.)
	- `models/` (job_offer, candidate, cv, application)

Prérequis
---------
- Python 3.10+ (3.11 recommandé)
- Une clé API Groq (utilisée par `backend/*/llm_client.py`).
- Installer les dépendances listées dans `requirements.txt`.

Installation (PowerShell)
------------------------
Copiez-collez depuis la racine du projet :

```powershell
# 1) Créer un environnement virtuel
python -m venv .venv

# 2) Activer l'environnement (PowerShell)
& .venv\Scripts\Activate.ps1

# 3) Mettre pip à jour (optionnel)
python -m pip install --upgrade pip

# 4) Installer les dépendances
pip install -r requirements.txt
```

Configuration des variables d'environnement
------------------------------------------
- Définir la clé Groq dans votre environnement (exemple PowerShell) :

```powershell
$env:GROQ_API_KEY = "votre_clef_groq"
```

Quelques modules peuvent nécessiter des dépendances système (ex: `lxml`, `PyMuPDF`, `pyarrow`). Si une installation échoue, installez les dépendances système appropriées (voir message d'erreur pip).

Utilisation
----------

- Lancer l'interface Streamlit (UI principale) :

```powershell
streamlit run app.py
```

- Extraire et analyser une annonce (script utilisé par l'UI) :

```powershell
python backend/agent_offres/annonces_extractor.py
```

- Lancer le matching via le module `agent_matching` (exemple) :

```powershell
python backend/agent_matching/run_matching.py --offer backend/agent_matching/data/offer.json --cvs backend/agent_matching/data/cvs.json --top_n 3 --output_dir outputs/
```

- Lancer le collecteur/parseur de CV (CLI) :

```powershell
python -m backend.email_collector.email_collector
```

Notes d'intégration LLM
-----------------------
- Les appels LLM utilisent la librairie `groq` et le modèle référencé dans les fichiers `backend/*/llm_client.py`.
- Assurez-vous que `GROQ_API_KEY` est défini avant d'exécuter les scripts qui appellent l'API Groq.

Données d'exemple
-----------------
- `backend/agent_matching/data/cvs.json`
- `backend/agent_matching/data/offer.json`
- `offres_pdf/` contient les PDF d'entrée attendus pour l'UI et l'extracteur.

Dépannage rapide
----------------
- Erreur d'installation pip : installez d'abord les dépendances système listées dans le message d'erreur (compilateurs, headers, bibliothèques). Ensuite relancez `pip install -r requirements.txt`.
- Problèmes LLM : vérifiez la variable `GROQ_API_KEY` et la connectivité réseau.
- Base de données : `rh_jobs.db` est créée automatiquement par `backend/service_database.py` à la première exécution.

Contribuer / développer
-----------------------
- Forkez / créez une branche pour vos modifications.
- Testez localement l'UI Streamlit et les scripts `backend/*`.
- Si vous souhaitez transformer le projet en microservices FastAPI ou ajouter un protocole MCP, je peux vous aider à refactorer l'architecture.

Licence
-------
Voir le fichier `LICENSE` à la racine du dépôt.



