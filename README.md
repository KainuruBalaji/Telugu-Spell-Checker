# Probabilistic Spell Checker for the Telugu Language

**Project ID:** A1-SpellChecker-IR-M2025  
**Author:** Kainuru Balaji  
**Roll No:** S20230010112

---

## 1. Project Overview

This project implements a probabilistic spell checker for the Telugu language, built from the ground up in Python. The system is designed to identify misspelled words in a given text, provide a ranked list of potential corrections, and allow the user to interactively choose the best replacement.

The core methodology is based on **Peter Norvig's spell-corrector algorithm**, which leverages a statistical language model derived from a large text corpus. The model's intelligence comes from understanding word probabilities and edit distances.

---

## 2. Description of Modules

The project is organized into two main Python scripts:

### `Model.py`
This script is responsible for the one-time preprocessing of the raw text data to create the spell checker's "brain" or **index**.

* **Functionality:** It parses a large Telugu Wikipedia XML dump using a memory-efficient iterative parser.
* **Language Model:** It tokenizes the text, counts the frequency of every unique word, and builds a comprehensive language model.
* **Noise Filtering:** To ensure accuracy, the script applies a **frequency threshold filter** (words must appear over 100 times). This critical step removes rare words and common spelling errors from the final dictionary.
* **Output:** The final, clean dictionary is saved as `Telugu_WordModel.json` to secondary storage.

### `Telugu_Spell_check.py`
This is the main, user-facing application that performs the spell checking.

* **Architecture:** The script loads the entire index (`Telugu_WordModel.json`) from secondary memory into a `SpellChecker` class instance in main memory for fast lookups.
* **Error Model:** It implements an `edits1` function that generates all possible corrections within one edit distance using the four required operations: **insertion, deletion, substitution, and transposition**.
* **Candidate Ranking:** For any misspelled word, it generates a set of potential corrections and ranks them based on the **probability (frequency)** of the candidate word appearing in the language model.
* **Interactive Correction:** The program features an interactive command-line interface (CLI). For each detected error, it presents the user with a ranked list of the top 5 candidates and allows them to choose the correct replacement.

---

## 3. How to Run the System

### Prerequisites
* Python 3.12
* A Telugu Wikipedia XML dump (e.g., `tewiki-20251001-pages-articles-multistream.xml`)

### Step 1: Build the Language Model (One-Time Setup)
First, create the spell checker index from the corpus.

1.  Place the Wikipedia XML file in the same directory as the Python scripts.
2.  Run the model builder from your terminal:
    ```bash
    python Model.py
    ```
3.  This process may take a significant amount of time. Upon completion, a `Telugu_WordModel.json` file will be created.

### Step 2: Run the Interactive Spell Checker
Once the model exists, you can run the main program.

1.  Execute the script from your terminal:
    ```bash
    python Telugu_Spell_check.py
    ```
2.  The program will load the index and display an interactive menu. Follow the on-screen prompts to test the spell checker.

---

## 4. Link to Data and Model Index

The full Telugu Wikipedia corpus and the generated `Telugu_WordModel.json` can be found in the GitHub repository for this project.

**Link:** https://github.com/KainuruBalaji/Telugu-Spell-Checker.git
