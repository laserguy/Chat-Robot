from .open_domain_handler import OpenDomainHandler
import openai
from . import constants

"""
    reference: https://platform.openai.com/examples/default-friend-chat
    Requirments:
        OpenAI Key
        It provides 18$ worth of free credits, only for a month
        After that it won't work
        
    Positives: 
        Good descriptive responses
        fast
    Negatives:
        But lack the dialogue state tracking
        Requires internet connection
"""
class OpenATBasedHandler(OpenDomainHandler):
    def __init__(self) -> None:
        super().__init__()
        openai.api_key = constants.OPENAI_API_KEY
        
    def generate_output_text(self,text: str)->str:
        message = ""
        try:
            response = openai.Completion.create(
            engine=constants.OPENAI_ENGLINE,
            prompt=text,
            temperature=constants.TEMPERATURE,
            max_tokens=constants.MAX_TOKENS,
            top_p=constants.TOP_P,
            frequency_penalty=constants.FREQUENCY_PENALTY,
            presence_penalty=constants.PRESENCE_PENALTY
            )
            message = response.choices[0].text.strip()
        
        except Exception as e:
            print("Exception occurred in OpenATBasedHandler: ", e)
            message = constants.NO_INTERNET_CONNECTION
            
        return message