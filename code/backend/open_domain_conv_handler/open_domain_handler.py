
from . import constants

class OpenDomainHandler:
    def generate_output_text(self,text: str)->str:
        pass
    
    def generate_output_text_with_context(self,text: str)->str:
        return constants.MODEL_NOT_IMPLEMENTED
    
    def clear_history(self)->None:
        return