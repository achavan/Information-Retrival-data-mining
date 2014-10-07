from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from tutorial.items import Page
from bs4 import BeautifulSoup
import string
import PorterStemmer as p

class ConcordiaSpider(CrawlSpider):
    name = "concordia"
    #allowed_domains = ["www.concordia.ca"]
    start_urls = [
        "http://www.encs.concordia.ca",
    ]
    
    #define the rule to crawl everything from concordia websites
    rules = [Rule(SgmlLinkExtractor(allow=('.*.concordia.ca')), callback='parse_item', follow=True)]
    
    
    '''Define the mainIndex, which will be dumped to a database later on
    Structure: {term: {docid : {title:titleFreq, body:bodyFreq, headings:headingsFreq} } }
    '''
    mainIndex = dict()
    
    '''Define the docId to URL mapping'''
    docIds = dict()

    docLengths = dict()

    totalDocLength = 0
    
    docIdIncrementer = 0
    
    '''To apply basic filters to the text like lowercasing, removing punctutations, \n and \t's '''
    def applyBasicFilters(self, text):
        text = text.lower()
        for char in string.punctuation:
            text = text.replace(char,"")
        
        for char in "\n\t\r":
            text = text.replace(char," ")
        return text

    '''Function used to store/update the term in the inverted index'''
    def putTermInIndex(self, where, docId, term):
        if term not in self.mainIndex:
            self.mainIndex[term] = dict()
        if docId not in self.mainIndex[term]:
            self.mainIndex[term][docId] = dict()
            self.mainIndex[term][docId]["title"] = '0'
            self.mainIndex[term][docId]["body"] = '0'
            self.mainIndex[term][docId]["headings"] = '0'
            self.mainIndex[term][docId][where] = '1'
        else:
            self.mainIndex[term][docId][where] = str(int(self.mainIndex[term][docId][where]) + 1)
            if(where == 'headings'):
                self.mainIndex[term][docId]["body"] = str(int(self.mainIndex[term][docId]["body"]) - 1)

    ''' Function to check if the term is numeric'''
    def isNumber(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    '''Crawler returns the document to this function'''
    def parse_item(self, response):
        '''page = Page()
        page['url'] = response.url
        page['completePage'] = response.body'''

        thisDocLength = 0
        
        print("parsed doc")
        self.docIdIncrementer += 1
        self.docIds[self.docIdIncrementer] = response.url
        
        soup = BeautifulSoup(response.body.lower())
        
        pageTitle = self.applyBasicFilters(soup.title.string)
        
        stopWords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]
        
        #Store the title terms in the index for this particular page
        try:
            for term in pageTitle.split(' '):
                if self.isNumber(term):
                    continue
                if term in stopWords:
                    continue
                if term == "":
                    continue
                self.putTermInIndex("title",self.docIdIncrementer,p.PorterStemmer().stem(term, 0,len(term)-1))
                thisDocLength += 1
        except:
            print ("Title problem")

        #Store the body terms in the index for this particular page
        try:
            links = []
            for link in soup.body.find_all('a'):           
                links.append(link.get_text())
                
            for someString in soup.body.stripped_strings:
                try:
                    if someString in links:
                        links.remove(someString)
                        continue
                except:
                    continue

                if len(someString) > 20:
                    continue

                someString = self.applyBasicFilters(someString)
            
                for term in someString.split(" "):
                    if self.isNumber(term):
                        continue
                    if term in stopWords:
                        continue
                    if term == "":
                        continue
                    if(term == ""):
                        continue
                    self.putTermInIndex("body",self.docIdIncrementer,p.PorterStemmer().stem(term, 0,len(term)-1))
                    thisDocLength += 1
        except:
            print("Problem in body")

        
        #Fetch all the heading tags
        try:            
            allHeadings = soup.body.find_all(['h1','h2','h3','h4','h5','h6'])
            #Store the heading tags in the body, and reduce the term frequency in body
            for heading in allHeadings:
                for content in heading.contents:
                    thisHeading = self.applyBasicFilters(repr(content.string))
                    for term in thisHeading.split(' '):
                        if self.isNumber(term):
                            continue
                        if term in stopWords:
                            continue
                        if term == "":
                            continue
                        if(term == ""):
                            continue
                        self.putTermInIndex("headings",self.docIdIncrementer,p.PorterStemmer().stem(term, 0,len(term)-1))
                        thisDocLength += 1

        except:
            print("Problem in headings")
        
        self.totalDocLength += thisDocLength
        self.docLengths[self.docIdIncrementer] = thisDocLength

        pass
