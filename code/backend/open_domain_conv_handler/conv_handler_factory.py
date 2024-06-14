from . import constants
from . import open_domain_handler
from . import openai_based_handler
from . import huggingface_based_handler
from . import hf_facebook_based_handler
from . import hf_godel_based_handler

class ConvHandlerFactory:
    def get_opendomain_conv_handler(self, model:str)-> open_domain_handler.OpenDomainHandler:
        if model == constants.OPENAI_ENGLINE:
            return openai_based_handler.OpenATBasedHandler()
        if model == constants.HUGGINGFACE_ENGINE:
            return huggingface_based_handler.HuggingFaceBasedHandler()
        if model == constants.FACEBOOK_ENGINE:
            return hf_facebook_based_handler.HfFacebookBasedHandler()
        if model == constants.GODEL_ENGINE:
            return hf_godel_based_handler.HfGodelBasedHandler()
        