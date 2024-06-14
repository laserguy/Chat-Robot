# coreferee is needed to add it to the pipeline
import coreferee
import language_tool_python
import spacy
import spacy_stanza
import stanza


class DependencyParser:

    def __init__(self, language: str, parser_name: str):
        self.parser = self.__load_parser(language, parser_name)
        self.coref_parser = self.__load_parser(language, "spacy")

    def parse(self, raw_sentences):
        docs = self.dependency_parse(raw_sentences)
        coref_docs = self.coref_parse(raw_sentences)

        # Add coreferences to the docs
        for doc, coref in zip(docs, coref_docs):
            doc._.coref_chains = coref._.coref_chains
        return docs

    def dependency_parse(self, raw_sentences):
        return self.parser.parse(raw_sentences)

    def coref_parse(self, raw_sentences):
        return self.coref_parser.parse(raw_sentences)

    @staticmethod
    def __load_parser(language: str, parser_name: str):
        if parser_name == "spacy":
            if language == "de":
                pipeline = spacy.load("de_core_news_lg")
            elif language == "en":
                pipeline = spacy.load("en_core_web_trf")
            else:
                raise NotImplementedError("Language " + language + " is not yet supported.")
            pipeline.add_pipe('coreferee')
            return ParserSpacy(pipeline)
        elif parser_name == "spacy_stanza":
            return ParserSpacy(spacy_stanza.load_pipeline(language))
        elif parser_name == "stanza":
            return ParserStanza(stanza.Pipeline(language))
        else:
            raise NotImplementedError("Parser Name " + parser_name + " is not yet supported.")


class ParserSpacy:

    def __init__(self, nlp):
        self.nlp = nlp

    def parse(self, sentences):
        return list(self.nlp.pipe(sentences))


class ParserStanza:

    def __init__(self, nlp):
        self.nlp = nlp

    def parse(self, sentences):
        return [self.nlp(". ".join(sentences))]
