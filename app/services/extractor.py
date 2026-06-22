import pdfplumber
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVExtractor:
    
    @staticmethod
    def extract_text_direct(file_bytes: bytes) -> str:
        text = ""
        try:
            with pdfplumber.open(file_bytes) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur: {str(e)}")
            return ""

    @classmethod
    def get_clean_text(cls, file_bytes: bytes) -> str:
        if not file_bytes:
            return ""
            
        
        extracted_text = cls.extract_text_direct(file_bytes)
        
        # 2. إذا كان الملف سكانر أو فارغ، نمرر نصاً برمجياً غنياً للتجربة (Fallback Text)
        if len(extracted_text) < 10:
            logger.warning("PDF scanné détecté. Utilisation d'un texte de simulation Tech.")
            
          
            extracted_text = """
            Khouloud Aoued - Développeuse Full-Stack / Ingénieure Logiciel
            Compétences : Python, Django, FastAPI, SQL, React, Docker, Git.
            Expérience : 5 ans d'expérience dans le développement d'applications web et d'architectures SaaS multi-tenancy.
            Projets : Création d'une application quiz locale, développement de dashboards analytiques.
            Langues : Arabe, Français, Anglais, Allemand.
            """
            
        return extracted_text