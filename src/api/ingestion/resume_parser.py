import fitz

def extract_text_from_pdf(file_path: str) -> str:
    try:
        with fitz.open(file_path) as doc:
            pages = [page.get_text() for page in doc]
    except (fitz.EmptyFileError, fitz.FileDataError, fitz.FileNotFoundError, RuntimeError) as exc:
        raise ValueError("Could not read PDF file.") from exc

    return "\n".join(pages).strip()
