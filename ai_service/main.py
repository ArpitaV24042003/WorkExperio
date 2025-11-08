# ai_service/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import traceback

# Import your existing AI functions (adjust names if different)
# These imports assume you moved your Python files into ai_service/ai_model/
# Example: ai_service/ai_model/resume_parsing.py
try:
    from ai_model.resume_parsing import parse_resume
except Exception:
    # If import fails, provide a stub to avoid hard crash during initial testing.
    def parse_resume(_):
        return {"error": "parse_resume not available - check imports"}

try:
    from ai_model.team_formation import generate_team
except Exception:
    def generate_team(_):
        return {"error": "generate_team not available - check imports"}

try:
    from ai_model.team_ps_selection import predict_performance
except Exception:
    def predict_performance(_):
        return {"error": "predict_performance not available - check imports"}

app = FastAPI(title="WorkExperio AI Service")

# Allow cross-origin calls (safe to restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can replace ["*"] with a list of allowed domains
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ai service running"}

@app.post("/api/parse_resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Accepts a file upload (resume). Returns parsed results.
    The parse_resume function in your ai_model should accept raw bytes or text.
    """
    try:
        raw = await file.read()
        # If your parse_resume expects text, decode:
        try:
            parsed = parse_resume(raw)
        except TypeError:
            # maybe parse_resume expects str
            parsed = parse_resume(raw.decode(errors="ignore"))
        return {"parsed": parsed}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_team")
async def generate_team_endpoint(payload: dict):
    """
    Expect a JSON body with input data (e.g., project requirements, candidate ids, etc).
    """
    try:
        result = generate_team(payload)
        return {"team": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict_performance")
async def predict_performance_endpoint(payload: dict):
    """
    Expect JSON input for performance prediction.
    """
    try:
        result = predict_performance(payload)
        return {"performance": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # For local testing only
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
