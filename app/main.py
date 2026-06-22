from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.services.extractor import CVExtractor
from app.services.ai_engine import AIEngine

load_dotenv()

app = FastAPI(title="AI CV Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "healthy"}

@app.post("/api/v1/analyze")
async def analyze_cv(
    job_description: str, 
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Veuillez téléverser un fichier PDF.")
    
    try:
        file_bytes = await file.read()
        cv_text = CVExtractor.get_clean_text(file_bytes)
        
        if not cv_text:
            raise HTTPException(status_code=422, detail="Impossible d'extraire le texte du PDF.")
            
        analysis_result = AIEngine.analyze_cv_against_job(
            cv_text=cv_text, 
            job_description=job_description
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))