import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import ResumeData
from .ingest.pdf_ingester import ingest_document
from .extract.extractor import WorkingDayExtractor

app = FastAPI(
    title="WorkingDay Resume Parser API",
    description="High-precision candidate-side resume parser for Workday job applications",
    version="0.1.0"
)

# Enable CORS for local extension and sandbox development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

extractor = WorkingDayExtractor()


class ParseTextRequest(BaseModel):
    raw_text: str
    put_additional_given_in_middle: bool = False


@app.get("/health")
def health():
    return {"status": "ok", "service": "workingday-parser", "version": "0.1.0"}


@app.post("/parse", response_model=ResumeData)
def parse_text_endpoint(req: ParseTextRequest):
    """
    Parses resume from raw text string.
    """
    from .ingest.layout import TextBlock
    lines = [l for l in req.raw_text.split("\n") if l.strip()]
    block = TextBlock(lines=lines, bbox=(0, 0, 500, float(len(lines) * 20)))
    result = extractor.extract_from_blocks(
        [block],
        put_additional_given_in_middle=req.put_additional_given_in_middle
    )
    return result


@app.post("/parse/file", response_model=ResumeData)
async def parse_file_endpoint(
    file: UploadFile = File(...),
    put_additional_given_in_middle: bool = Form(False)
):
    """
    Parses resume from an uploaded PDF or DOCX file.
    """
    try:
        contents = await file.read()
        blocks, links = ingest_document(contents, file.filename or "resume.pdf")
        if not blocks:
            raise HTTPException(status_code=400, detail="Could not extract text from the provided file.")

        result = extractor.extract_from_blocks(
            blocks=blocks,
            annotation_links=links,
            put_additional_given_in_middle=put_additional_given_in_middle
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("workingday_parser.main:app", host="0.0.0.0", port=8000, reload=True)
