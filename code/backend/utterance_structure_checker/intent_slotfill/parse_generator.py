import json
import spacy

from . import constants
from . import response_strings
import string
import traceback
import logging
logger = logging.getLogger(__name__)

import sys
sys.path.append('../../')
from explainability.explain_responses import ExplainResponses

class ParseGenerator:
    def __init__(self, intent: str)->None:
        self.intent = intent
        dependency_chain = json.load(open(constants.DEPENDENCY_CHAIN_JSON, "r"))
        self.main_chain = dependency_chain[intent]
        self.nlp = spacy.load(constants.SPACY_LANGUAGE_MODEL)
        self.last_token_index = 0
        self.sub_chain = ""
        self.sub_intent = ""
        
    """
        Returns a dictionary mapping
        if sentence complete:
            { 1: [] }                   # empty dictionary
        elif sentence incomplete:
            { 0: [<missing chains>] }   # contains the index of the chains for the intent which are missed
        else:
            {-1: [] }                   # in case of exception, empty dictionary
    """    
    def parse_and_check_dependency(self,text:str)->dict:
        try:
            self.sub_intent = self.find_sub_intent(text)
            self.sub_chain = self.main_chain[self.sub_intent]['chain']
            
            doc = self.nlp(text)
            
            # check if the dependency chain is present in sentence
            """
                matched_chain_len => How many chains inside the sentence were found in the dependency chain json of the sub-intent
                found_chain_pos => The chain is an array, which chains for the current intent is found in the dependency chain json
            """
            chain_len, matched_chain_len = len(self.sub_chain), 0
            
            chain_pos = 0     # index of chain
            found_chain_pos = []
            prev_index = 0
            
            for chain in self.sub_chain:
                # The current iteration continues from where previous iteration stopped (in case when previous dependency chain was present)
                
                for i in range(prev_index, len(doc)):
                    token = doc[i]
                    #print(token.text,token.dep_,token.pos_)
                    flag = self.__recursive_dependency_matcher(token, chain)
                    if flag:
                        prev_index = self.last_token_index
                        matched_chain_len += 1
                        found_chain_pos.append(chain_pos)
                        break
                chain_pos += 1
                
            if matched_chain_len >= chain_len:
                print("Sentence structure complete, can be sent to the program")            
                return {constants.COMPLETE: []}
            else:
                print("Slots missing")
                # taking complement of the found_chain_pos
                return {constants.INCOMPLETE:
                            [x for x in range(chain_len) if x not in found_chain_pos]}                
                        
        except Exception as e:
            print("Error in parse_and_check_dependency in ParseGenerator",e)
            traceback.print_exc()
            return {constants.FAILURE: []}
        
    
    # private helper function
    def __recursive_dependency_matcher(self,token,chain_level)->bool:
        self.last_token_index = token.i
        if token.dep_ == chain_level['dep'] and token.pos_ in chain_level['pos'].split('/'):
            flag = True
        else:
            flag = False

        # Check if both token and chain_level have children
        if "children" in chain_level:
            if bool(list(token.children)) :
                # Check if the children in chain json exists in the children of the token
                for child_chain_level in chain_level['children']:
                    child_flag = ""
                    for child_token in token.children:
                        # Recursively call __recursive_dependency_matcher for each child
                        child_flag = self.__recursive_dependency_matcher(child_token, child_chain_level)
                        
                        if child_flag:    # If child matches, the no need to check further
                            break
                    
                    # If no child matched, then no need to iterate durther in chain json
                    if not child_flag:
                        return False
            else:
                # When chain json has children but sentence doesn't
                return False        
        
        return flag
    
    def find_sub_intent(self,text:str)->str:
        doc = self.nlp(text)
        for sub_intent in self.main_chain:
            # basic sub-intent has no requirements
            # Therefore if no sub-intent is found, then return the basic sub-intent
            if sub_intent == 'basic':
                continue
            
            val = self.main_chain[sub_intent]['requirements']
            for token in doc:
                if token.dep_ == val['dep'] and token.pos_ == val['pos']:
                    if "text" in val and token.text == val['text']:
                        print("sub_intent :" + sub_intent)
                        return sub_intent
                    elif "text" not in val:
                        return sub_intent
                    
        return 'basic'

    def gen_response_for_missing_slots(self, missing_slots_index: list, text: str,ques_answer_model):
        logger.info("Slots missing")
        ExplainResponses().collect_explanation("Slots missing")
        
        missed = ''
        for i in missing_slots_index:
            missed +=  response_strings.SLOT_NAMES[self.intent][self.sub_intent][i] + ' '
        logger.info(missed)
        ExplainResponses().collect_explanation(missed)
            
        # first missing slot index
        index = missing_slots_index[0]
        response = response_strings.RESPONSE_STRING[self.intent][self.sub_intent][index]
       
        text = text.rstrip(string.punctuation)
        doc = self.nlp(text)
        for token in doc:
            if token.dep_ == 'ROOT':
                break
        
        """
        These W questions are to extract the information from the sentence. Using these to generate the responses
        in case some slot is missing.
        For example:
            sentence: Move the red cube
            missing slot: Location, move where?
            response should be: Where do you want to move the red cube?
            
        To generate the above response, we have to get "red cube" from the sentence.
        This can be done using the 'Question-Answer' model, for above sentence asking question:
            Move what?
        And the model gives the response 'red cube', that can be appended with the response strings.  
        """
        
        if len(self.main_chain[self.sub_intent]['chain']) <= 1:
            return response + '?'                   # Since only one slot is there and that is also missing, direct response is fine
        else:
            question = 'what?' if index != 0 else 'where?'
        question = token.text + ' ' + question
        print(question)
        
        QA_input = {
            'question': question,
            'context': text
        }
        
        res = ques_answer_model(QA_input)
        
        # The question was not understood then the response would similar to the context
        # Therefore in suuch case send the response directly
        if res['answer'] == text:
            return response + '?'
        
        return response + ' ' + res['answer'] + '?'
        
        