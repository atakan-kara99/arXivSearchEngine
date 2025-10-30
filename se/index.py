import fileinput
import os
import zipfile
from nltk import PorterStemmer, stem
from nltk.tokenize import word_tokenize

from .settings import INDEX_SUFFIX, PATH_TO_ARCHIVE, STOPWORDS, POSTING_SUFFIX
from .utils import get_position_of_term

"""
The main task of this class is to index from a collection tokens 
for a specific meta attribute.
So every attribute gets his own index (own dictionary and own posting list).
"""
class Index:
    """
    Constructor to create dicts to work with
    """
    def __init__(self):
        # the dictionary of our words
        self.dictionary = {}
        # contains the list of tokens to be inserted
        self.queue = {}

    """
    Stores the dictionary as a file and clears the temporary
    dictionary.
    """
    def create_arxiv_byteoffset_dict(self):
        with zipfile.ZipFile(os.path.dirname(os.path.realpath(__file__)) + os.sep + PATH_TO_ARCHIVE) as archive:
            json_file = str(archive.namelist()[0])
            with archive.open(json_file) as json_obj:
                persistent_file = open('arxiv.txt', 'a', encoding="utf8")
                i = 0
                offset = json_obj.tell()
                while True:
                    print("Line: " + str(i) + ", Offset: " + str(offset))
                    entry = f"{i} {offset}\n"
                    persistent_file.write(entry)
                    json_obj.readline()
                    i += 1
                    new_offset = json_obj.tell()
                    if offset == new_offset:
                        break
                    offset = new_offset
                persistent_file.close()

    """
    Stores the dictionary as a file and clears the temporary
    dictionary.
    """
    def create_dictionary(self, meta_data):
        keys = list(self.dictionary.keys())
        sorted_keys = sorted(keys)
        persistent_dict = open(meta_data+INDEX_SUFFIX, 'a', encoding="utf8")
        for w in sorted_keys:
            entry = f"{w} {self.dictionary[w]}\n"
            persistent_dict.write(entry)
        persistent_dict.close()
        del self.dictionary
        
    """
    Creates our (later sorted) dictionary_file.
    Provides very fast look ups for tokens.
    First the method inserts a token into the list
    and then it creates an entry in our postings list.
    After that it creates a reference to this list.
    """
    def add_to_dictionary(self, document: str, doc_id: str, meta_data: str):
        # split the document into tokens
        tokens = word_tokenize(document.lower())
        # create a mapping between the stemmed word/token
        # and the list of positions.
        term_pos = {}
        for t in tokens:
            if t not in STOPWORDS and len(t) > 3:
                # get the positions of the term in the given document
                p = get_position_of_term(tokens, t)
                # stemming the words for inserting in the postings list.
                stemmed = PorterStemmer().stem(t)
                if stemmed not in term_pos:
                    # add the position to the term
                    term_pos[stemmed] = p
                    # preparement for creating the posting list
                    n=len(term_pos[stemmed])
                    # store the current posting list as a list
                    current_posting_list = [1, doc_id, len(tokens), n, ]+term_pos[stemmed] # store the length of the document
                    # lookup if the term already exist in the queue
                    # if yes, append the posting to the list
                    # otherwise create a new mapping
                    if stemmed in self.queue:
                        # append the posting list
                        self.queue[stemmed].extend(current_posting_list[1:])
                        # increase the counter for the term
                        self.queue[stemmed][0] += 1
                    else:
                        # when the current posting list is new, insert it to the queue
                        self.queue[stemmed] = current_posting_list
                        if stemmed not in self.dictionary:
                            self.dictionary[stemmed] = -1


    """
    Writes into the postings file.
    We will create all posting lists for a term and then
    we append the postings to our file.
    """
    def add_to_posting_list(self, meta_data: str):
        # create temporary list of queue
        tmp_queue = {}
        for p in self.queue:
            if self.dictionary[p] != -1:
                tmp_queue[p] = self.dictionary[p]
        # get the counter for the file
        counter = 0
        # open the file to append data
        posting_list_file = open(meta_data+POSTING_SUFFIX, 'a', encoding="utf8")
        for p in self.queue:
            if self.dictionary[p] == -1:
                # convert the list into bytes
                #posting_list_as_byte_list = bytes(self.queue[p], 'ascii')
                current_head = posting_list_file.tell()
                # write the bytes sequence into the list
                posting_list_file.write(' '.join(map(str, self.queue[p]))+"\n")
                # add the head and length of the posting list to the dictionary
                self.dictionary[p] = counter
                counter +=1
        posting_list_file.close()
        #clear the queue
        del self.queue

        
        """
        (1) Get the min counter of the dicts.
        (2) Iterate with the counter of the posting file
        (3) When counter and line are identical,
        read the line and merge the posting file with the 
        line content and write it into the line.
        (4) When max counter < line number, break the loop.
        """
        # exit()
        # # TODO: implement the possibility to merge two lists to the file

        # posting_list_file = fileinput.input(meta_data+settings.POSTING_SUFFIX, inplace=1)


        # if bool(dict_with_queue_terms):
        #     #iterate over the lines of the file
        #     for line, content in enumerate(posting_list_file):
        #         # skip if the counter is too large
        #         if counter >= len(sorted_dict):
        #             break
        #         # only update if the line is equal to the data that is still missing
        #         # and if the queue got still tokens to insert
        #         if line == sorted_dict[sorted_dict_keys[counter]] and sorted_dict_keys[counter] in self.queue:
        #             # convert the byte stream to readable content
        #             readable_content = list(bytes(content))
        #             readable_content[0]+=self.queue[sorted_dict_keys[line]][0]
        #             readable_content.extend(self.queue[sorted_dict_keys[counter]][1:])
        #             print(bytes(readable_content), end='\n')
        #         else:
        #             print(content, end='')
        #         counter +=1

