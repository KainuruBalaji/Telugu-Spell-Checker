

import re
from collections import Counter
import json
import xml.etree.ElementTree as ET


def tokenize(text):
    if not text:
        return []
    return re.findall(r'[\u0C00-\u0C7F]+', text)


def build_model(xml_path, output_path):
    word_counts = Counter()
    print(f"Parsing XML file from: {xml_path} using an iterative parser.")

    context = ET.iterparse(xml_path, events=("start", "end"))
    event, root = next(context)
    namespace = root.tag.split('}')[0].strip('{')
    text_path = f'./{{{namespace}}}revision/{{{namespace}}}text'

    page_count = 0
    for event, elem in context:
        if event == 'end' and elem.tag == f'{{{namespace}}}page':
            text_element = elem.find(text_path)
            if text_element is not None and text_element.text:
                words = tokenize(text_element.text)
                word_counts.update(words)

            page_count += 1
            if page_count % 5000 == 0:
                print(f"Processed {page_count} pages...")

            root.clear()

    print(f"\nProcessing complete. Processed a total of {page_count} pages.")
    print(f"Model initially found {len(word_counts)} unique word tokens.")

    # A strict filter to remove rare words and common spelling errors.
    MIN_FREQUENCY = 100
    filtered_word_counts = {word: count for word, count in word_counts.items() if count > MIN_FREQUENCY}

    print(f"Filtered model to {len(filtered_word_counts)} unique words (frequency > {MIN_FREQUENCY}).")

    print(f"Saving filtered model to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_word_counts, f, ensure_ascii=False, indent=4)
    print("Model building complete. ✨")


if __name__ == '__main__':
    WIKI_XML_PATH = './tewiki-20251001-pages-articles-multistream.xml'
    MODEL_OUTPUT_PATH = 'Telugu_WordModel.json'
    build_model(WIKI_XML_PATH, MODEL_OUTPUT_PATH)