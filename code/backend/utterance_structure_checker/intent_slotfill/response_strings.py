# GENERATE RESPONSES
SENT_TO_ROBOT_ARM_PROGRAM = "Sent: "
SOMETHING_WENT_WRONG = "Something went wrong"
SENTENCE_STRUCTURE_INCORRECT = "Sentence structure is incorrect, missing "
NO_INTENT_FOUND = "Sorry, your utterance has no intent"

"""
    Each comma separated element in the sub-intent represents a slot
    Therefore if a slot is missing, appropriate response is returned
"""

RESPONSE_STRING = {
    'move':{
        'basic':[
            'What do you want to move',        # Object slot
            'Where do you want to move'        # location slot
            ],
        'between prep used':[
            'What do you want to move',        # Object slot
            'Where do you want to move',       # location 1 slot
            'Where in between you want to move',  # location 2 slot
        ],
        'from prep used':[
            'What do you want to move',        # Object slot
            'Where from, you want to move',     # location 1 slot
            'Where to, you want to move'        # location 2 slot
            ]
        },
    'pour':{
        'basic':[
            'What do you want to pour',        # Object slot
            'Where do you want to pour'        # location slot
            ],
        'pour with empty word':[
            'What do you want to pour',        # Object slot
            'Where do you want to pour'        # location slot            
        ]
        },
    'shake':{
        'basic':[
            'What do you want to shake',        # Object slot
            ],
        'shake many times':[
            'What do you want to shake',        # Object slot
            'How many times to shake',          # Count slot
        ]
        },
    'open':{
        'basic':[
            'What do you want to open',        # Object slot
        ]
        },
    'close':{
        'basic':[
            'What do you want to close',        # Object slot
        ]
        },
    'clean':{
        'basic':[
            'What do you want to clean',        # Object slot
            ],
        'clean with accessory object':[
            'What do you want to clean',        # Object slot
            'With what you want to clean',      # Accessory slot
        ]
    }
}


SLOT_NAMES = {
    'move':{
        'basic':[
            'What',        # Object slot
            'Where'        # location slot
            ],
        'between prep used':[
            'What',        # Object slot
            'Where',       # location 1 slot
            'Between',     # location 2 slot
        ],
        'from prep used':[
            'What',        # Object slot
            'From where',  # location 1 slot
            'To where'     # location 2 slot 
            ]
        },
    'pour':{
        'basic':[
            'What',        # Object slot
            'Where'        # location slot
            ],
        'pour with fill word':[
            'What',        # Object slot
            'Where'        # location slot            
        ]
        },
    'shake':{
        'basic':[
            'What',        # Object slot
            ],
        'shake many times':[
            'What',        # Object slot
            'Count',          # Count slot
        ]
        },
    'open':{
        'basic':[
            'What',        # Object slot
        ]
        },
    'close':{
        'basic':[
            'What',        # Object slot
        ]
        },
    'clean':{
        'basic':[
            'What',        # Object slot
            ],
        'clean with accessory object':[
            'What',        # Object slot
            'With',      # Accessory slot
        ]
    }
}