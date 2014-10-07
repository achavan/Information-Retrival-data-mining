import json
import math
from collections import OrderedDict


class bm25f:

    
    numberOfDocs = 0.0;
    docVectors = dict()
    
    invertedIndex = dict()

       

    def __init__(self):
        with open('docLengths.json') as f:
            self.docLengths = json.load(f)

        with open('invertedIndex.json') as f:
            self.invertedIndex = json.load(f)

        self.sortedIndex = OrderedDict(sorted(self.invertedIndex.items(), key=lambda t: t[0]))
        self.numberOfDocs = float(len(self.docLengths))

        
        
    '''Method to read document vectors from a file'''
    def readVectorsFromFile(self):
        with open('docVectors.json') as f:
            self.docVectors = json.load(f)

    '''calculate idf for each query term'''
    def idf(self, queryTerm):
        n = self.numberOfDocs
        df = len(self.invertedIndex[queryTerm])
        return math.log10(n/df)
                                 

    '''bm25f ranking of query with each doc in cluster'''       
    def bm25fRanking(self, cluster, queryVector):

        k = 1.2
        b = 0.75

        bm25Score = {}

        avgDocLength = self.docLengths['avgLength'] # average length of all docs

        
        for doc in cluster:
            docScore = 0.0
            if doc in self.docLengths:
                lengthOfDoc = float(self.docLengths[str(doc)]) #length of the document

            else:
                lengthOfDoc = avgDocLength
                
            for term in queryVector:
                if term in self.sortedIndex and str(doc) in self.sortedIndex[term]:
                    tf = (int(self.sortedIndex[term][str(doc)]["title"])*5) + int(self.sortedIndex[term][str(doc)]["body"]) + (int(self.sortedIndex[term][str(doc)]["headings"])*3)
                    
                    numerator = tf * (k + 1.0)
                    denominator = tf + (k * (( 1.0 - b) + ( b * (lengthOfDoc/avgDocLength))))
                    docScore += self.idf(term) * ( numerator / denominator) #calculate score using bm25f formula
              
            bm25Score[doc] = docScore

        
        sorted_bm25Rank = sorted(bm25Score.iteritems(), key=lambda (k, v): (-v, k))[:10]#sort to find top 10 docs
        '''for doc, rank in sorted_bm25Rank: #print the top 5 docs and their scoring
            print doc, rank'''
        return sorted_bm25Rank
                    

        

    
    
    
    

    
