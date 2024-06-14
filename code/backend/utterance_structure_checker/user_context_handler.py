"""
    This file will handle the user-response to our questions
    
    For example:
        User Utterance: Move the red cube.
        VerbBot response: Where do you want to move the red cube?
        User response: on top of the container
        
    Therefore, this user response has to be combined with user previous utterance
    So overall this is sent to the robot program.
    => Move the red cube on top of the container
    
    Therefore below class is only to be initiated when VerbBot generates a question
    Below is a singleton class, since we want to hold the previous_utterance and question that VerBot asked
    and these variables shouldn't be created again and again whenever we create a new object
    We have to create the object at two different places, therefore making it singleton was better choice
"""

from . import constants
from .intent_slotfill import response_strings as is_response_strings

import spacy
import string

class UserContextHandler:
    _self = None
    _nlp = None
    _initialized = False

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self
    
    def __init__(self):
        if not self._initialized:
            self._nlp = spacy.load(constants.SPACY_LANGUAGE_MODEL)
            self._initialized = True
            self.previous_utterance = ""
            self.question = ""
            self.previous_intent = ""
    
    def init_context(self,text: str,question: str,intent: str)-> None:
        if text[-1] == '.':
            text = text[:-1]
        self.previous_utterance = text.rstrip(string.punctuation)
        self.question = question
        self.previous_intent = intent
        
    def clear_context(self) -> None:
        self.previous_utterance = ""
        self.question = ""
        self.previous_intent = ""
        
    def get_previous_intent(self) -> str:
        return self.previous_intent
        
    def is_context_present(self) -> bool:
        if self.previous_utterance != "" and self.question != "":
            return True
        return False
    
    def is_response_within_context(self,text: str, intent: str) -> bool:
        ques = self.question.split()[0].lower()
        within_context = False
        
        if intent is None:
            within_context = True
        elif intent == self.previous_intent:
            if ques == 'what':
                # check if dobj is present and no pobj is present
                if self.__dobj_present(text) and not self.__pobj_present(text):
                    within_context = True
            elif ques == 'where':
                # check if pobj is present but no dobj is present
                if self.__pobj_present(text) and not self.__dobj_present(text):
                    within_context = True
                    
            text = self.__get_text_after_verb(text)
                
        if within_context == True:
            # The length of the sentence shouldn't be more than a certain number
            if len(text.split()) > constants.CONTEXT_LENGTH_THRESHOLD:
                within_context = False
                
        return within_context
    
    def combine_response_to_previous_utterance(self,text: str,intent: str)->str:
        # Did question contain 'What' or 'Where', based on that the response would be combined
        ques = self.question.split()[0].lower()
        print("Question "+ ques)
        combined_utterance = ''
        
        if intent is not None:
            # If the current utterance contains the intent(root verb), then the "info" we need is after the root verb
            """
                prev_utterance: Can you please move
                VerbBot: What do you want to move?
                current_utterance: Move the red cube
                
                In above example the user response "Move the red cube", the intent is there: "move"
                The "info" we need is "red cube"
            """
            text = self.__get_text_after_verb(text)
        
        if ques == 'what':
            # Add the response right next to the root verb of the previous utterance
            combined_utterance = self.__insert_after_root_verb(text)
            
        elif ques == 'where':
            # Check for the basic structure of the text, all prep have a pobj?
            missing = self.basic_structure_check(text)
            if missing != "":
                return is_response_strings.SENTENCE_STRUCTURE_INCORRECT + missing
            # Add the response at the end of the previous utterance
            combined_utterance = self.previous_utterance + ' ' + text
        
        print("Combined utterance :" + combined_utterance)
        self.clear_context()
        return combined_utterance
    
    
    # Check for basic dependencies, e.g each ADP(preposition) should be connected with the pobj     
    def basic_structure_check(self,text: str) -> str:
        missing = ""
        doc = self._nlp(text)
        for token in doc:
            # Check for the prepostion, in some cases prepositions can have a ROOT dependency as well
            # e.g: "into the box" -> Here 'into' is ROOT
            if token.pos_ == "ADP" and (token.dep_== "prep" or token.dep_ == "ROOT"):
                try:
                    for child in token.children:
                        # The pobj should be noun/ a proper noun or a pronoun
                        if (child.pos_ == "NOUN" or child.pos_ == "PROPN" or child.pos_ == "PRON") and child.dep_ == "pobj":
                            missing = ""
                            break
                        else:
                            missing = "NOUN"
                    else:
                        if len(list(token.children)) == 0:
                            missing = "NOUN"
                except StopIteration as e:
                    missing = "NOUN"
                    
        return missing
    
    # private function
    def __dobj_present(self,text: str) -> bool:
        doc = self._nlp(text)
        
        for token in doc:
            if token.dep_ == "dobj" and (token.pos_ == "NOUN" or token.pos_ == "PROPN"):
                return True
            
        return False
    
    # private function
    def __pobj_present(self,text: str) -> bool:
        doc = self._nlp(text)
        
        for token in doc:
            if token.dep_ == "pobj" and (token.pos_ == "NOUN" or token.pos_ == "PROPN"):
                return True
            
        return False
    
    # private function
    def __get_text_after_verb(self,text: str) ->str:
        doc = self._nlp(text)
        
        for token in doc:
            if token.pos_ == 'VERB' and token.dep_ == 'ROOT':  # Check if the token is a verb
                verb_index = token.i
                return ' '.join([token.text for token in doc[verb_index+1:]])

        return ""
    
    # private function
    def __insert_after_root_verb(self,text:str) -> str:
        doc = self._nlp(self.previous_utterance)
        
        # Find the root verb in the first sentence
        root_verb = next((token for token in doc if token.pos_ == 'VERB' and token.dep_ == 'ROOT'), None)
        root_verb_index = root_verb.i
        
        # Insert the second sentence right after the root verb token
        combined_utterance = ' '.join([token.text for i, token in enumerate(doc) if i <= root_verb_index] +
                                     text.split() +
                                     [token.text for i, token in enumerate(doc) if i > root_verb_index])
        
        return combined_utterance
            
            
            
    
    
    
    
        
    
    
