from .open_domain_handler import OpenDomainHandler
from . import constants

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

"""
    Reference: https://huggingface.co/microsoft/GODEL-v1_1-large-seq2seq?text=Hi.
        https://github.com/microsoft/GODEL
        
    positives:
        No key required
        open source
        Dialogue state tracking(DST)
    negatives:
        slower
        Using dialogue history makes it difficult to change to new topic in conversation
        Might give "inappropriate" results
        Chat history contains the user inputs and the bot reponse, but when the bot uses the current user utterance plus the chat history,
        but is unable to distinguish between what were the user input and what were his/her responses. This makes it give insensible responses.
        USE AT YOUR OWN RISK!!!

"""

class HfGodelBasedHandler(OpenDomainHandler):
    def __init__(self) -> None:
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(constants.GODEL_ENGINE, padding_side="left")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(constants.GODEL_ENGINE)
        self.dialog = []
        
    def generate_output_text(self,text: str)->str:
        message = ""
        try:
            instruction = f'Instruction: given a dialog context, you need to response empathically.'
            # Leave the knowldge empty
            knowledge = ''
            self.dialog.append(text)
            message = self.__generate(instruction,knowledge,self.dialog)
            self.dialog.append(message)
        except Exception as e:
            print("Exception occurred in HuggingFaceBasedHandler: ", e)
            message = constants.GENERIC_MESSAGE
            
        return message
    
    # private function
    def __generate(self,instruction:str, knowledge:str, dialog:list)->str:
        if knowledge != '':
            knowledge = '[KNOWLEDGE] ' + knowledge
        dialog = ' EOS '.join(dialog)
        query = f"{instruction} [CONTEXT] {dialog} {knowledge}"
        input_ids = self.tokenizer(f"{query}", return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=128, min_length=8, top_p=0.9, do_sample=True)
        output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return output