from fastapi import FastAPI, UploadFile, File
import shutil
import os
from src.api.processing.skill_extractor import extract_skills
from src.api.ingestion.resume_parser import extract_text_from_pdf
from src.api.processing.matcher import match_skills

app = FastAPI(title="HireWay API")

UPLOAD_DIR = "data/raw/resumes"

# garante que a pasta existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # salvar arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(file_path)

    resume_skills = extract_skills(extracted_text)

    return {
        "filename": file.filename,
        "skills": resume_skills,
        "text_preview": extracted_text[:1000]
    }

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = ""
):
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(file_path)

    resume_skills = extract_skills(extracted_text)
    job_skills = extract_skills(job_description)

    match_result = match_skills(resume_skills, job_skills)

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "match": match_result
    }

