import math
import collections
import os
import sys
import json
import linecache
import zipfile

# using the nltk package for preprocessing
from .index import Index
from .search import Search
from .settings import PATH_TO_ARCHIVE, PATH_TO_JSON, POSTING_SUFFIX, INTERVAL_OF_INSERTING, INDEX_SUFFIX, NUM_OF_BOOGLE_DOCS

"""
My very first search engine with very cool features.
Searching for information,
insert new data and creating very awesome indices.
"""


class SearchEngine:
    def __init__(self):
        # our partial dictionary
        self.dictionary = {}
        # store the interleaved dictionary in here
        self.dictionary_interleaved = {}

    """
    Initializes the index.
    Calls the methods from the class 'Index'.
    For each meta data, we create an own dictionary file
    but all information are stored in the same posting file.
    """

    def create_index(self, meta_data: str):
        # when the files are not existing, just create them
        index = open(meta_data + INDEX_SUFFIX, 'w', encoding="utf8")
        index.close()
        postings = open(meta_data + POSTING_SUFFIX, 'w', encoding="utf8")
        postings.close()
        # first of all open the archive and extract the json file name
        with zipfile.ZipFile(os.path.dirname(os.path.realpath(__file__)) + PATH_TO_ARCHIVE) as corpus:
            json_file = str(corpus.namelist()[0])
            # create index object
            index = Index()
            with corpus.open(json_file) as jObj:
                for cntr, obj in enumerate(jObj):
                    curr_dict = json.loads(obj)
                    """
                    Collect the data and create the dictionary.
                    """
                    index.add_to_dictionary(curr_dict[meta_data], cntr, meta_data)
                    # represents an threshold to clear the queue and write 
                    # the values in the posting list file
                    if cntr % INTERVAL_OF_INSERTING == 0 and cntr != 0:
                        # write in the posting list and clear the data
                        index.add_to_posting_list(meta_data)
                        # -- ONLY DEBUGGING PURPOSE -- #
                        parsed_documents = INTERVAL_OF_INSERTING * (cntr + 1)
                        print(str(cntr) + " documents passed!")
                        print("Size of the dict in MB: ", end="")
                        print(sys.getsizeof(index.dictionary) // 1000000)
                    # -- ONLY DEBUGGING PURPOSE -- #
                    if cntr % 100000 == 0 and cntr != 0:
                        print(f"\033[1m Already passend {cntr} documents!\033[0m")
                        # writes the last data to the file
            index.add_to_posting_list(meta_data)
            # stores the data in the index
            index.create_dictionary(meta_data)

    def number_of_documents(self, name):
        with zipfile.ZipFile(os.path.dirname(os.path.realpath(__file__)) + os.sep + PATH_TO_ARCHIVE) as archive:
            json_file = str(archive.namelist()[0])
            with archive.open(json_file) as json_obj:
                doc_count = 0
                for cntr, obj in enumerate(json_obj):
                    curr_dict = json.loads(obj)
                    if name in curr_dict['author'].lower():
                        print("Id of the document: " + str(cntr))
                        print(curr_dict['author'])
                        doc_count += 1
        print(doc_count)

    """ 
    Returns a mapping between the id and the corresponding json object.
    """
    def get_info_by_id(self, identifiers: list) -> list:
        file = os.path.dirname(os.path.realpath(__file__)) + os.sep + PATH_TO_JSON
        resulting_data = collections.OrderedDict()
        for i, id in enumerate(identifiers):
            if i >= NUM_OF_BOOGLE_DOCS: 
                break
            line = linecache.getline(file, id+1)
            resulting_data[id] = json.loads(line)
        return resulting_data
        

    def compute_snippet(self, document: str, query: list):
        """ Computes snippets from a given document and a given query. """
        sentences = document.split('. ')
        weights = []
        for s in sentences:
            tmp_weight = 0
            for q in query:
                tmp_weight += math.log(s.count(q) + 1)
            weights.append(tmp_weight)

        winner = sentences[weights.index(max(weights))]

        # TODO: print also the sentences of the place two ..

        #winner_tokens = winner.split()
        #if len(winner_tokens) > 30:
        #    return ' '.join(winner_tokens[:30]) + '..'
        #else:
        return winner + "."

    """
    Universal method for the arXiv search
    """

    def search(self, query: str):
        search = Search()
        query = query.lower()
        # Facetted search
        if 'author:' in query:
            query = query[7:]
            posting_list = search.singleKeywordSearchIn('author', query)
            ranking = search.facettedRanking(posting_list, 0)
        elif 'title:' in query:
            query = query[6:]
            posting_list = search.singleKeywordSearchIn('title', query)
            ranking = search.facettedRanking(posting_list, 1)
        elif 'abstract:' in query:
            query = query[9:]
            posting_list = search.singleKeywordSearchIn('abstract', query)
            ranking = search.facettedRanking(posting_list, 2)
        # Phrase Search
        elif query[0] == '\"' and query[-1] == '\"':
            query = query[1:-1]
            search.phraseSearch(query)
            ranking = search.phraseRanking()
        elif ' ' in query:
            # Multiple Keyword Search
            multiple = search.multipleKeywordSearch(query.split())
            ranking = search.multipleKeywordRanking(multiple)
        elif not (' ' in query):
            # Single Keyword Search
            single = search.singleKeywordSearch(query)
            ranking = search.singleKeywordRanking(single)
        else:
            # If none of the above / Invalid input
            return []
        return search.sortDict(ranking)

    def create_arxiv(self):
        index = Index()
        index.create_arxiv_byteoffset_dict()

if __name__ == "__main__":
    sengine = SearchEngine()
    #ids: list = sengine.search('krestel')
    #print(ids)
