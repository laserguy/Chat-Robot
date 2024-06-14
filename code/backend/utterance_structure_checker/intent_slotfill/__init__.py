# Intent and Slot filling
# Making the factory pattern for intent wise dependency chain parsing

# Intent specific responses need to be generated


""" 
Guidelines to add intent into the dependency json file 

1 - Intent can consist of multiple sub-intents(check dependency_chain.json file)
2 - Each intent have a "basic" sub-intent apart from other sub-intents, if there are no other sub-intent then only "basic" will be there
3 - Each sub-intent is a list of comma separated slots
4 - When adding a new sub-intent make sure that the slots are unique, i.e two slots can be children  of the same word, add them separately and uniquely
    For example "Shake the cylinder 5 times"
    Here "cylinder" and "times" are children of "Shake", but add them separately
    And when adding the slot of "times" don't start with "ROOT" (Check 'Shake' in the dependency_chain.json)

"""
