from .intent_handler import IntentHandler
from . import constants

import spacy
from sklearn.metrics.pairwise import cosine_similarity


class WEIntentHandler(IntentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.nlp = spacy.load(constants.SPACY_LANGUAGE_MODEL)
        
    def find_intent(self, text: str) -> str:
        try:
            doc = self.nlp(text)
            root = None
            # Find the root of the sentence
            for token in doc:
                if token.dep_ == "ROOT" and token.pos_ == 'VERB':
                    root = token
                    break
            
            if root is None:        # If no actionable intent present(VERB)
                print("No intent found")
                return root
            
            print("root: ", root.text)
            # Check if the root match the existing intent labels
            if root.text in constants.MOVE_INTENT_LABELS:
                return constants.MOVE_INTENT_LABELS[0]
            elif root.text in constants.POUR_INTENT_LABELS:
                return constants.POUR_INTENT_LABELS[0]
            elif root.text in constants.CLEAN_INTENT_LABELS:
                return constants.CLEAN_INTENT_LABELS[0]
            elif root.text in constants.INTENT_LABELS:
                return root.text
            
            # If root doesn't match any of the existing intent labels, find the most similar to root verb
            similarity_scores = []
            for intent in constants.INTENT_LABELS:
                intent_embedding = self.nlp(intent)[0].vector.reshape(1, -1)
                root_embedding = root.vector.reshape(1, -1)
                similarity = cosine_similarity(root_embedding, intent_embedding)[0][0]
                similarity_scores.append(similarity)

            # Find the index of the most similar
            most_similar_index = similarity_scores.index(max(similarity_scores))
            most_similar_intent = constants.INTENT_LABELS[most_similar_index]
            
            print("Most similar intent: ", most_similar_intent)
            return most_similar_intent
        except Exception as e:
            print("Exception occurred in WEIntentHandler: ", e)