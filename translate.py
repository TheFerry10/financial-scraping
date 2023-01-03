from deep_translator import GoogleTranslator
from typing import List

def translate(text_batches: List[str]):
    all_tags_en = []
    error_tags = []
    for text in text_batches:
        try:
            all_tags_en.append(GoogleTranslator(source="de", target="en").translate(text))
        except:
            error_tags.append(text)