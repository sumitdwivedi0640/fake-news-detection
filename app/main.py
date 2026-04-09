from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.pipeline import FakeNewsPipeline
from src.schemas import AnalyzeRequest, AnalyzeResponse, URLAnalyzeRequest


app = FastAPI(
    title="Fake News Detection API",
    description="Production-grade fake news detection with LangGraph agents and SHAP explainability.",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = FakeNewsPipeline()


@app.get("/")
def home():
    return {"message": "Fake News Detection API Running", "version": "2.0.0"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_news(request: AnalyzeRequest):
    try:
        return pipeline.analyze_text(request.news)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Analysis failed.") from exc


@app.post("/analyze_url", response_model=AnalyzeResponse)
def analyze_url(request: URLAnalyzeRequest):
    try:
        return pipeline.analyze_url(str(request.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="URL analysis failed.") from exc
