import streamlit as st
import pdfplumber
from google import genai
from google.genai import types
import json
import os


st.set_page_config(
    page_title="AI CV Analyzer & Improver Pro",
    page_icon="💼",
    layout="wide"
)


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
                {{"id": 1, "critique": "Le résumé initial manque d'impact", "exemple_amelioration": "Développeuse Full-Stack passionnée par l'IA..."}},
                {{"id": 2, "critique": "L'expérience n'est pas chiffrée", "exemple_amelioration": "Optimisation des requêtes..."}}
            ],
            "formatting_review": "Conseils sur la forme."
        }}
        """

        
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
        except Exception:
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
            except Exception:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )

        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}


st.title("💼 AI CV Analyzer & Smart Improver Pro")
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
                st.session_state['analysis_result'] = analysis
                st.session_state['cv_text'] = cv_text


if 'analysis_result' in st.session_state:
    analysis = st.session_state['analysis_result']
    
    match_pct = analysis.get("match_percentage", 0)
    
    st.metric(label="📊 Score de Match ATS", value=f"{match_pct}%")
    st.progress(match_pct / 100)
    
    st.write("---")
    
    col_cards1, col_cards2 = st.columns(2)
    with col_cards1:
        st.markdown("### ✅ Points Forts")
        for point in analysis.get("strong_points", []):
            st.markdown(f"- {point}")
            
    with col_cards2:
        st.markdown("### ❌ Compétences Manquantes")
        for skill in analysis.get("missing_skills", []):
            st.markdown(f"- :red[{skill}]")
    
    st.write("---")
    
    st.markdown("### 💡 Suggestions d'Amélioration & Exemples Prêts à l'emploi")
    for sug in analysis.get("suggestions", []):
        critique_text = sug.get('critique') or "Analyse"
        with st.expander(f"🔍 {critique_text}"):
            st.markdown("**Version suggérée par l'IA :**")
            
            
            version_corrigee = (
                sug.get('exemple_amelioration') or 
                sug.get('exemple_amélioration') or 
                sug.get('exemple') or 
                "Texte généré indisponible"
            )
            st.code(version_corrigee, language="text")

    st.write("---")
    st.markdown("### 🎨 Conseils de mise en page")
    st.info(analysis.get("formatting_review", "Aucun conseil de forme généré."))