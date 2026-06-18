import os
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from models import ReviewRequest
from services.review_service import review_code, get_review_result, generate_report_for_review
from database import init_db

load_dotenv()

app = FastAPI(title="AI Code Reviewer")

init_db()

HTML_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _render_template(name: str, **kwargs) -> str:
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(HTML_DIR))
    template = env.get_template(name)
    return template.render(**kwargs)


@app.get("/", response_class=HTMLResponse)
async def index():
    return _render_template("index.html")


@app.post("/api/review")
async def create_review(
    request: Request = None,
    code: str = Form(None),
    language: str = Form("python"),
    file: UploadFile = File(None),
):
    if code and file:
        raise HTTPException(400, "Provide either pasted code or a file, not both.")
    if not code and not file:
        raise HTTPException(400, "Provide code to review (paste or upload a file).")

    if file:
        content = await file.read()
        code = content.decode("utf-8")
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext in ("py",):
            language = "python"
        elif ext in ("js", "jsx", "mjs"):
            language = "javascript"

    if not code or not code.strip():
        raise HTTPException(400, "Code cannot be empty.")

    result = review_code(code, language)
    return result.model_dump()


@app.get("/api/review/{review_id}")
async def get_review(review_id: str):
    data = get_review_result(review_id)
    if data is None:
        raise HTTPException(404, "Review not found.")
    return data


@app.post("/api/review/{review_id}/report")
async def download_report(review_id: str, fmt: str = Form("html")):
    try:
        content, content_type, filename = generate_report_for_review(review_id, fmt)
        return Response(content=content, media_type=content_type, headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        })
    except ValueError:
        raise HTTPException(404, "Review not found.")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
