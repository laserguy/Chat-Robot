import queue
import json
import sys

from .dependency_parser import DependencyParser

from .communicator import IOSocket
from .issues import OutputUtterance
from . import constants
sys.path.append('../utterance_structure_checker/intent_slotfill')
from utterance_structure_checker.intent_slotfill import response_strings

class SendRecieveHandler:
    def __init__(self, attempts: int = None)->None:
        self.program_connector = IOSocket(constants.IP, constants.PORT)
        self.program_connector.connect_blocking(attempts)
        self.dependency_parser = DependencyParser('en', 'spacy_stanza')
        
    def stop(self)->None:
        if self.program_connector is not None:
            self.program_connector.stop()
        self.program_connector = None
    
    def send_message(self,text: str, intent:str,sub_intent: str)->str:
        message = self.__generate_message(text,intent,sub_intent)
        self.program_connector.send_message(json.dumps(message))
        return self.__get_incoming_message()
        
    def __generate_message(self,text:str,intent:str,sub_intent: str)->dict:
        message = {}
        message['instruction'] = text
        message['intent'] = intent
        message['slots'] = response_strings.SLOT_NAMES[intent][sub_intent]
        message['type'] = "speech"
        for doc in self.dependency_parser.parse([text]):
            j = doc.to_json()
            j['coref_chains'] = [{"most_specific_mention_index": chain.most_specific_mention_index,
                 "token_indices": [m.token_indexes for m in chain.mentions]}
                for chain in doc._.coref_chains.chains]
            message['dep_tree'] = j
        
        return message

    def __get_incoming_message(self)->str:
        try:
            request = self.program_connector.try_to_receive(timeout=20)
        except KeyboardInterrupt:
            return constants.KEYBOARD_INTERRUPT
        except queue.Empty:
            print("Here I am")
            return constants.SOMETHING_WENT_WRONG
        if request == '':
            print("Hier bin ich")
            return constants.SOMETHING_WENT_WRONG
        try:
            msg_json = json.loads(request)
        except json.JSONDecodeError:
            return constants.SOMETHING_WENT_WRONG
        print(msg_json)
        output_utterance = OutputUtterance(issue_object=msg_json["message"])
        return output_utterance.issue.to_utterance()
        