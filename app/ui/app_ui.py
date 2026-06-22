import streamlit as st
import requests

# إعدادات الصفحة العامة
st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="💼",
    layout="centered"
)

st.title("💼 AI CV Analyzer & Matcher")
st.subheader("Analysez l'adéquation d'un CV avec une offre d'emploi en un clic")
st.write("---")

# 1. مدخلات المستخدم
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

# 2. زر بدء التحليل المنطقي
if st.button("🚀 Lancer l'analyse", use_container_width=True):
    if not job_description or not uploaded_file:
        st.error("Veuillez fournir à la fois la description du poste et un fichier CV.")
    else:
        with st.spinner("Analyse en cours par l'IA... Veuillez patienter..."):
            try:
                # إعداد الملف لإرساله كـ Multipart Form Data
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                # إرسال المعامل كـ Query Parameter كما صممنا في FastAPI الـمحدث
                backend_url = f"http://127.0.0.1:8000/api/v1/analyze?job_description={job_description}"
                
                # الاتصال بالـ Backend
                response = requests.post(backend_url, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        analysis = result["analysis"]
                        
                        # 3. عرض النتيجة بشكل مرئي مبهر
                        st.balloons()
                        st.success("Analyse terminée avec succès !")
                        
                        # عرض نسبة المطابقة بشكل دائري أو شريط تقدم
                        match_pct = analysis.get("match_percentage", 0)
                        st.metric(label="📊 Score de Correspondance (Match)", value=f"{match_pct}%")
                        st.progress(match_pct / 100)
                        
                        # تقسيم الشاشة إلى قسمين لنقاط القوة والمهارات الناقصة
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
                        # عرض التوصيات في أسفل اللوحة
                        st.markdown("### 💡 Suggestions d'Amélioration")
                        for suggestion in analysis.get("suggestions", []):
                            st.info(suggestion)
                            
                    else:
                        st.error("Le backend n'a pas pu traiter la demande correctement.")
                else:
                    st.error(f"Erreur de connexion avec le serveur Backend (Code: {response.status_code})")
                    
            except Exception as e:
                st.error(f"Impossible de joindre le serveur Backend. Assurez-vous qu'il est en cours d'exécution. Détails : {str(e)}")