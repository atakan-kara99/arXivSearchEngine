from .settings import *
from nltk.stem import PorterStemmer

"""
Apply the preprocessing on a given document.
Returns list of strings that are:
- tokenized
- normalized
- removed stop words
- stemmed
"""
def preprocessing(document: str) -> list:
    return [PorterStemmer().stem(w)
        for w in word_tokenize(document.lower())
        if w not in STOPWORDS and len(w) > 3]

"""
Returns the position(indices) of a given term in a given document.
TODO: Iterate over the document and store directly the positions.
"""
def get_position_of_term(document: str, term: str):
    occurrences = []
    for pos, curr_elem in enumerate(document):
        if curr_elem == term:
            occurrences.append(pos)
    return occurrences


""" Creates ngrams. """
def create_n_grams( n: int, document: str):
    """
    Creates ngrams based on our tokenized list.
    :param n: the arity of our ngrams.
    :return: the list of our ngrams.
    """
    head_pointer = 0
    ngrams = []
    tokens = preprocessing(document)
    while True:
        if head_pointer + n > len(tokens):
            break
        sub_tokens = tokens[head_pointer:head_pointer+n]
        ngrams.append(tuple(sub_tokens))
        head_pointer += 1
    return ngrams

"""
Implementation of iterative binary search.
"""
def binary_search(elem: str, curr_list : list) -> bool:
    head = 0
    tail = len(curr_list)-1
    middle = (head + tail) // 2
    while head <= tail:
        if elem == curr_list[middle]:
            return True
        if elem < curr_list[middle]:
            tail = middle-1
            middle = (head+tail)//2
        else:
            head = middle+1
            middle = (head+tail)//2
    return False

"""
Method for transforming incoming queries to queries
that are supported by Solr.
"""
def transformQueryForSolr(query: str):
    query = query.lower()
    newQuery = ''
    # Facetted search
    if 'author:' in query:
        newQuery = query.replace('author:', 'authors:')
    elif 'title:' in query or 'abstract:' in query:
        newQuery = query
    # Phrase Search
    elif query[0] == '\"' and query[-1] == '\"':
        newQuery = helpFuncTransformQueryForSolr(query)
    elif ' ' in query:
        query = query.split()
        # Multiple Keyword Search
        for que in query:
            newQuery += helpFuncTransformQueryForSolr(que)
            if que != query[-1]:
                newQuery += ' OR '
    elif not (' ' in query):
        # Single Keyword Search
        newQuery = helpFuncTransformQueryForSolr(query)
    else:
        # If none of the above / Invalid input
        return ''
    return newQuery

def helpFuncTransformQueryForSolr(query: str):
    autQ = 'authors:' + query
    titQ = 'title:' + query
    absQ = 'abstract:' + query
    return autQ + ' OR ' + titQ + ' OR ' + absQ

"""
V byte encoding.
"""
# def v_byte_encoding(num:int):
#     if num < 2**7:
#         return bin(num+128)
#     elif num >= 2**7 and num < 2**14:
#         return bin(1),bin(num+128)
#     elif num >= 2**14 and num < 2*21:
#         pass
#     elif num >= 2**21 and num < 2**28:
#         pass