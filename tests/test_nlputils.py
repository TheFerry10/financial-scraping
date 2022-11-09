import unittest
from preprocessing import nlputils

class TestGermanTextProcessing(unittest.TestCase):
    
    def setUp(self):
        self.maxDiff = None
        self.germanTextProcessing = nlputils.GermanTextProcessing()
        self.sample = "Was Analysten von der Amazon-Aktie erwarten"
        self.sample_cleaned = "Was Analysten von der Amazon Aktie erwarten"
        self.sample_cleaned_stopwords_removed = "Was Analysten Amazon Aktie erwarten"
        self.sample_cleaned_stopwords_removed_lemma = "Was Analyst Amazon Aktie erwarten"
        self.sample_pos_solution = "was Analyst Amazon Aktie erwarten"
        
    def test_clean_remove_stopwords(self):
        text_cleaned = self.germanTextProcessing.clean(self.sample, remove_stopwords=True)
        self.assertEqual(text_cleaned, self.sample_cleaned_stopwords_removed)
            
    def test_clean_not_remove_stopwords(self):
        text_cleaned = self.germanTextProcessing.clean(self.sample, remove_stopwords=False)
        self.assertEqual(text_cleaned, self.sample_cleaned)
        
    def test_tag_pos(self):
        pos = self.germanTextProcessing.tag_pos(self.sample_cleaned_stopwords_removed)
        self.assertEqual(pos, self.sample_pos_solution)
        
    def test_batch_run(self):
        samples_processed = self.germanTextProcessing.batch_run([self.sample])
        self.assertEqual(samples_processed, [self.sample_pos_solution])


if __name__ == '__main__':
    unittest.main()
    