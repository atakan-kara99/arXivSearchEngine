#########################################
# GLOBAL SETTINGS FOR OUR SEARCH ENGINE #
#########################################
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords

# -- path to our archive -- #
PATH_TO_ARCHIVE = 'archive.zip' 

# -- determine the interval the program writes the posting list -- #
INTERVAL_OF_INSERTING = 2000000 # iterate over all docs and then create the posting file

# -- define suffix for index file endings -- #
INDEX_SUFFIX = '.dictionary.txt'

# -- define suffix for posting file endings -- #
POSTING_SUFFIX = '.postings.txt'

# -- regular expression for tokenizer -- #
TOKENIZER = RegexpTokenizer(r"\w+") 

# -- list of stopwords to filter with -- #
STOPWORDS = stopwords.words('english')

# -- represents the whole counts of words in all titles -- #
COUNT_OF_TITLE_WORDS = 143784991

# -- represents the whole counts of words in all authors -- #
COUNT_OF_AUTHORS_WORDS = 137644500

# -- represents the whole counts of words in all abstracts -- #
COUNT_OF_ABSTRACT_WORDS = 1790113915

# -- sum of all counts -- #
COUNT_OF_ALL_WORDS = COUNT_OF_ABSTRACT_WORDS + COUNT_OF_AUTHORS_WORDS + COUNT_OF_TITLE_WORDS

# -- number of relevant solr documents -- #
NUM_OF_SOLR_DOCS = 30

# -- number of boogle documents -- #
NUM_OF_BOOGLE_DOCS = 100

PATH_TO_JSON = "arxiv-metadata-oai-snapshot.json"
