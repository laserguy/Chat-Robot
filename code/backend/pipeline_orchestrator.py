from domain_handler.rule_based_classification import RuleBasedHandler
from open_domain_conv_handler.conv_handler_factory import ConvHandlerFactory

from intent_handler.zero_shot_classification import ZSCIntentHandler
from intent_handler.word_embedding_classification import WEIntentHandler
from utterance_structure_checker.utterance_structure_checker import USChecker
from utterance_structure_checker.user_context_handler import UserContextHandler

from utterance_structure_checker.intent_slotfill import response_strings as is_response_strings
from open_domain_conv_handler import constants as odc_constants
from program_response_handler.send_recieve_handler import SendRecieveHandler

from explainability.explain_responses import ExplainResponses

import traceback
import logging
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        self.domain_handler = RuleBasedHandler()
        self.open_domain_handler = ConvHandlerFactory().get_opendomain_conv_handler(odc_constants.FACEBOOK_ENGINE)
        self.intent_handler = WEIntentHandler()
        self.utterance_structure_checker = USChecker()
        self.user_context = UserContextHandler()
        self.exp_response = ExplainResponses()
        self.program_response_handler = SendRecieveHandler()
    
    def send_response(self,text: str)->str:
        out_msg = ""
        try:
            logger.info("input: "+ text)
            text = self.__sentence_preprocessing(text)
            
            # FIND DOMAIN
            in_domain = self.domain_handler.is_inside_domain(text)
            log = "Classified as In-Domain: " + str(in_domain)
            logger.info(log)
            self.exp_response.collect_explanation(log)
            if in_domain == False:
                if self.user_context.is_context_present():
                    log = "Existing task-oriented context cleared"
                    logger.info(log)
                    self.exp_response.collect_explanation(log)
                    self.user_context.clear_context()
                out_msg = self.open_domain_handler.generate_output_text_with_context(text)
                return out_msg
            
            # Clear the open-domain chat history(since it's in domain/task-oriented)
            self.open_domain_handler.clear_history()
            
            # GET INTENT
            intent_label = self.intent_handler.find_intent(text)
            if intent_label is None and not self.user_context.is_context_present():
                log = "No root verb present"
                logger.info(log)
                self.exp_response.collect_explanation(log)
                return is_response_strings.NO_INTENT_FOUND
            
            prev_intent = self.user_context.get_previous_intent() # store the previous intent
            combined_text_flag = False   # If the current utternace is combined with the previous utternace
            
            # IF CONTEXT IS THERE, RESPONSE WITHIN CONTEXT
            if self.user_context.is_context_present():
                log = "Task-oriented context exists"
                self.exp_response.collect_explanation(log)
                logger.info(log)
                if self.user_context.is_response_within_context(text,intent_label):
                    text = self.user_context.combine_response_to_previous_utterance(text,intent_label)
                    if is_response_strings.SENTENCE_STRUCTURE_INCORRECT in text:
                        return text
                    combined_text_flag = True
                else:
                    self.user_context.clear_context()
            
            # Before moving next in the pipeline, make sure intent is available       
            if intent_label is None and combined_text_flag:
                # No intent is there but user context available
                # set the previous intent to be the current intent
                intent_label = prev_intent
            
            logger.info("Intent: " + intent_label)
            self.exp_response.collect_explanation("Intent: " + intent_label)
            # CHECK THE SENTENCE STRUCTURE / CHECK INTENT-WISE SLOTS
            missing = self.utterance_structure_checker.basic_structure_check(text)
            if missing == "":
                log = "Utterance basic structure is correct"
                logger.info(log)
                #self.exp_response.collect_explanation(log)
                out_msg = self.utterance_structure_checker.intent_wise_slot_fill(intent_label, text)
            else:
                out_msg = is_response_strings.SENTENCE_STRUCTURE_INCORRECT + missing
            
            if is_response_strings.SENT_TO_ROBOT_ARM_PROGRAM in out_msg:
                # Send the text to the VerbBot Robot ARM
                log = "Sent to the robotic arm"
                logger.info(log)
                self.exp_response.collect_explanation(log)
                out_msg = self.program_response_handler.send_message(text,intent_label,self.utterance_structure_checker.get_sub_intent())
                #out_msg += text
                return out_msg
            
        except Exception as e:
            print("Exception occurred in (PipelineOrchestrator) pipeline sequence ", e)
            traceback.print_exc()
            out_msg = is_response_strings.SOMETHING_WENT_WRONG
            if self.user_context.is_context_present():
                self.user_context.clear_context()
            
        return out_msg
    
    def get_dependency_tree(self,text: str)->str:
        try:
            text = self.__sentence_preprocessing(text)
            return self.utterance_structure_checker.get_dependency_tree(text)
        except Exception as e:
            print("Exception occurred in (PipelineOrchestrator), calculating dependency tree", e)
    
    def stop(self)->None:
        self.program_response_handler.stop()
    
    # private function        
    def __sentence_preprocessing(self,text:str)->str:
        text = text.lower()
        return text.rstrip('.')