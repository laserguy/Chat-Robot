from .utterance_s_checker import UtteSChecker
from . import constants
from .intent_slotfill import parse_generator
from .intent_slotfill import constants as is_constants
from .intent_slotfill import response_strings as is_response_strings
from .user_context_handler import UserContextHandler

import spacy
from spacy import displacy
from transformers import pipeline
import traceback

class USChecker(UtteSChecker):
    def __init__(self) -> None:
        super().__init__()
        self.nlp = spacy.load(constants.SPACY_LANGUAGE_MODEL)
        self.ques_answer_model = pipeline('question-answering', model=constants.QUESTION_ANSWER_MODEL, tokenizer=constants.QUESTION_ANSWER_MODEL)
        self.parse_gen_obj = None
        
    def get_dependency_tree(self,text: str) -> str:
        try:
            doc = self.nlp(text)
            svg = displacy.render(doc, style='dep')
            return svg
        except Exception as e:
            traceback.print_exc()
            print("Exception occurred in USChecker", e)
            
    def basic_structure_check(self,text: str) -> str:
        return UserContextHandler().basic_structure_check(text)
    
    def intent_wise_slot_fill(self,intent: str, text: str) -> str:
        try:
            self.parse_gen_obj = parse_generator.ParseGenerator(intent)
            parsed_out = self.parse_gen_obj.parse_and_check_dependency(text)
            
            if is_constants.COMPLETE in parsed_out:
                # Sentence complete send to the program
                return is_response_strings.SENT_TO_ROBOT_ARM_PROGRAM
            
            elif is_constants.INCOMPLETE in parsed_out:
                msg = self.parse_gen_obj.gen_response_for_missing_slots(parsed_out[is_constants.INCOMPLETE],text,self.ques_answer_model)
                # We are asking some information from the user, so we need to hold the previous text(context)
                UserContextHandler().init_context(text,msg,intent)
                return msg
            else:
                return is_response_strings.SOMETHING_WENT_WRONG
        
        except Exception as e:
            traceback.print_exc()
            print("Exception occurred while intent-wise slot filling in USChecker",e)
            return is_response_strings.SOMETHING_WENT_WRONG
    
    # The below function to be called when intent-wise_slot_fill function was called before(everytime)
    def get_sub_intent(self)->str:
        if self.parse_gen_obj == None:
            print("Function get_sub_intent called without initialization of parse generator")
            return Exception
        return self.parse_gen_obj.sub_intent