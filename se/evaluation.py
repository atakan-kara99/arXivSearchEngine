
import math
import re

"""
Class for evaluating a query with three different measures.
"""
class Evaluation:

    def __init__(self, goldStandard: list, currentResults: list) -> None:
        self.retrieved = len(currentResults)
        self.currentList = currentResults
        self.goldList = goldStandard
        self.relevant = len(goldStandard)

    """
    Method for calculating the precision@10 measure
    for queries.
    """
    def precisionAt10(self) -> float:
        if self.retrieved == 0:
            return 0
        retrievedRelevantDocs = [elem for elem in self.currentList if elem in self.goldList]
        retrievedRelevant = len(retrievedRelevantDocs)
        return retrievedRelevant / self.retrieved
    
    """
    Method for calculating the mean average precision
    (MAP) for queries. 
    """
    def meanAveragePrecision(self) -> float:
        if self.retrieved == 0:
            return 0
        result = 0
        j = 1
        for i, elem in enumerate(self.currentList):
            if j > self.relevant:
                break
            if elem in self.goldList:
                result += j / (i+1)
                j += 1
        return result / self.relevant

    """
    Method for calculating the average normalized
    Discounted Cumulative Gain.
    """
    def normalizedDCG(self):
        if self.retrieved == 0:
            return 0
        k = self.relevant
        rankingValues = [math.ceil((k-i+1) / (0.3*k)) for i in range(k)]
        # Discounted Cumulative Gain at each position
        dcgList = [0]*self.retrieved
        cumulative = 0
        for i, elem in enumerate(self.currentList):
            dcgList[i] += cumulative
            if elem in self.goldList:
                rel = rankingValues[self.goldList.index(elem)]
                if i == 0:
                    dcgList[i] = rel
                else:
                    dcgList[i] += rel / math.log2(i+1)
            cumulative = dcgList[i]
            
        # Ideal Discounted Cumulative Gain at each position
        idealDcgList = [0]*self.retrieved
        cumulative = 0
        for i, elem in enumerate(self.currentList):
            idealDcgList[i] += cumulative
            if i < len(rankingValues):
                if i == 0:
                    idealDcgList[i] = rankingValues[i]
                else:
                    idealDcgList[i] += rankingValues[i] / math.log2(i+1)
            cumulative = idealDcgList[i]
            
        # nDCG values (divide actual by ideal):
        nDCG = [0]*self.retrieved
        averageNDCG = 0
        for i in range(self.retrieved):
            nDCG[i] = dcgList[i] / idealDcgList[i]
            averageNDCG += nDCG[i]
        return averageNDCG / self.retrieved

