import re
import spacy
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
from tqdm import tqdm

nltk.download('punkt')
nltk.download('stopwords')




class GermanTextProcessing:
     """
     A collection of preprocessing steps specified to the needs of German language.
     """
     def __init__(self):
          with open("data/stopwords-de.txt", "r") as f:
               self.stop_words = set(f.read().split("\n"))
          # self.stop_words = set(stopwords.words("german"))
          self.nlp = spacy.load('de_core_news_sm')

     def clean(self, text: str, lower: bool = False, remove_stopwords: bool = False) -> str:
          text = text.replace('-', ' ')
          words = word_tokenize(text)
          if lower:
               words = [word.lower() for word in words]
          if remove_stopwords:
               words = [
                    word for word in words if word not in self.stop_words
                    ]
          words = [word.strip() for word in words if word.isalnum()]
          return " ".join(words)
     
     
     def tag_pos(self, text: str) -> str:
          mails_lemma = []
          doc = self.nlp(text)
          return ' '.join([x.lemma_ for x in doc])
     
     def batch_run(self, corpus: List[str]):
          corpus_processed = []
          for text in tqdm(corpus):
               text_clean = self.clean(text, remove_stopwords=True)
               text_norm = self.tag_pos(text_clean)
               corpus_processed.append(text_norm)
          return corpus_processed

     
     
     