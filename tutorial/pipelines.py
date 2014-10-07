# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class ConcordiaPipeline(object):
    def process_item(self, item, spider):
        return item
    def close_spider(self, spider):
        print("So I am in close spider")
        for term in spider.mainIndex:
            print (term, spider.mainIndex[term])
        with open('invertedIndex.json', 'w') as f:
            json.dump(spider.mainIndex, f)
        with open('docIds.json', 'w') as f:
            json.dump(spider.docIds, f)

        docLengths = spider.docLengths
        docLengths['avgLength'] = spider.totalDocLength / len(spider.docIds)
        with open('docLengths.json', 'w') as f:
            json.dump(docLengths, f)



# elsewhere...
'''with open('my_dict.json') as f:
    my_dict = json.load(f)'''