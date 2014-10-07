from __future__ import division
import os
from collections import OrderedDict
import json
import math
import pickle
import random
import numpy
import copy

class KMeans:
    docVectors = dict()
    '''Create the vectors for the documents'''
    def createVectors(self,sortedIndex,sortedDocIds):
        for docId in sortedDocIds:
            thisDocVector = []
            for term in sortedIndex:
                    freqForThisTerm = 0
                    if docId in sortedIndex[term]:
                            freqForThisTerm = (int(sortedIndex[term][docId]["title"])*5) + int(sortedIndex[term][docId]["body"]) + (int(sortedIndex[term][docId]["headings"])*3)
                    thisDocVector.append(freqForThisTerm)
            self.docVectors[docId] = thisDocVector
        #dump the vectors into a file for later use in the query
        with open('docVectors.json', 'w') as f:
            json.dump(self.docVectors, f)

    '''Method to read document vectors from a file'''
    def readVectorsFromFile(self):
        with open('docVectors.json') as f:
            self.docVectors = json.load(f)

    '''Method to calculate euclidian distance between two documents'''
    def findDistance(self, doc1, doc2):
        try:
            score = 0
            for i in range(len(doc1)):
                score += (doc1[i] - doc2[i]) * (doc1[i] - doc2[i])
            return math.sqrt(score)
        except:
            print("Debug: Doc1 ", type(doc1), "Doc2 ", type(doc2))
        
    
    '''Method used in re-computation of centroid'''
    def mean(self,a):
        return sum(a) / len(a)

    '''Method for readjusting centroid for a specific cluster'''
    def adjustCentroid(self, cluster):
        clusterVectors = []
        for docId in cluster:
            clusterVectors.append(self.docVectors[str(docId)])
            
        #Get the mean of all the vectors in this cluster
        mainCentroid = map(self.mean,zip(*clusterVectors))
        newCentroid = mainCentroid
        score = 10000
        # Now select the nearest doc for this 
        for docId in cluster:
            distanceFromCentroid = 9999
            try:
                distanceFromCentroid = numpy.linalg.norm(numpy.array(mainCentroid)-numpy.array(self.docVectors[str(docId)]))
            except:
                distanceFromCentroid = self.findDistance(mainCentroid, self.docVectors[str(docId)])

            if distanceFromCentroid < score:
                score = distanceFromCentroid
                newCentroid = docId
            
        #print ("Debug: Centroid type ",type(newCentroid))
        return newCentroid
    
    '''Method implements K-Means'''
    def applyKMeans(self, docIds, maxIterations, maxSeeds):

        clusters = []
        for i in range(0,maxSeeds):
            clusters.append([])

        centroids = []
        
        #Select random seeds
        initialSeeds = []
        for i in range(0,maxSeeds):
            randomSeed = random.randrange(1,len(docIds)) 
            if i in initialSeeds:
                i -= 1
                continue
            clusters[i].append(randomSeed)
            initialSeeds.append(randomSeed)

        print("Random Seeds Generated") 
        print (initialSeeds)
        #Define initial seeds as centroids
        for seed in initialSeeds:
            centroids.append(seed)

        previousClusters = []

        print ("Debug: Usual centroid type", type(centroids[0]), ' Number of centroids: ',len(centroids))
        #Iterate through each document to put it some cluster
        for i in range(0,maxIterations):
            print("Started Iteration :",i)
            clusters = []

            for k in range(0,maxSeeds):
                clusters.append([centroids[k]])

            for docId in docIds:
                if docId in centroids:
                    continue
                score = 100000
                selectedCentroid = -1
                processedCentroidNumber = 0
                for centroid in centroids:
                    distanceFromCentroid = 100000
                    try:
                        a = numpy.array(self.docVectors[str(centroid)])
                        b = numpy.array(self.docVectors[str(docId)])
                        distanceFromCentroid = numpy.linalg.norm(a-b)
                    except:
                        distanceFromCentroid = self.findDistance(self.docVectors[str(centroid)], self.docVectors[str(docId)])

                    if distanceFromCentroid < score:
                        score = distanceFromCentroid
                        selectedCentroid = processedCentroidNumber
                    processedCentroidNumber += 1
                        
                clusters[selectedCentroid].append(docId)
                #Repositioning of centroid, if required after every document processing, very bulky and time consuming
                #centroids[selectedCentroid] = self.adjustCentroid(clusters[selectedCentroid])

            print("Docs processed now adjusting centroids")
            #Adjust centroids, once all docs are processed.
            for k in range(0,len(centroids)):
                print("Size for Cluster",k,len(clusters[k]))
                centroids[k] = self.adjustCentroid(clusters[k])

            
            print("Iteration ",i," Complete")

            with open('centroid.pickle', 'w') as f:
                pickle.dump(centroids, f)

            with open('clusters.pickle', 'w') as f:
                pickle.dump(clusters, f)
        
            if len(previousClusters) > 0:
                converged = True
                for k in range(0,len(previousClusters)):
                    if len(previousClusters[k]) != len(clusters[k]):
                        converged = False
                        break
                if converged:
                    break
            previousClusters = copy.copy(clusters)

        print("K-Means converged")
                    
                              
if __name__ == "__main__":
    #Change this accordingly
    os.chdir('//Users//mac//Desktop//tutorial')
    invertedIndex = dict()
    
    with open('invertedIndex.json') as f:
        invertedIndex = json.load(f)
    sortedIndex = OrderedDict(sorted(invertedIndex.items(), key=lambda t: t[0]))

    docIds = dict()
    with open('docIds.json') as f:
        docIds = json.load(f)
    sortedDocIds = OrderedDict(sorted(docIds.items(), key=lambda t: t[0]))

    kMeans = KMeans()
    print ("Creating document vectors")

    #Run this thing if creating new vector representation on docs for new index
    #kMeans.createVectors(sortedIndex,sortedDocIds)
    kMeans.readVectorsFromFile()
    print ("Document vectors creation done")
    print ("Applying K-Means")
    kMeans.applyKMeans(docIds, 10, 10)
    '''
    vectors = [['1','2'],['2','3'],['4','5']]
    mainCentroid = map(kMeans.mean,zip(*vectors))
    print (mainCentroid)'''
