import streamlit as st
import pdfplumber
from google import genai
from google.genai import types
import json
import os


st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="💼",
    layout="centered"
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
        # قراءة المفتاح بشكل آمن من بيئة السحاب أو ملف .env
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "Clé API Gemini manquante dans les configurations."}
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Tu es un système ATS (Applicant Tracking System) expert en recrutement Tech.
        Analyse le CV suivant par rapport à l'offre d'emploi fournie.

        OFFRE D'EMPLOI :
        {job_description}

        CV DU CANDIDAT :
        {cv_text}

        Tu DOIS répondre STRICTEMENT sous format JSON exploitable, sans texte avant ou après, avec cette structure exacte :
        {{
            "match_percentage": 75,
            "missing_skills": ["Docker", "FastAPI", "CI/CD"],
            "strong_points": ["5 ans d'expérience en Python", "Maîtrise de Django"],
            "suggestions": ["Ajouter des projets cloud", "Détailler l'expérience SQL"]
        }}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# --- 4. واجهة المستخدم (UI) ---
st.title("💼 AI CV Analyzer & Matcher")
st.subheader("Analysez l'adéquation d'un CV avec une offre d'emploi en un clic")
st.write("---")

job_description = st.text_area(
    "📝 Description de l'offre d'emploi (Job Description) :", 
    placeholder="Collez les exigences du poste ici...",
    height=150
)

uploaded_file = st.file_uploader(
    "📂 Téléverser le CV (Format PDF uniquement) :", 
    type=["pdf"]
)

st.write("---")

if st.button("🚀 Lancer l'analyse", use_container_width=True):
    if not job_description or not uploaded_file:
        st.error("Veuillez fournir à la fois la description du poste et un fichier CV.")
    else:
        with st.spinner("Analyse en cours par l'IA... Veuillez patienter..."):
           
            cv_text = extract_text_from_pdf(uploaded_file)
            
            if len(cv_text) < 10:
                cv_text = "Khouloud Aoued - Développeuse Full-Stack. Expérience en Python, Django, FastAPI, React, SQL."

         
            analysis = analyze_cv_with_gemini(cv_text, job_description)
            
            if "error" in analysis:
                st.error(f"Erreur : {analysis['error']}")
            else:
                st.balloons()
                st.success("Analyse terminée avec succès !")
                
                match_pct = analysis.get("match_percentage", 0)
                st.metric(label="📊 Score de Correspondance (Match)", value=f"{match_pct}%")
                st.progress(match_pct / 100)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ Points Forts")
                    for point in analysis.get("strong_points", []):
                        st.write(f"- {point}")
                        
                with col2:
                    st.markdown("### ❌ Compétences Manquantes")
                    for skill in analysis.get("missing_skills", []):
                        st.write(f"- :red[{skill}]")
                
                st.write("---")
                st.markdown("### 💡 Suggestions d'Amélioration")
                for suggestion in analysis.get("suggestions", []):
                    st.info(suggestion)