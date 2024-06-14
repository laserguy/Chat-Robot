from transformers import pipeline
from .intent_handler import IntentHandler
from . import constants

"""
    Reference: https://huggingface.co/tasks/zero-shot-classification
"""

class ZSCIntentHandler(IntentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.classifier = pipeline(constants.ZERO_SHOT_CLASSIFICATION,
                      model=constants.FACEBOOK_MODEL)
        
    def find_intent(self, text: str) -> str:
        try:
            score_dict = self.classifier(text, constants.INTENT_LABELS)
            max_score_index = score_dict['scores'].index(max(score_dict['scores']))
            max_score_label = score_dict['labels'][max_score_index]
            print("Intent: {} score: {}".format(max_score_label,score_dict['scores'][max_score_index]))
            
            # TODO: See if there is a need to put a threshold for the intent i.e If the score is higher than the  threshold
            # then only we have a intent, otherwise there will be no intent in the sentence
            
            return max_score_label
        except Exception as e:
            print("Exception occurred in ZSCIntentHandler: ", e)