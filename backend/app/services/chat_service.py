from app.services.intent_classifier import IntentClassifier


class ChatService:

    @classmethod
    def process(cls, message):

        capability = IntentClassifier.classify(message)

        return {
            "capability": capability,
            "message": message
        }