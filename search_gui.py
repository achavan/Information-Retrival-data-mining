from Tkinter import *
import webbrowser
import tkFont
import string
import PorterStemmer as p
import bm25f as bm
import kmeans as km
import pickle
import json
from collections import OrderedDict

class SearchGui(Frame):

    def __init__(self, master):
        """ Initialize the Frame """
        Frame.__init__(self, master)
        self.grid()
        
        self.text = Text(self, width = 50)
        self.group = None
        self.userQuery = None
        self.queryVector = []
        self.queryDocVector = []        
        self.url_results = []
        self.url_clicked = None
        self.close_centroid = None
        self.lowestDistance = {}
        self.create_gui()
        self.docVectors = dict()
        
        
      
        
    '''create the different aspects of the gui'''
    def create_gui(self):
        
        
        self.label = Label(self, text = "Enter your query:")
        self.label.grid(row =0, column =0, columnspan = 4, padx = 10, sticky = W ) #put the label onto the window

        '''Search box'''
        self.queryEntry = Entry(self, width = 35)
        self.queryEntry.grid(row = 1, column = 0, padx = 10, sticky = W)
        

        
        '''Search button'''
        self.searchButton = Button(self)
        self.searchButton["text"] = "Search"
        self.searchButton["command"] = self.calculate_results
        self.searchButton.grid(row = 1, column = 1, padx = 5, sticky = W)

        
    '''open the webpage once it has been clicked'''
    def click(self, url):
                
        webbrowser.open(url)
        print "Opening Web Page"

    '''creating a query vector after query has been processed'''
    def createqueryVector(self, Term):
        self.queryVector.append(Term)
        
    '''create the query doc vector to store the frequencies'''
    def createQueryDocVectors(self, queryVec):
        
        for term in sortedIndex:
            freqForThisTerm = 0
            for t in queryVec:
                if t == term:
                    freqForThisTerm += 1
            
            self.queryDocVector.append(freqForThisTerm)
        

    '''calculate the distance between query and centroid'''            
    def calculateDistance(self, centroid):
        self.distanceVector = []
        return km.KMeans().findDistance(self.docVectors[str(centroid)],self.queryDocVector)
        
         
         
    '''Query handling'''
    def calculate_results(self):
        self.queryVector = []
        self.queryDocVector = []
        if self.group != None:
            self.group.grid_forget()

        
        self.userQuery = self.queryEntry.get() #get user input from text field

        '''query manipulation'''
        self.userQuery = self.userQuery.lower()
        for char in string.punctuation:
            self.userQuery = self.userQuery.replace(char, " ")

        stopWords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

        for term in self.userQuery.split(' '):
            if term in stopWords:
                continue

            if term == "":
                continue

            '''apply porter stemmer and create the query vector'''
            self.createqueryVector(p.PorterStemmer().stem(term, 0,len(term)-1))

        '''create the query doc vector to keep track of frequencies'''
        self.createQueryDocVectors(self.queryVector)
            
            
        print self.queryVector
        '''load all doc vectors'''
        with open('docVectors.json') as f:
            self.docVectors = json.load(f)

        '''load all the centroids'''   
        with open('centroid.pickle') as f:
            centroids = pickle.load(f)
            
        '''for each centroid calculate it's distance to the query vector'''
        for centroid in centroids:
            
            self.lowestDistance[centroid] = self.calculateDistance(centroid)        
            
        

        '''get the centroid with the lowest distance'''    
        sorted_distance = sorted(self.lowestDistance.iteritems(), key=lambda (k, v): (v, k))[:1]
        for doc, rank in sorted_distance: #print the top 5 docs and their scoring
            self.close_centroid = doc

        print "closest centroid = " + self.close_centroid

        clusters = []
        '''load all clusters'''
        with open('clusters.pickle')as f:
            clusters = pickle.load(f)

        print "getting cluster:"

        print int(self.close_centroid)

        '''get the current cluster'''
        indexCent  = centroids.index(self.close_centroid)
        
        '''rank the docs in the current cluster'''
        returned_docs = {}
        returned_docs = bm.bm25f().bm25fRanking(clusters[indexCent], self.queryVector)

        self.url_results = []

        '''get the url results'''
        for doc, rank in returned_docs:
            self.url_results.append(docIds[doc])
           
        
        '''set a frame around the results'''
        self.group = LabelFrame(self, text="Results", padx=5, pady=5)
        self.group.grid(padx=10, pady=10, column = 4)

        '''display the results and make them clickable'''
        for i,url in enumerate(self.url_results):
            label=Label(self.group,text=url, fg="blue", cursor = "hand2")
            label.grid(row=i+2, column = 4)
            label.bind("<Button-1>",lambda e,url=url:self.click(url))

               
  
       
if __name__ == "__main__":

    invertedIndex = dict()
    with open('invertedIndex.json') as f:
        invertedIndex = json.load(f)
    sortedIndex = OrderedDict(sorted(invertedIndex.items(), key=lambda t: t[0]))

    with open('docIds.json') as f:
        docIds = json.load(f)
    

    root = Tk()
    root.title("Search Concordia")
    root.geometry("1000x500")

    app = SearchGui(root)
    
    root.mainloop()
