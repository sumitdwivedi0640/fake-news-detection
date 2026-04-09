from urllib.parse import urlparse

import re
import requests


class URLExtractorService:
    def extract_article_text(self, url: str) -> str:
        url = str(url)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Invalid URL. Please provide a valid http/https URL.")

        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html = response.text

            # Preferred parser path.
            try:
                from bs4 import BeautifulSoup  # type: ignore

                soup = BeautifulSoup(html, "html.parser")
                paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
                cleaned = " ".join([p for p in paragraphs if p])
                if cleaned.strip():
                    return cleaned.strip()
            except Exception:
                # Regex fallback for environments without bs4.
                text_only = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
                text_only = re.sub(r"<[^>]+>", " ", text_only)
                text_only = re.sub(r"\s+", " ", text_only).strip()
                if text_only:
                    return text_only
        except requests.RequestException as exc:
            raise ValueError(f"Failed to fetch URL content: {exc}") from exc

        raise ValueError("Unable to extract meaningful text from URL.")
