from typing import List

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import os
import requests

from src.config import settings
from src.core.logger import logger


class ReasonerService:
    def __init__(self) -> None:
        self.prompt_template = (
            "You are a fact-checking AI system.\n\n"
            "News:\n{news}\n\n"
            "Prediction:\n{prediction}\n\n"
            "Evidence:\n{evidence}\n\n"
            "Explain clearly:\n"
            "1) Why this news may be fake or real\n"
            "2) Mention contradictions and uncertainty\n"
            "3) Keep language concise for a general audience"
        )

    def _build_llm(self):
        provider = settings.llm_provider.lower()
        if provider == "openai":
            from langchain_openai import ChatOpenAI

            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
            return ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model, temperature=0.2)

        if provider == "groq":
            from langchain_groq import ChatGroq

            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is required for Groq provider.")
            return ChatGroq(api_key=settings.groq_api_key, model_name=settings.groq_model, temperature=0.2)

        # Fast preflight avoids long hangs when Ollama daemon is not running.
        if provider == "ollama":
            health_url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
            try:
                requests.get(health_url, timeout=2)
            except requests.RequestException as exc:
                raise ValueError(f"Ollama is unreachable at {settings.ollama_base_url}: {exc}") from exc

        from langchain_ollama import ChatOllama

        return ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url, temperature=0.2)

    def generate_explanation(self, news: str, prediction: str, evidence: List[str]) -> str:
        formatted_prompt = self.prompt_template.format(
            news=news,
            prediction=prediction,
            evidence="\n".join(evidence) if evidence else "No external evidence available.",
        )
        llm_enabled = os.getenv("ENABLE_LLM", "0").strip() == "1"
        if not llm_enabled:
            evidence_note = (
                f"Top retrieved evidence count: {len(evidence)}."
                if evidence
                else "No external evidence could be retrieved."
            )
            return (
                f"Model prediction is {prediction}. "
                f"This result is based on TF-IDF + Logistic Regression signal patterns. "
                f"{evidence_note} "
                "Detailed LLM explanation is disabled. Set ENABLE_LLM=1 to enable it."
            )

        try:
            llm = self._build_llm()
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(llm.invoke, formatted_prompt)
            try:
                response = future.result(timeout=20)
            except FutureTimeoutError:
                future.cancel()
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            else:
                executor.shutdown(wait=False)
            return response.content
        except FutureTimeoutError:
            logger.warning("ReasonerService timed out after 20s; returning fallback explanation.")
            evidence_note = (
                f"Top retrieved evidence count: {len(evidence)}."
                if evidence
                else "No external evidence could be retrieved."
            )
            return (
                f"Model prediction is {prediction}. "
                f"This result is based on TF-IDF + Logistic Regression signal patterns. "
                f"{evidence_note} "
                "LLM explanation timed out, so this fallback explanation is shown."
            )
        except Exception as exc:
            logger.exception("ReasonerService failed: %s", exc)
            # Deterministic fallback keeps API usable without LLM dependencies.
            evidence_note = (
                f"Top retrieved evidence count: {len(evidence)}."
                if evidence
                else "No external evidence could be retrieved."
            )
            return (
                f"Model prediction is {prediction}. "
                f"This result is based on TF-IDF + Logistic Regression signal patterns. "
                f"{evidence_note} "
                "LLM explanation is currently unavailable due to provider/dependency configuration."
            )
