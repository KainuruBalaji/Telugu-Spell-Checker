

import json
import re
from typing import Set, List, Dict, Tuple

# A constant defining all characters used for generating spelling variations.
TELUGU_CHARSET = 'అఆఇఈఉఊఋౠఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళక్షఱాిీుూృౄెేైొోౌ్ంఃఁ'


def generate_level_one_edits(word: str) -> Set[str]:
    """
    Creates a set of all possible string variations that are one edit away from the input word.

    This function performs four types of edits:
    1.  Deletions: Removing one character.
    2.  Transpositions: Swapping two adjacent characters.
    3.  Replacements: Changing one character to another from the Telugu charset.
    4.  Insertions: Adding one character from the Telugu charset.
    """
    word_splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]

    deletes = {prefix + suffix[1:] for prefix, suffix in word_splits if suffix}
    transposes = {prefix + suffix[1] + suffix[0] + suffix[2:] for prefix, suffix in word_splits if len(suffix) > 1}
    replaces = {prefix + char + suffix[1:] for prefix, suffix in word_splits if suffix for char in TELUGU_CHARSET}
    inserts = {prefix + char + suffix for prefix, suffix in word_splits for char in TELUGU_CHARSET}

    return deletes.union(transposes, replaces, inserts)


def generate_level_two_edits(word: str) -> Set[str]:
    """
    Creates a set of all possible string variations that are two edits away.
    This is achieved by running the level-one edit generation on each result from the first pass.
    """
    return {e2 for e1 in generate_level_one_edits(word) for e2 in generate_level_one_edits(e1)}


def extract_telugu_tokens(text: str) -> List[str]:
    """
    Splits a string into a list of Telugu words using a Unicode-aware regex.
    """
    if not text:
        return []
    # The regex [\u0C00-\u0C7F] matches the entire Telugu script Unicode block.
    return re.findall(r'[\u0C00-\u0C7F]+', text)


class SpellCorrector:
    def __init__(self, index_file_path: str):
        """
        Initializes the SpellCorrector by loading the language model from a JSON file.
        The language model is a dictionary of word frequencies.
        """
        print(f"Loading language model from: {index_file_path}")
        try:
            with open(index_file_path, 'r', encoding='utf-8') as f:
                self.word_freq_map = json.load(f)
        except FileNotFoundError:
            print(f"Error: Model file '{index_file_path}' not found. Please run your model-building script first.")
            exit()

        self.total_word_count = float(sum(self.word_freq_map.values()))
        print("Language model loaded successfully. ✅")

    def get_word_probability(self, word: str) -> float:
        """Calculates the probability of a word, P(word), based on its corpus frequency."""
        return self.word_freq_map.get(word, 0) / self.total_word_count

    def filter_known_words(self, words: Set[str]) -> Set[str]:
        """Filters a set of words, returning only those present in the language model."""
        return {w for w in words if w in self.word_freq_map}

    def find_correction_candidates(self, word: str) -> List[str]:
        """
        Finds and ranks potential corrections for a given word in order of probability.
        It searches in a prioritized order:
        1. The original word itself (edit distance 0).
        2. Words at one edit distance.
        3. Words at two edit distances.
        """
        # Priority 1: Check if the word is already known and correct.
        known_original = self.filter_known_words({word})
        if known_original:
            return sorted(list(known_original), key=self.get_word_probability, reverse=True)

        # Priority 2: Check for known words at one edit distance.
        level_one_candidates = self.filter_known_words(generate_level_one_edits(word))
        if level_one_candidates:
            return sorted(list(level_one_candidates), key=self.get_word_probability, reverse=True)

        # Priority 3: Check for known words at two edit distances.
        level_two_candidates = self.filter_known_words(generate_level_two_edits(word))
        if level_two_candidates:
            return sorted(list(level_two_candidates), key=self.get_word_probability, reverse=True)

        # Priority 4: If no candidates found, return the original word.
        return [word]

    def process_text_interactively(self, text: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Analyzes a text, identifies misspelled words, and interactively prompts the user
        to choose the correct replacement from a ranked list of candidates.
        """
        source_tokens = extract_telugu_tokens(text)
        corrected_tokens = []
        all_suggestions = {}

        for token in source_tokens:
            if token in self.word_freq_map:
                corrected_tokens.append(token)
            else:
                suggestions = self.find_correction_candidates(token)
                all_suggestions[token] = suggestions

                if len(suggestions) == 1 and suggestions[0] == token:
                    corrected_tokens.append(token)
                    continue

                print(f"\nSuggestion for  ( Showing words by their Ranks)'{token}':")
                top_suggestions = suggestions[:5]

                for i, suggestion in enumerate(top_suggestions):
                    print(f"  {i + 1}) {suggestion}")

                keep_option = len(top_suggestions) + 1
                print(f"  {keep_option}) Keep original word")

                final_word = token
                while True:
                    user_input = input(f"Select an option (1-{keep_option}): ")
                    try:
                        selected_option = int(user_input)
                        if 1 <= selected_option <= len(top_suggestions):
                            final_word = top_suggestions[selected_option - 1]
                            break
                        elif selected_option == keep_option:
                            final_word = token
                            break
                        else:
                            print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")

                corrected_tokens.append(final_word)

        return " ".join(corrected_tokens), all_suggestions


if __name__ == "__main__":
    INDEX_FILE_PATH = 'Telugu_WordModel.json'
    corrector = SpellCorrector(INDEX_FILE_PATH)

    sample_sentences = [
        "భారత్ ఒక మహాన దేసం ఇక్కడ తెలుగు బాష మాట్లాడతారు",
        "ఆకశంలో నక్షత్రాలు మెరుస్తున్నాయి",
        "నాకు చదవడం ఇస్టం",
        "హైదరాబాదు తెలంగాణా రాజధాని",
        "ప్రభుతవం కొత్త పథకాలు ప్రవేశపెట్టింది"
    ]

    while True:
        print("\n" + "#" * 60)
        print("### Telugu Spell Checker - Interactive Menu ###")
        print("#" * 60)

        for i, sentence in enumerate(sample_sentences):
            print(f"  {i + 1}. Check sample: '{sentence}'")

        print("  6. Enter custom text")
        print("  7. Quit")

        choice = input("Enter your choice (1-7): ")
        text_to_process = ""

        if choice == '7':
            print("Exiting program......")
            break
        elif choice in {'1', '2', '3', '4', '5'}:
            text_to_process = sample_sentences[int(choice) - 1]
        elif choice == '6':
            text_to_process = input("Enter your Telugu sentence here: ")
        else:
            print("\n⚠️ Invalid input. Please select a number from 1 to 7.")
            continue

        if text_to_process:
            final_text, all_suggestions_made = corrector.process_text_interactively(text_to_process)

            print("\n" + "-" * 50)
            print("Original Input:  ", text_to_process)
            print("Final Result:    ", final_text)
            print("-" * 50)

        input("\nPress Enter to continue...")