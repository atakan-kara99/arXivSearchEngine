
# Abstract data type for a postings list
class Posting:
    
    def __init__(self, term: str, metaData: str, postingsStr: str) -> None:
        if postingsStr == '':
            self.term = term
            self.metaData = metaData
            self.numOfPostings = 0
            # docID -> (numOfTokens, occurrenceInDoc, [position])
            self.postingsDict = {}
        else:
            self.term = term
            self.metaData = metaData
            splitPostingsStr = postingsStr.split()
            self.numOfPostings = int(splitPostingsStr[0])
            self.postingsDict = {}
            i = 1
            while(i < len(splitPostingsStr)):
                docID = int(splitPostingsStr[i])
                i += 1
                tokens = int(splitPostingsStr[i])
                i += 1
                occurrences = int(splitPostingsStr[i])
                for k in range(occurrences):
                    i += 1
                    position = int(splitPostingsStr[i])
                    if docID in self.postingsDict:
                        self.postingsDict[docID][2].append(position)
                    else:
                        self.postingsDict[docID] = (tokens, occurrences, [position])
                i += 1

    def getNumOfTokensFor(self, doc: int) -> int:
        if not (self.postingsDict and doc in self.postingsDict):
            return 0
        else:
            return self.postingsDict[doc][0]

    def getOccurrencesFor(self, doc: int) -> int:
        if not (self.postingsDict and doc in self.postingsDict):
            return 0
        else:
            return self.postingsDict[doc][1]

    def getAllPositionsFor(self, doc: int) -> list:
        if not (self.postingsDict and doc in self.postingsDict):
            return []
        else:
            return self.postingsDict[doc][2]

    def getAllOccurrences(self) -> list:
        occurrencesList = []
        for posting in self.postingsDict:
            occurrencesList.append(posting[1])
        return occurrencesList

    def getAllIDs(self) -> set:
        keys = self.postingsDict.keys()
        return set(keys)

    def sumOccurrences(self) -> int:
        sum = 0
        for posting in self.postingsDict:
            sum += posting[1]
        return sum

    def sumTokens(self) -> int:
        sum = 0
        for posting in self.postingsDict:
            sum += posting[0]
        return sum

    def setTerm(self, term: str) -> None:
        self.term = term

    def setMetaData(self, metaData: str) -> None:
        self.metaData = metaData

    def setNumOfPostings(self, numOfPostings: int) -> None:
        self.numOfPostings = numOfPostings

    def setPostingsDict(self, postingsDict: dict) -> None:
        self.postingsDict = postingsDict

    def getTerm(self) -> str:
        return self.term

    def getMetaData(self) -> str:
        return self.metaData

    def getNumOfPostings(self) -> int:
        return self.numOfPostings

    def getPostingsDict(self) -> dict:
        return self.postingsDict

    def __str__(self) -> str:
        if self.term == '':
            strr = "Not found in " + self.metaData + ".\n"
        else:
            strr = "'" + self.term + "' occurs " + str(self.numOfPostings) + " times in " + self.metaData + " index.\n"
            for id in self.postingsDict:
                strr += "In document " + str(id) + " it appears " + str(self.postingsDict[id][1]) + " out of " + str(self.postingsDict[id][0]) + " times at " + str(self.postingsDict[id][2]) + ".\n"
        return strr