import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Setup the project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INCOMING_DIR = BASE_DIR / "incoming"
REPORTS_DIR = BASE_DIR / "reports"
STATIC_DIR = BASE_DIR / "static"

for _dir in [DATA_DIR, INCOMING_DIR, REPORTS_DIR, STATIC_DIR]:
    _dir.mkdir(exist_ok=True)

app = FastAPI(title="AI Analytics MCP Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the existing pipeline runner
from main import run_pipeline

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a data file (CSV or Excel) to the incoming directory."""
    try:
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ["csv", "xlsx", "xls"]:
            return JSONResponse(status_code=400, content={"error": "Only CSV and Excel files are supported."})
        
        save_path = INCOMING_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"filename": file.filename, "message": "File uploaded successfully", "path": str(save_path)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/settings")
async def update_settings(
    nvidia_key: str = Form(""),
    groq_key: str = Form(""),
    deepseek_key: str = Form(""),
    email_sender: str = Form(""),
    email_password: str = Form(""),
    email_receiver: str = Form("")
):
    """Updates the .env file with the provided API keys and email settings."""
    env_content = f"""# API Keys
NVIDIA_API_KEY={nvidia_key}
GROQ_API_KEY={groq_key}
DEEPSEEK_API_KEY={deepseek_key}

# Email Settings
EMAIL_SENDER={email_sender}
EMAIL_PASSWORD={email_password}
EMAIL_RECEIVER={email_receiver}
"""
    env_path = BASE_DIR / ".env"
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
        
    return {"message": "Settings updated successfully"}

@app.post("/api/run")
async def trigger_pipeline(
    filename: str = Form(...),
    domain: str = Form("Sales"),
    send_email: bool = Form(False)
):
    """Runs the analytics pipeline on the selected file for the selected domain."""
    try:
        csv_path = INCOMING_DIR / filename
        if not csv_path.exists():
            return JSONResponse(status_code=404, content={"error": f"File {filename} not found."})
            
        # We need to pass the domain to the pipeline somehow.
        # Since the pipeline was built for sales, we will pass it via an environment variable for now.
        os.environ["DATA_DOMAIN"] = domain
        
        # Run pipeline synchronously (in production we'd use BackgroundTasks, but for simplicity we'll block)
        # Note: the run.py set PYTHONIOENCODING, but since we are running within FastAPI we are good.
        results = run_pipeline(csv_path=str(csv_path), send_mail=send_email)
        
        return {"message": "Pipeline completed successfully", "results": results}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/download/{file_type}")
async def download_result(file_type: str):
    """Downloads generated results."""
    file_map = {
        "dashboard": REPORTS_DIR / "dashboard.html",
        "report": REPORTS_DIR / "report.pdf",
        "csv": DATA_DIR / "cleaned_sales.csv",
        "pbids": REPORTS_DIR / "analytics.pbids",
    }
    
    if file_type not in file_map:
        return JSONResponse(status_code=400, content={"error": "Invalid file type."})
        
    file_path = file_map[file_type]
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not generated yet."})
        
    return FileResponse(path=file_path, filename=file_path.name)

# Mount the static files for the frontend UI
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Make sure we run with UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
