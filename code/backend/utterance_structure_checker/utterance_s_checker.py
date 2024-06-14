
class UtteSChecker:
    def get_dependency_tree(self,text: str)->str:
        pass
    
    """
        Checks if the basic dependencies are present in the text.
    """
    def find_missing_dependencies(self,text: str)->str:
        pass
    
    """
        For each intent checks all slots are fill
        If not filled then generates the appropriate response
    """
    def intent_wise_slot_fill(self,intent:str,text: str)->str:
        pass