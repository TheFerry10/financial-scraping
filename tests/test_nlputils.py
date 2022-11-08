import unittest
from preprocessing import nlputils

class TestGermanTextProcessing(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.germanTextProcessing = nlputils.GermanTextProcessing()
        self.samples = [
            "Amazon-Aktie in Grün: Neues Logistikzentrum in Helmstedt offiziell eröffnet"
            "Was Analysten von der Amazon-Aktie erwarten"
                        ]
        self.samples_cleaned = [
            "Amazon Aktie in Grün Neues Logistikzentrum in Helmstedt offiziell eröffnet"
            "Was Analysten von der Amazon Aktie erwarten"
                        ]
        self.samples_cleaned_stopwords_removed = [
            "Amazon Aktie Grün Neues Logistikzentrum Helmstedt offiziell eröffnet"
            "Was Analysten Amazon Aktie erwarten"
                        ]
        self.samples_cleaned_stopwords_removed_lemma = [
            "Amazon Aktie Grün neu Logistikzentrum Helmstedt offiziell eröffnen"
            "Was Analyst Amazon Aktie erwarten"
                        ]
        
        
        self.sample_pos = "Amazon Aktie in Grün Neues Logistikzentrum in Helmstedt offiziell eröffnet"
        self.sample_pos_solution = "Amazon Aktie in Grün neu Logistikzentrum in Helmstedt offiziell eröffnen"
        
    def test_clean_remove_stopwords(self):
        for sample, solution in zip(self.samples, self.samples_cleaned_stopwords_removed):
            text_cleaned = self.germanTextProcessing.clean(sample, remove_stopwords=True)
            self.assertEqual(text_cleaned, solution)
            
    def test_clean_not_remove_stopwords(self):
        for sample, solution in zip(self.samples, self.samples_cleaned):
            text_cleaned = self.germanTextProcessing.clean(sample, remove_stopwords=False)
            self.assertEqual(text_cleaned, solution)

        
    def test_tag_pos(self):
        pos = self.germanTextProcessing.tag_pos(self.sample_pos)
        print(pos, sep='\n')
        self.assertEqual(pos, self.sample_pos_solution)
        
    def test_batch_run(self):
        samples_processed = self.germanTextProcessing.batch_run(self.samples)
        print(samples_processed)
        self.assertEqual(samples_processed, self.samples_cleaned_stopwords_removed_lemma)

if __name__ == '__main__':
    unittest.main()