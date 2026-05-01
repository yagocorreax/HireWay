import re
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from src.api.processing.skill_extractor import extract_skills
from src.api.ingestion.resume_parser import extract_text_from_pdf
from src.api.processing.matcher import match_skills

app = FastAPI(title="HireWay API")

UPLOAD_DIR = Path("data/raw/resumes")
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/x-pdf", "application/octet-stream"}

# garante que a pasta existe
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _safe_resume_path(filename: str) -> Path:
    original_name = Path(filename or "").name

    if not original_name or Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(original_name).stem).strip("._")
    safe_stem = safe_stem or "resume"
    file_path = UPLOAD_DIR / f"{safe_stem}_{uuid4().hex}.pdf"

    try:
        file_path.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid filename.") from exc

    return file_path


def _validate_upload_metadata(file: UploadFile) -> None:
    content_type = (file.content_type or "").split(";")[0].strip().lower()

    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")


def _save_upload_file(file: UploadFile, file_path: Path) -> None:
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with file_path.open("rb") as buffer:
        header = buffer.read(1024)

    if b"%PDF-" not in header:
        file_path.unlink(missing_ok=True)
        raise ValueError("Uploaded file is not a valid PDF.")


async def _store_resume(file: UploadFile) -> Path:
    _validate_upload_metadata(file)
    file_path = _safe_resume_path(file.filename)

    try:
        await run_in_threadpool(_save_upload_file, file, file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return file_path


async def _extract_resume_text(file_path: Path) -> str:
    try:
        return await run_in_threadpool(extract_text_from_pdf, str(file_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = await _store_resume(file)
    extracted_text = await _extract_resume_text(file_path)

    resume_skills = extract_skills(extracted_text)

    return {
        "filename": file.filename,
        "skills": resume_skills,
        "text_preview": extracted_text[:1000]
    }

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form("")
):
    file_path = await _store_resume(file)
    extracted_text = await _extract_resume_text(file_path)

    resume_skills = extract_skills(extracted_text)
    job_skills = extract_skills(job_description)

    match_result = match_skills(resume_skills, job_skills)

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "match": match_result
    }

