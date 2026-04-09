from src.agents.graph import FakeNewsAgentGraph
from src.core.logger import logger
from src.services.url_extractor import URLExtractorService


class FakeNewsPipeline:
    def __init__(self) -> None:
        self.graph = FakeNewsAgentGraph()
        self.url_extractor = URLExtractorService()

    def analyze_text(self, news: str) -> dict:
        if not news or not news.strip():
            raise ValueError("News text cannot be empty.")

        # Keep inference bounded for latency and stability.
        normalized_news = news.strip()
        max_chars = 6000
        if len(normalized_news) > max_chars:
            normalized_news = normalized_news[:max_chars]

        logger.info("Running text analysis pipeline.")
        result = self.graph.run(normalized_news)
        return {
            "prediction": result.get("prediction", "UNKNOWN"),
            "confidence": result.get("confidence", 0.0),
            "evidence": result.get("evidence", []),
            "explanation": result.get("explanation", "No explanation available."),
            "shap": result.get("shap", {"important_words": [], "weights": []}),
            "source_text": normalized_news,
        }

    def analyze_url(self, url: str) -> dict:
        logger.info("Running URL analysis pipeline for: %s", url)
        content = self.url_extractor.extract_article_text(url)
        if not content or not content.strip():
            raise ValueError("Extracted URL content is empty.")
        return self.analyze_text(content)
