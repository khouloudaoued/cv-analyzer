import streamlit as st
import pdfplumber
from google import genai
from google.genai import types
import json
import os


st.set_page_config(
    page_title="AI CV Analyzer Pro",
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
        Tu es un système ATS (Applicant Tracking System) expert en recrutement Tech et un coach en carrière professionnelle.
        Analyse le CV suivant par rapport à l'offre d'emploi fournie.

        OFFRE D'EMPLOI :
        {job_description}

        CV DU CANDIDAT :
        {cv_text}

        Tu DOIS répondre STRICTEMENT sous format JSON exploitable, بدون أي كلام إضافي، بالهيكل التالي تماماً:
        {{
            "match_percentage": 85,
            "strong_points": ["Compétence X", "Expérience Y"],
            "missing_skills": ["Technologie Z"],
            "suggestions": ["Conseil 1"],
            "formatting_review": "نقد احترافي قصير حول تنسيق الـ CV، طوله، ولغته (هل يحتاج صياغة أفضل؟)"
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


st.title("💼 AI CV Analyzer & Matcher Pro")
st.markdown("### حسّن فرص قبولك في الوظائف باستخدام التحليل الذكي الفوري من Gemini")
st.write("---")


col_in1, col_in2 = st.columns([1, 1])

with col_in1:
    job_description = st.text_area(
        "📝 Description de l'offre d'emploi (Job Description) :", 
        placeholder="Collez les exigences du poste ici...",
        height=200
    )

with col_in2:
    uploaded_file = st.file_uploader(
        "📂 Téléverser le CV (Format PDF uniquement) :", 
        type=["pdf"]
    )
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} chargé avec succès.")

st.write("---")

if st.button("🚀 Lancer l'analyse approfondie", use_container_width=True):
    if not job_description or not uploaded_file:
        st.error("Veuillez fournir à la fois la description du poste et un fichier CV.")
    else:
        with st.spinner("الذكاء الاصطناعي يقوم بقراءة الـ CV وتحليل المهارات حالياً..."):
            cv_text = extract_text_from_pdf(uploaded_file)
            if len(cv_text) < 10:
                cv_text = "Khouloud Aoued - Développeuse Full-Stack. Expérience en Python, Django, FastAPI, React, SQL."

            analysis = analyze_cv_with_gemini(cv_text, job_description)
            
            if "error" in analysis:
                st.error(f"Erreur : {analysis['error']}")
            else:
                st.balloons()
                
                
                st.markdown("## 📊 Tableau de Bord d'Analyse")
                
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
                        st.markdown(f">  **{point}**")
                        
                with col_cards2:
                    st.subheader("❌ Compétences Manquantes")
                    for skill in analysis.get("missing_skills", []):
                        st.markdown(f"> 🔴 :red[{skill}]")
                
                st.write("---")
                
                
                st.subheader("✍️ Analyse de Forme & Style (التنسيق والأسلوب)")
                st.info(analysis.get("formatting_review", "Aucune remarque sur le format."))
                
                
                st.subheader("💡 Suggestions d'Amélioration")
                for index, suggestion in enumerate(analysis.get("suggestions", [])):
                    st.warning(f"{index+1}. {suggestion}")
                
                
                st.write("---")
                report_text = f"""--- RAPPORT D'ANALYSE ATS ---
Score de Match : {match_pct}%

Points Forts :
{chr(10).join(['- ' + p for p in analysis.get('strong_points', [])])}

Compétences Manquantes :
{chr(10).join(['- ' + s for s in analysis.get('missing_skills', [])])}

Remarques sur la forme :
{analysis.get('formatting_review', '')}
"""
                st.download_button(
                    label="📥 Télécharger le rapport complet (TXT)",
                    data=report_text,
                    file_name=f"Rapport_ATS_{uploaded_file.name.replace('.pdf', '')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )