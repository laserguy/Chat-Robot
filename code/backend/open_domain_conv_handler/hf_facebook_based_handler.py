from .open_domain_handler import OpenDomainHandler
from . import constants

from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
import torch

"""
    Reference: https://huggingface.co/docs/transformers/model_doc/blenderbot
    https://parl.ai/docs/tutorial_chat_service.html
        - The above reference contains a recipe to build a open-domain chat-bots but they run in on-terminal and also have DST
        - The code written here(python),does not have the ability of state tracking
    
    positives:
        No key required
        open source
    negatives:
        slow, since model downloaded locally
        bit more slower compared to DialoGPT, it also asks questions to the user, but without DST it is worthless
        not very descriptive responses
"""

class HfFacebookBasedHandler(OpenDomainHandler):
    def __init__(self) -> None:
        super().__init__()
        self.tokenizer = BlenderbotTokenizer.from_pretrained(constants.FACEBOOK_ENGINE)
        self.model = BlenderbotForConditionalGeneration.from_pretrained(constants.FACEBOOK_ENGINE, add_cross_attention=False)
        
        # history to be used when generating responses with context
        self.history = []
        
    def generate_output_text(self,text: str)->str:
        message = ""
        try:
            inputs = self.tokenizer(text + self.tokenizer.eos_token, return_tensors='pt')
            res = self.model.generate(**inputs,max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
            message = self.tokenizer.decode(res[0],skip_special_tokens=True)
        
        except Exception as e:
            print("Exception occurred in HfFacebookBasedHandler: ", e)
            message = constants.GENERIC_MESSAGE
            
        return message
    
    def generate_output_text_with_context(self, text: str) -> str:
        message = ""
        try:
            new_user_input_ids = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors='pt')

            # append the new user input tokens to the chat history
            bot_input_ids = torch.cat([torch.LongTensor(self.history), new_user_input_ids], dim=-1)

            # generate a response 
            self.history = self.model.generate(bot_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id).tolist()

            # convert the tokens to text, and then split the responses into the right format
            response = self.tokenizer.decode(self.history[0]).replace("<s>","").split("</s>")
            message = [(response[i], response[i+1]) for i in range(0, len(response), 2)]  # convert to tuples of list
            print(message)
        
        except Exception as e:
            print("Exception occurred in HfFacebookBasedHandler: ", e)
            message = constants.GENERIC_MESSAGE
            
        return message
    
    def clear_history(self):
        self.history = []
    