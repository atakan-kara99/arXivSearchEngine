
"""
Class for searching and ranking results
by using the retrieval model QL.
"""
import linecache
import os

from .settings import *
from .utils import *
from .posting import *


class Search:

    """
    Loads parts of the dictionary into the main memory.
    Use binary search for looking up.
    If the term is not in the main memory, load the part between two terms (interleaving).
    Use also binary search on the loaded part.
    """
    def load_data_to_dict(self, meta_name):
        self.dictionary = {}
        cntr = 0
        with open(os.path.dirname(os.path.realpath(__file__)) + os.sep + meta_name+INDEX_SUFFIX, 'r', encoding="utf8") as index:
            for line in index:
                content = line.split(' ')
                self.dictionary[content[0]] = content[1]
        return

    # ------------------------------ ranking ------------------------------

    """
    Method for ranking single keyword search results
    """
    def singleKeywordRanking(self, posting_lists: list) -> list:
        author_postings = posting_lists[0]
        title_postings = posting_lists[1]
        abstract_postings = posting_lists[2]
        allIDs = set()
        for posting in posting_lists:
            allIDs = allIDs.union(posting.getAllIDs())
        dict = {}
        for id in allIDs:
            numOfTokens = 0
            for posting in posting_lists:
                numOfTokens += posting.getNumOfTokensFor(id)
            authorOccur = author_postings.getOccurrencesFor(id)
            titleOccur = title_postings.getOccurrencesFor(id)
            abstractOccur = abstract_postings.getOccurrencesFor(id)
            first = 0.8*(2*authorOccur + 3*titleOccur + abstractOccur) / numOfTokens
            second = 0.2*(abstractOccur + titleOccur + abstractOccur) / COUNT_OF_ALL_WORDS
            rankValue = first + second
            dict[id] = rankValue
        return dict

    """
    Method for ranking of multiple keyword search results.
    Uses single keyword ranking.
    """
    def multipleKeywordRanking(self, postings_lists: list):
        dictLists = [self.singleKeywordRanking(posting_list) for posting_list in postings_lists]
        resDict = {}
        for dict in dictLists:
            for key in dict:
                if key in resDict:
                    resDict[key] += dict[key]
                else:
                    resDict[key] = dict[key]
        return resDict

    """
    Method for sorting a dictionary by its values in DESC order
    """
    def sortDict(self, dict: dict):
        sortDict = sorted(dict.items(), key=lambda x: x[1], reverse=True)
        sortedIDs = [item[0] for item in sortDict]
        return sortedIDs
    
    """
    Method for ranking phrase search
    """
    def phraseRanking(self):
        dict = {}
        for id in self.occurInDoc:
            first = self.occurInDoc[id] / self.tokensInDoc[id]
            second = self.occurInCorp / COUNT_OF_ALL_WORDS
            rankValue = first + second
            dict[id] = rankValue
        return dict

    """
    Method for ranking facetted search
    """
    def facettedRanking(self, posting_list: list, meta: int) -> list:
        dict = {}
        for id in posting_list.getAllIDs():
            numOfTokens = posting_list.getNumOfTokensFor(id)
            occur = posting_list.getOccurrencesFor(id)
            first = (occur * self.multiplier(meta)) / numOfTokens
            second = occur / COUNT_OF_ALL_WORDS
            rankValue = first + second
            dict[id] = rankValue
        return dict

    # ------------------------------ searching ------------------------------ 

    """
    Single keyword search for a specific index type
    """
    def singleKeywordSearchIn(self, meta_data: str, term: str) -> list:
        preprocessedTerm = preprocessing(term)
        if preprocessedTerm != []:
            preprocessedTerm = preprocessedTerm[0]
        else:
            preprocessedTerm = ''
        self.load_data_to_dict(meta_data)
        keys = list(self.dictionary.keys())
        if binary_search(preprocessedTerm, keys):
            # get the posting list
            posting_str = linecache.getline(os.path.dirname(os.path.realpath(__file__)) + os.sep + meta_data+POSTING_SUFFIX, int(self.dictionary[preprocessedTerm])+1)
            posting_list = Posting(term, meta_data, posting_str)
        else:
            posting_list = Posting(term, meta_data, '')
        return posting_list

    """
    Single keyword search for all index types simultaniously
    """
    def singleKeywordSearch(self, keyword: str) -> list:
        author_postings = self.singleKeywordSearchIn('author', keyword)
        title_postings = self.singleKeywordSearchIn('title', keyword)
        abstract_postings = self.singleKeywordSearchIn('abstract', keyword)
        return [author_postings, title_postings, abstract_postings]

    """
    Multiple keyword search by using the single keyword search
    """
    def multipleKeywordSearch(self, keywords: list) -> list:
        return [self.singleKeywordSearch(term) for term in keywords]

    # Methods for boolean search, DOES NOT WORK!!!
    """
    ids_for_terms = set()

    def getResultSet(self, term: str):
        if term in self.ids_for_term:
            set_of_ids = self.ids_for_terms[term]
        else:
            set_of_ids = self.singleKeywordSearch(term)
            self.ids_for_terms[term] = set_of_ids
        return set_of_ids

    def intersection(self, term1: str, term2: str):
        set_of_ids1 = self.getResultSet(term1)
        set_of_ids2 = self.getResultSet(term2)
        ids_for_search1 = self.getAllIDs(set_of_ids1)
        ids_for_search2 = self.getAllIDs(set_of_ids2)
        return ids_for_search1.intersection(ids_for_search2)

    def union(self, term1: str, term2: str):
        set_of_ids1 = self.getResultSet(term1)
        set_of_ids2 = self.getResultSet(term2)
        ids_for_search1 = self.getAllIDs(set_of_ids1)
        ids_for_search2 = self.getAllIDs(set_of_ids2)
        return ids_for_search1.union(ids_for_search2)

    def booleanSearch(self, query: str):
        self.ids_for_terms = {}
        pass
    """

    """
    Class variables for the phrase search algorithm
    """
    postingDict = {}
    splitQuery = []
    occurInDoc = {}
    occurInCorp = 0
    tokensInDoc = {}

    """
    Returns the multiplier of a meta data
    author -> 2
    title -> 3
    abstract -> 1
    """
    def multiplier(self, meta: int) -> int:
        if meta == 2:
            return 1
        elif meta == 1:
            return 3
        else:
            return 2

    """
    Recursive method for checking if the next term in the phrase occures
    after the previous term
    e.g.: 1027588, 9, 0, 1 .. if true -> 1027588, 10, 0, 2
    """
    def checkOccurrenceAt(self, id: int, pos: int, meta: int, currQueryIndex: int) -> None:
        if currQueryIndex >= len(self.splitQuery):
            self.occurInCorp += 1
            multiplier = self.multiplier(meta)
            term = self.splitQuery[currQueryIndex-1]
            tokensInDoc = self.postingDict[term][meta].getNumOfTokensFor(id)
            if id in self.occurInDoc:
                    self.occurInDoc[id] += 1*multiplier
                    self.tokensInDoc[id] += tokensInDoc
            else:
                    self.occurInDoc[id] = 1*multiplier
                    self.tokensInDoc[id] = tokensInDoc
        else:
            term = self.splitQuery[currQueryIndex]
            if not (term in self.postingDict):
                self.postingDict[term] = self.singleKeywordSearch(term)
            posting = self.postingDict[term][meta]
            positions = posting.getAllPositionsFor(id)
            if pos in positions:
                self.checkOccurrenceAt(id, pos+1, meta, currQueryIndex+1)

    """
    Method for the phrase search
    """
    def phraseSearch(self, query: str) -> None:
        self.tokensInDoc = {}
        self.postingDict = {}
        self.occurInDoc = {}
        self.occurInCorp = 0
        self.splitQuery = preprocessing(query)
        firstposting = self.singleKeywordSearch(self.splitQuery[0])
        self.postingDict[self.splitQuery[0]] = firstposting
        for meta in range(3):
            splitposting = firstposting[meta]
            ids = splitposting.getAllIDs()
            for id in ids:
                positions = splitposting.getAllPositionsFor(id)
                for pos in positions:
                    self.checkOccurrenceAt(id, pos+1, meta, 1)