from src.services.reasoner import ReasonerService

reasoner = ReasonerService()


def generate_explanation(news, prediction, evidence):
    return reasoner.generate_explanation(news, prediction, evidence)
