from google import genai
from google.genai import types
import json
import logging

logger = logging.getLogger(__name__)

class AIEngine:
    
    _client = None

    @classmethod
    def get_client(cls):
        """تهيئة عميل Gemini بشكل آمن ومحمي لـ GitHub"""
        if cls._client is None:
            import os
            from dotenv import load_dotenv
            load_dotenv() 
            
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                raise ValueError("Clé API Gemini manquante. Veuillez configurer GEMINI_API_KEY.")
            
            cls._client = genai.Client(api_key=api_key)
        return cls._client

    @classmethod
    def analyze_cv_against_job(cls, cv_text: str, job_description: str) -> dict:
        """تحليل النصوص باستخدام نموذج gemini-2.5-flash الحديث"""
        try:
            client = cls.get_client()
            
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
            logger.error(f"Erreur lors de l'appel à l'API Gemini: {str(e)}")
            return {
                "match_percentage": 0,
                "missing_skills": ["Erreur d'analyse"],
                "strong_points": [],
                "suggestions": [f"Veuillez réessayer. Détails : {str(e)}"]
            }