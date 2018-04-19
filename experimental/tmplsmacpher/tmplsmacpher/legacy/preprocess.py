"""Helper functions for preprocessing corpora.
"""
import logging

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

from utils import DiskCache


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.DEBUG)


RULES = [
    ('---', ' '),
    ('--', ' '),
    ('-', ''),
]


@DiskCache(forceRerun=False)
def preprocessAll(documents, lemmatize=True):
    """Preprocesses a list of plain string documents.
    Applies replacement rules (cleans), tokenizes, and stems 
    a list of plain string documents.

    By default, will lemmatize corpus using the WordNetLemmatizer. 
    If lemmatize is set to False, will stem the corpus using 
    the PorterStemmer. 

    Args:
        documents: list of plain string documents to be preprocessed.

    Returns:
        A list of cleaned and stemmed/lemmatized token lists. 
    """
    logging.info('Raw documents...')
    logging.info(documents)

    logging.info('Cleaning...')
    cleaned = applyRulesToDocuments(documents, RULES)
    logging.info(cleaned)

    logging.info('Tokenizing and removing stopwords...')
    tokenized = tokenizeDocuments(cleaned)
    logging.info(tokenized)

    if lemmatize:
        logging.info('Lemmatizing...')
        preprocessed = lemmatizeTokenLists(tokenized)
        logging.info(preprocessed)

    # Stem instead.
    else:
        logging.info('Stemming...')
        preprocessed = stemTokenLists(tokenized)
        logging.info(preprocessed)

    return preprocessed


def tokenizeDocuments(documents):
    """Tokenizes a list of documents and removes stopwords.
    Tokenization: convert document to individual elements.
    Stopword removal: remove trivial, meaningless words.
        Stop words are common english words that can be deemed extraneous to 
        certain natural language processing techniques and therefore can be 
        filtered out of the training corpus.

    Args:
        document: list of plain string documents to tokenize.

    Returns:
        List of tokenized documents.
    """
    return [_tokenizeDocument(document) for document in documents]


def _tokenizeDocument(document):
    """Converts a single document to lowercase, removes stopwords, 
    and tokenizes.

    Args:
        document: plain string document to be tokenized.

    Returns:
        Tokenized version of document.
    """
    stoplist = set(stopwords.words('english'))
    tokenized = []
    for word in document.lower().split():
        if word not in stoplist:
            tokenized.append(word)
    return tokenized


def applyRulesToDocuments(documents, rules):
    """Used to apply rules to documents.
    Eg. Replacing hyphens with spaces, replacing em dashes, etc.

    Args:
        documents: list of plain string documents to apply rules to.
        rules: list of tuples mapping old patterns to desired new patterns.

    Returns:
        Documents with old patterns replaced with desired new patterns.
    """
    return [_applyRulesToDocument(document, rules) for document in documents]


def _applyRulesToDocument(document, rules):
    """Applies rules to one document.

    Args:
        document: plain string document to apply rules to.
        rules: list of tuples mapping old pattern to desired new patterns.

    Returns:
        Document with old patterns replaced with desired new patterns.
    """
    for (old, new) in rules:
        document = document.replace(old, new)
    return document


def stemTokenLists(tokenLists):
    """Stems a list of token lists.
    Chops off the ends of the words using a rough heuristic process that
    takes into account the length of the word, number of syllables, etc. to 
    chop off the end of a word in the hopes are arriving at its atomic stem.

    Args:
        tokenLists: list of token lists to be stemmed.

    Returns:
        A list of stemmed token lists.
    """
    return [_stemTokenList(tokenList) for tokenList in tokenLists]


def _stemTokenList(tokenList):
    """Stems a single token list. Trims off ends of words in
    the hopes of reducing semantically related words to the same stem.

    Eg. 'chopping', 'chopped', 'chopper' --> 'chop'

    Args:
        tokenLists: the single token list to be stemmed.

    Returns:
        A stemmed token lists.
    """
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokenList]


def lemmatizeTokenLists(tokenLists):
    """Lemmatizes a list of token lists.
    Uses vocubulary and morphological analysis with the aim of
    only removing inflectional endings (eg. 'chopping' vs. 'chopped')
    and returning the dictionary base of a word -- known as the word's 'lemma.'

    Args:
        tokenLists: list of token lists to be lemmatized.

    Returns:
        A list of lemmatized token lists.
    """
    return [_lemmatizeTokenList(tokenList) for tokenList in tokenLists]


def _lemmatizeTokenList(tokenList):
    """Lemmatizes a single token list.

    Args:
        tokenList: the single token list to be lemmatized.

    Returns:
        A lemmatized token list.
    """
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokenList]