from .open_domain_handler import OpenDomainHandler
from . import constants

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

"""
    Reference: https://huggingface.co/microsoft/DialoGPT-medium?text=Hey+my+name+is+Clara%21+How+are+you%3F
    
    positives:
        No key required
        open source
    negatives:
        slow, since model downloaded locally
        not very descriptive responses
        
        The model starts to break, when we start using the chat history, therefore it's better to use this without
        chat history.
        This will sacrifice the dialogue state tracking, but the open-domain dialogue without history is still possible

"""

class HuggingFaceBasedHandler(OpenDomainHandler):
    def __init__(self) -> None:
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(constants.HUGGINGFACE_ENGINE, padding_side="left")
        self.model = AutoModelForCausalLM.from_pretrained(constants.HUGGINGFACE_ENGINE)
        self.initialized = False
        #self.chat_history_ids = None
        
    def generate_output_text(self,text: str)->str:
        message = ""
        try:
            text_ids = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors='pt')

            # append the text tokens to the chat history
            bot_input_ids = torch.cat([chat_history_ids, text_ids], dim=-1) if self.initialized == True else text_ids
            #self.initialized = True  ----> uncomment it to use chat-history

            # generated a response while limiting the total chat history to 1000 tokens, 
            chat_history_ids = self.model.generate(bot_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)

            # pretty print last ouput tokens from bot
            message = self.tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        
        except Exception as e:
            print("Exception occurred in HuggingFaceBasedHandler: ", e)
            message = constants.GENERIC_MESSAGE
            
        return message