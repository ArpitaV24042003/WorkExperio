# backend/app/routers/ai.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.ai_client import ai_generate_team, ai_predict_performance, ai_parse_resume

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/generate-team")
def generate_team(payload: dict):
    try:
        return {"team": ai_generate_team(payload)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-performance")
def predict_performance(payload: dict):
    try:
        return {"performance": ai_predict_performance(payload)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        parsed = ai_parse_resume(tmp_path)
        return {"parsed": parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
