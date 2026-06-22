import streamlit as st
import pdfplumber
from google import genai
from google.genai import types
import json
import os

# --- 1. Configuration de la page ---
st.set_page_config(
    page_title="AI CV Analyzer & Improver",
    page_icon="💼",
    layout="wide"
)

# --- 2. Logique d'extraction du PDF ---
def extract_text_from_pdf(file_bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception:
        return ""

# --- 3. Analyse principale du CV ---
def analyze_cv_with_gemini(cv_text: str, job_description: str) -> dict:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "Clé API Gemini manquante."}
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Tu es un système ATS expert et un coach en carrière professionnelle.
        Analyse le CV suivant par rapport à l'offre d'emploi fournie.

        OFFRE D'EMPLOI :
        {job_description}

        CV DU CANDIDAT :
        {cv_text}

        Tu DOIS répondre STRICTEMENT sous format JSON exploitable, avec cette structure exacte :
        {{
            "match_percentage": 85,
            "strong_points": ["Compétence X", "Expérience Y"],
            "missing_skills": ["Technologie Z"],
            "suggestions": [
                {{"id": 1, "critique": "Le résumé initial manque d'impact", "exemple_amelioration": "Développeuse Full-Stack passionnée par l'IA, spécialisée en FastAPI et architectures SaaS..."}},
                {{"id": 2, "critique": "L'expérience en bases de données n'est pas chiffrée", "exemple_amelioration": "Optimisation des requêtes SQL ayant permis de réduire le temps de chargement de 30%..."}}
            ],
            "formatting_review": "Conseils sur la forme."
        }}
        """

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
            else:
                raise e

        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# --- 4. Fonctionnalité bonus : Améliorateur de section à la demande ---
def generer_reformulation_sur_mesure(texte_original, objectif) -> str:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        prompt = f"Prends ce texte brut issu d'un CV : '{texte_original}'. Reformule-le de manière extrêmement professionnelle, percutante et optimisée pour les ATS, avec pour objectif de : {objectif}. Donne uniquement le texte amélioré sans blabla."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Erreur de génération : {str(e)}"

# --- 5. Interface Utilisateur (UI) ---
st.title("💼 AI CV Analyzer & Smart Improver")
st.markdown("### Analysez votre CV et générez des améliorations textuelles instantanées")
st.write("---")

col_in1, col_in2 = st.columns([1, 1])

with col_in1:
    job_description = st.text_area(
        "📝 Description de l'offre d'emploi :", 
        placeholder="Collez les exigences du poste ici...",
        height=200
    )

with col_in2:
    uploaded_file = st.file_uploader(
        "📂 Téléverser le CV (PDF) :", 
        type=["pdf"]
    )

st.write("---")

if st.button("🚀 Lancer l'analyse approfondie", use_container_width=True):
    if not job_description or not uploaded_file:
        st.error("Veuillez fournir la description du poste et le CV.")
    else:
        with st.spinner("Analyse en cours..."):
            cv_text = extract_text_from_pdf(uploaded_file)
            if len(cv_text) < 10:
                cv_text = "Khouloud Aoued - Développeuse Full-Stack. Python, Django, FastAPI, React."

            analysis = analyze_cv_with_gemini(cv_text, job_description)
            
            if "error" in analysis:
                st.error(f"Erreur : {analysis['error']}")
            else:
                st.balloons()
                
                # Sauvegarde des résultats dans la session Streamlit pour l'interactivité
                st.session_state['analysis_result'] = analysis
                st.session_state['cv_text'] = cv_text

if 'analysis_result' in st.session_state:
    analysis = st.session_state['analysis_result']
    
    # --- Affichage du Tableau de Bord ---
    match_pct = analysis.get("match_percentage", 0)
    col_res1, col_res2 = st.columns([1, 2])
    with col_res1:
        st.metric(label="Score de Match", value=f"{match_pct}%")
        st.progress(match_pct / 100)
    with col_res2:
        chart_data = {
            "Points Forts": len(analysis.get("strong_points", [])),
            "Manques": len(analysis.get("missing_skills", []))
        }
        st.bar_chart(chart_data, horizontal=True, height=150)
    
    st.write("---")
    
    col_cards1, col_cards2 = st.columns(2)
    with col_cards1:
        st.subheader("✅ Points Forts")
        for point in analysis.get("strong_points", []):
            st.markdown(f"> **{point}**")
            
    with col_cards2:
        st.subheader("❌ Compétences Manquantes")
        for skill in analysis.get("missing_skills", []):
            st.markdown(f"> 🔴 :red[{skill}]")
    
    st.write("---")
    
    # --- Section Suggestions et Amélioration Directe ---
    st.subheader("💡 Suggestions d'Amélioration & Exemples Prêts à l'emploi")
    
    for sug in analysis.get("suggestions", []):
        with st.expander(f"🔍 {sug.get('critique')}"):
            st.markdown("**Version suggérée par l'IA :**")
            st.code(sug.get('exemple_amelioration'), language="text")
            st.caption("Vous pouvez copier ce texte directement dans votre CV.")

    st.write("---")
    
    # --- NOUVEAUTÉ : L'outil d'amélioration dynamique (Smart Improver) ---
    st.subheader("🛠️ Outil d'Amélioration Sur-Mesure (Copier/Coller magique)")
    st.markdown("Collez une section de votre CV actuel que vous voulez réécrire pour cette offre :")
    
    texte_a_ameliorer = st.text_area("Votre texte actuel (ex: une description d'expérience ou votre résumé) :", height=100)
    objectif_amelioration = st.selectbox("Objectif de l'amélioration :", [
        "Rendre plus percutant et professionnel",
        "Mettre en valeur les compétences Cloud et CI/CD",
        "Ajouter des verbes d'action orientés résultats (Tech)",
        "Intégrer les mots-clés de l'offre d'emploi"
    ])
    
    if st.button("🪄 Générer la version améliorée"):
        if texte_a_ameliorer:
            with st.spinner("Réécriture en cours..."):
                version_corrigee = generer_reformulation_sur_mesure(texte_a_ameliorer, objectif_amelioration)
                st.success("Voici votre texte optimisé ! Vous n'avez plus qu'à le copier :")
                st.code(version_corrigee, language="text")
        else:
            st.warning("Veuillez coller du texte d'abord.")