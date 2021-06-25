from nltk.parse import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
import pandas as pd
import urllib.request
import json
from tqdm.auto import tqdm

tqdm.pandas()

class CoreNLPFeatures:
    
    def __init__(self, core_nlp_server_url="http://localhost:9000"):
        self.core_nlp_server_url = core_nlp_server_url

        try:
            urllib.request.urlopen("http://localhost:9000").getcode()
        except urllib.request.URLError as error:
            print("\nERROR: Is the Stanford CoreNLP server running?\nSee the readme\n\n")
            raise

        # general parser for non-implemented features
        self.parser = CoreNLPParser(url=core_nlp_server_url)

        # Neural Dependency Parser
        self.dep_parser = CoreNLPDependencyParser(url=core_nlp_server_url)

    def _is_sentence_passive(self, sentence) -> bool:
        """
        returns bool

        Uses dep parser to identify whether a sentence has passive dependencies.
        Then it is considered in passive writing style.
        """
        parses = self.dep_parser.parse(sentence.split())
        for parse in parses:
            for governor, dep, dependent in parse.triples():
                if dep.endswith(":pass"):
                    return True
        return False

    # def _get_sentiment_value(self, sentence) -> int:
    #     """
    #     returns integer sentiment value 0-4 (negative to positive)
    #     """
    #     properties = {
    #         'annotators': 'sentiment',
    #         'pipelineLanguage': 'en',
    #         'outputFormat': 'json'
    #     }
    #     annotation = self.parser.api_call(sentence, properties=properties)
        
    #     # in case of multiple sentences, just returning the first to avoid issues.
    #     # returns a value from 0-4
    #     return int(annotation['sentences'][0]['sentimentValue'])

    # def _get_sentiment_distribution(self, sentence) -> list:
    #     """
    #     returns a list of sentiment distributions from negative to positive.
    #     """
    #     properties = {
    #         'annotators': 'sentiment',
    #         'pipelineLanguage': 'en',
    #         'outputFormat': 'json'
    #     }
    #     annotation = self.parser.api_call(sentence, properties=properties)
        
    #     # in case of multiple sentences, just returning the first to avoid issues.
    #     return annotation['sentences'][0]['sentimentDistribution']

    def extract_passive_case(self, sentences):
        s = "sentence"
        df = pd.DataFrame(sentences, columns=[s])

        df['is_passive'] = df[s].progress_apply(lambda sent: int(self._is_sentence_passive(sent)))
        

        return (["is_passive"], df)

    def add_all_text_features(self, df, col_sentences):
        (cols, df_sub) = self.extract_passive_case(df[col_sentences])
        df[cols] = df_sub[cols]
        return df
