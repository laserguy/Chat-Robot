from .domain_classifier import DomainHandler
from . import constants
import spacy
import csv
from nltk.stem import SnowballStemmer

"""
    This Rule Based Classification is one specific algorithm for handling domain, in case you want to use a different approach then extend
    the DomainHandler interface and write your implementation.
    
    File verbbot_words is a comma separated file containing the most commonly used words in the verbbot domain.
    
    CLASSIFICATION APPROACH:
     - Remove stop words
     - If 80% of the words are part of the verbbot_words file(after 1st step), then the incoming utterance will be classified as IN_DOMAIN
"""
class RuleBasedHandler(DomainHandler):
    def __init__(self)-> None:
        super().__init__()
        self.nlp = spacy.load(constants.SPACY_LANGUAGE_MODEL)
        
        self.verbbot_words = set()
        for w in constants.STOP_EXCEPTIONS:
            self.nlp.Defaults.stop_words.remove(w)
        
        with open(constants.VERBBOT_VOCAB, newline='') as csvfile:
            reader = csv.reader(csvfile)
            row = next(reader)  # read the first (and only) row
            for word in row:
                self.verbbot_words.add(word.strip())
        
    
    def is_inside_domain(self,text: str) -> bool:
        try:
            print("Input Text: ", text)
            processed_text = self.__lemmatize_text(text)
            print("lemmatized text: ", processed_text)
            processed_text = self.__remove_stop_words(processed_text)
            #print("Stop words removed: ",processed_text)
            
            words = processed_text.split()
            words = self.__remove_punctuations(words)
            
            print("After removing stop words ",words)
            count = sum(1 for x in words if x in self.verbbot_words)
            print("IN DOMAIN LEN: ",str(count), "OVERALL LEN", str(len(words)))
            
            # If 80% of words are in the VerbBot dictionary, then its in-domain
            if count / len(words) >= constants.IN_DOMAIN_THRESHOLD:
                return constants.IN_DOMAIN
            
            return constants.OUT_DOMAIN
        except Exception as e:
            print("Exception occurred in RuleBasedHandler: ", e)
            return constants.OUT_DOMAIN
    
    # private function      
    def __remove_stop_words(self,text:str) -> str:
        doc = self.nlp(text)
        tokens = [token.text for token in doc if not token.is_stop]
        output_sentence = ' '.join(tokens)
        return output_sentence
    
    """
        Does bit aggressive stemming, therefore in most cases changes the words completely
        Used for removing plurals
        But better solution was to add plurals in the Verbot vocabulary
    """
    # private function
    def __stemm_text(self,text:str)->str:
        stemmer = SnowballStemmer()
        doc = self.nlp(text)
        stemmed_tokens = []
        for token in doc:
            # Skip the words that are in the exceptions: 
            if token.text in constants.STEMM_EXCEPTIONS:
                stemmed_tokens.append(token.text)
            else:
                stemmed_tokens.append(stemmer.stem(token.text))
        stemmed_sentence = " ".join(stemmed_tokens)
        return stemmed_sentence
    
    # private function
    def __remove_punctuations(self,words:list)->list:
        return [word for word in words if word not in [",", ".","?"]]
    
    # private function
    def __lemmatize_text(self,text:str)->str:
        try:
            doc = self.nlp(text)
            lemmatized_tokens = []
            for token in doc:
                if token.text in constants.LEMM_EXCEPTIONS:
                    lemmatized_tokens.append(token.text)
                elif token.lemma_ == '-PRON-':            # Pronouns are lemmatized to this so don't consider them
                    lemmatized_tokens.append(token.text)
                else:
                    lemmatized_tokens.append(token.lemma_)
            lemmatized_sentence = " ".join(lemmatized_tokens)
            return lemmatized_sentence
        except Exception as e:
            print("Exception occurred in Lemmatization")