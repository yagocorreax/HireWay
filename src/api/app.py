from fastapi import FastAPI, UploadFile, File
import shutil
import os

from src.api.ingestion.resume_parser import extract_text_from_pdf

app = FastAPI(title="HireWay API")

upload_dir= "data/raw/resumes"

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    extracted_text = extract_text_from_pdf(file_path)

    return {
        "filename": file.filename,
        "text_preview": extracted_text[:1000] 
    }