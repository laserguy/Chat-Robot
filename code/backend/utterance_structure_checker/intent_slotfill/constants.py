import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPENDENCY_CHAIN_JSON = os.path.join(BASE_DIR, 'dependency_chain.json')

SPACY_LANGUAGE_MODEL = 'en_core_web_sm'

# SENTENCE TAGS AND DEPENDENCIES
NOUN_PROPN = 'NOUN/PROPN'

# INTENT LABLES

MOVE = "move"
# SUB LABELS
MOVE_PREP = "prep next to root verb"
MOVE_BET = "between prep used"

POUR = "pour"
# SUB LABEL
POUR_EMPTY = "pour with empty word"             # In case empty word is used e.g "Empty the test tube into the beaker"

SHAKE = "shake"
# SUB LABEL
SHAKE_TIMES = "shake many times"                # "Shake the test tube 10 times"

CLEAN = "clean"
# SUB LABEL
CLEAN_WITH = "clean with accessory object"

OPEN = "open"
CLOSE = "close"

BASIC = "basic"                                 # All intents have a basic by default

# For status of sentence structure
COMPLETE = 1
INCOMPLETE = 0
FAILURE = -1