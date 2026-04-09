from typing import List

from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    news: str


class URLAnalyzeRequest(BaseModel):
    url: HttpUrl


class SHAPResponse(BaseModel):
    important_words: List[str]
    weights: List[float]


class AnalyzeResponse(BaseModel):
    prediction: str
    confidence: float
    evidence: List[str]
    explanation: str
    shap: SHAPResponse
    source_text: str
