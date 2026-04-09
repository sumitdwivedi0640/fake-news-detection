from src.services.classifier import ClassifierService

classifier = ClassifierService()


def predict_news(text):
    return classifier.predict(text)
