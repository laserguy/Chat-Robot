import os

IN_DOMAIN = True
OUT_DOMAIN = False
SPACY_LANGUAGE_MODEL = 'en_core_web_sm'

IN_DOMAIN_THRESHOLD = 0.8

STOP_EXCEPTIONS = {'move'}

"""
    Stemming 
        resistance -> resist
        cylinder   -> cylind
        measuring  -> measur
    Therefore, placed in exception
    
    The purpose of stemming was to make sure that we don't have to add plural words in the vocab
    But it creates more problems
    The above list is tiny compared to all the exceptions
"""
STEMM_EXCEPTIONS = ['resistance','measuring','cylinder','palette','package']

"""
    Lemmatize is better option, as for Verbot vocablary, there are only few exceptions
    maximally => maximally (should be converted to maximum)
	Same for minimally
	measuring => measure. In our case we want to keep it as measuring
"""
LEMM_EXCEPTIONS = ['maximally','minimally','measuring','left','lay']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# The below file also contain the plurals and past tense also
VERBBOT_WORDS = os.path.join(BASE_DIR, 'verbbot_words.csv')

# Below file contains only the root words of the vocab
VERBBOT_VOCAB = os.path.join(BASE_DIR, 'verbbot_vocab.csv')
