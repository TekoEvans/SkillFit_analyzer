import streamlit as st
import json
import os
import threading
from pathlib import Path
from datetime import datetime
from backend.models.job_offer import JobOffer
from backend.service_database import JobOfferRepository
from backend.agent_offres.annonces_extractor import run
from backend.email_collector.email_collector import _run_cli
from backend.agent_matching.run_matching import matching




# Configuration de la page
st.set_page_config(
    page_title="Système de Matching CV",
    page_icon="💼",
    layout="wide"
)
# Dossier où stocker les PDF
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_UPLOAD_DIR = os.path.join(BASE_DIR, "offres_pdf")

os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
# Initialisation de la session state
repo = JobOfferRepository()


BASE_DIR = Path(__file__).resolve().parent

# _run_cli()

# for thread in threading.enumerate():
#     if thread != threading.current_thread():
#         thread.join()


json_path = Path(BASE_DIR) / "backend" / "email_collector" / "candidates" / "candidates_statisticien_20251127.json"

with open(json_path, "r", encoding="utf-8") as f:
    cvs = json.load(f)
# Fonction d'analyse de matching
# def analyze_match(job, cv,top):
#     score = 0
#     matched_skills = 0
    
#     # Analyse des compétences (60 points max)
#     if job.get('skills') and cv.get('skills'):
#         for job_skill in job['skills']:
#             for cv_skill in cv['skills']:
#                 if job_skill.lower() in cv_skill.lower() or cv_skill.lower() in job_skill.lower():
#                     matched_skills += 1
#                     score += 60 / len(job['skills'])
#                     break
    
    # Analyse de l'expérience (30 points max)
    # job_exp = int(job.get('experience', 0))
    # cv_exp = int(cv.get('experience', 0))
    # if cv_exp >= job_exp:
    #     score += 30
    # elif cv_exp >= job_exp * 0.7:
    #     score += 20
    # elif cv_exp >= job_exp * 0.5:
    #     score += 10
    
    # # Bonus formation (10 points)
    # if cv.get('education'):
    #     score += 10
    
    # return min(100, int(score)), matched_skills

# Header
st.title("💼 Système de Matching Offres d'Emploi - CV")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Ajouter une Offre", "🔍 Analyser", "🏆 Résultats"])

# TAB 1: Ajouter une offre
with tab1:
    st.header("Nouvelle Offre d'Emploi")
    uploaded_pdf = st.file_uploader(
    "Joindre l'offre d'emploi *",
    type=["pdf"]
)
    
    with st.form("job_form"):
       col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        
        top_n = st.number_input(
            "Nombres de CVs à retenir",
            min_value=1,
            max_value=100,
            value=1
        )
    
        
        submitted = st.form_submit_button("✅ Ajouter l'Offre d'Emploi", use_container_width=True)
        
    if submitted:
        if not uploaded_pdf:
            st.error("❌ Les champs obligatoires (*) doivent être remplis.")
        else:
            pdf_path = None
            
            # Sauvegarde du PDF
            if uploaded_pdf:
                pdf_path = os.path.join(PDF_UPLOAD_DIR, uploaded_pdf.name)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_pdf.read())
            

            # Création de l'objet JobOffer
            
            json_offer = run(pdf_path.split('/')[-1])
            offer = JobOffer(
                            title=json_offer["title"],
                            description=json_offer["description"],
                            responsibilities=json.dumps(json_offer["responsibilities"]),
                            skills=json.dumps(json_offer["skills"]),
                            location=json_offer["location"],
                            experience=json_offer["experience"],
                            contact_email=json_offer["contact_email"],
                            filename=json_offer["filename"],
                            offer_date=json_offer["offer_date"],
                            
                        )

            offer_id = repo.add(offer)
            with st.spinner("🔄 Analyse en cours..."):
                st.success(f"✅ Offre enregistrée avec succès : **{offer_id}**")
    
    # Affichage des offres enregistrées
    
    jobs = repo.list()
    
    if repo:
        st.markdown("---")
        st.subheader(f"📋 Offres enregistrées ({len(jobs)})")
        
        for job in jobs:
            with st.expander(f" {job.title}_{job.location}_{job.offer_date}", expanded=False):
                st.write(f"**Description:** {job.description}")
                if job.skills:
                    st.write(f"**Compétences:** {job.skills}")
                st.write(f"**Expérience requise:** {job.experience}")

# TAB 2: Analyser
with tab2:
    st.header("Analyser les Candidatures")
    
    # Info sur les CVs
    st.info(f"📄 **CVs en mémoire:** {len(cvs)} candidats disponibles")
    
    # Afficher les CVs
    with st.expander("👥 Voir tous les CV en mémoire"):
        for cv in cvs:
            st.markdown(f"""
            **{cv['full_name']}**  
            - Email: {cv['email']}  
            - Tel: {cv['phone_number']}  
            - Compétences: {cv['technical_skills']}  
            - Expérience: {cv['summary']}   
            - Formation: {cv['educations'][0]["title"]}
            """)
            st.markdown("---")
    
    st.markdown("---")
    
    # Sélection de l'offre
    if not repo:
        st.warning("⚠️ Aucune offre d'emploi disponible. Ajoutez une offre dans l'onglet 'Ajouter une Offre'.")
    else:
        job_options = {job.title: job for job in jobs}
        selected_job_title = st.selectbox(
            "Sélectionner une offre d'emploi",
            options=list(job_options.keys())
        )
        
        if selected_job_title:
            selected_job = job_options[selected_job_title]
            
            # Affichage de l'offre sélectionnée
            st.markdown("### 📄 Offre sélectionnée")
            with st.container():
                st.markdown(f"**{selected_job.title}**")
                st.write(selected_job.description)
                if selected_job.skills:
                    st.write(f"🔧 **Compétences:** {selected_job.skills}")
                st.write(f"⏱️ **Expérience:** {selected_job.experience}")
            
            st.markdown("---")
            
            # Bouton d'analyse
            if st.button("🚀 Lancer l'Analyse", type="primary", use_container_width=True):
                if not cvs:
                    st.error("❌ Aucun CV en mémoire.")
                else:
                    with st.spinner("🔄 Analyse en cours..."):
                       
                        matching(Path(BASE_DIR)/"backend"/"agent_offres"/"outputs"/"annonce_statisticien.json",Path(BASE_DIR)/'backend'/'email_collector'/'candidates'/'candidates_statisticien_20251127.json',top_n)
                       
                    
                    st.success("✅ Analyse terminée ! Consultez l'onglet 'Résultats'")
                    st.balloons()
print(BASE_DIR)
with open(Path(BASE_DIR)/"backend"/"agent_matching"/"outputs"/"candidates_retained.json", "r", encoding="utf-8") as f:
    top_candidates = json.load(f)                    

# TAB 3: Résultats
with tab3:
    st.header(f"🏆 Top {top_n} Candidats Sélectionnés")
    
    if  not top_candidates:
        st.info("ℹ️ Aucune analyse effectuée. Allez dans l'onglet 'Analyser' pour lancer une analyse.")
    else:
        st.success(f"Résultats")
        st.markdown("---")
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        colors = ["gold", "silver", "#CD7F32", "blue", "green"]
        
        for idx, candidate in enumerate(top_candidates):
            # Carte pour chaque candidat
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {medals[idx]} {candidate['full_name']}")
                    st.markdown(f"#### {candidate['phone_number']} / {candidate['email']}")
                  
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**🔧 Compétences:**")
                        # st.write(', '.join(candidate['skills']))
                        st.write(f"**⏱️ Expérience:** {candidate['key_points']} ")
                    
                    with col_b:
                        st.write(f"**🎓 Formation:**")
                        st.write(candidate['rationale'])
                        
                
                with col2:
                    # Score
                    score_color = "green" if candidate['matching_score'] >= 80 else "orange" if candidate['matching_score'] >= 60 else "red"
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: {score_color}; color: white; border-radius: 10px;'>
                        <h1 style='margin: 0;'>{candidate['matching_score']}%</h1>
                        <p style='margin: 0;'>Score</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Barre de progression
                st.progress(candidate['matching_score'] / 100)
                
                st.markdown("---")
        
        # Statistiques globales
        st.markdown("### 📊 Statistiques")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_score = sum(c['matching_score'] for c in top_candidates) / len(top_candidates)
            st.metric("Score moyen", f"{avg_score:.1f}%")
        
        with col2:
            best_score = top_candidates[0]['matching_score']
            st.metric("Meilleur score", f"{best_score}%")
        
        with col3:
            excellent = sum(1 for c in top_candidates if c['matching_score'] >= 80)
            st.metric("Candidats excellents (≥80%)", excellent)