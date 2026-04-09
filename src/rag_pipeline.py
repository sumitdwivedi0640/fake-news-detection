from src.services.retriever import RetrieverService

retriever = RetrieverService()


def fetch_news_articles(query):
    return retriever.fetch_news_articles(query)
