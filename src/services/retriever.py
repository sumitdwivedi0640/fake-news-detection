from typing import List

import requests

from src.config import settings
from src.core.logger import logger


class RetrieverService:
    def fetch_news_articles(self, query: str) -> List[str]:
        if not settings.news_api_key:
            logger.warning("NEWS_API_KEY missing. Returning empty evidence.")
            return []

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": settings.news_api_key,
            "language": "en",
            "pageSize": 5,
            "sortBy": "relevancy",
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            evidence = [article.get("title", "").strip() for article in articles if article.get("title")]
            return evidence[:5]
        except requests.RequestException as exc:
            logger.exception("RetrieverService failed to fetch evidence: %s", exc)
            return []
