import pymongo

myclient = pymongo.MongoClient('mongodb://cs553:cs553@localhost:27017/amazonproducts?authSource=amazonproducts')

mongo = myclient["amazonproducts"]
feature = mongo['feature']


f= open('/home/cs553/553project/feature_alex.json','r')

count=0
for line in f:
    a=eval(line)
    x = feature.insert_one(a)
    count+=1
    if(count%1000==0):
        print(count)
f.close()
#         import json
# import gzip



# def convert(input):
#     def parse(path):
#         g = gzip.open(path, 'r')
#         for l in g:
#             yield json.dumps(eval(l))

#     count=0
#     for l in parse(input):
#         x = mongo.metadata.insert_one(l)
#         count+=1
#         if(count%1000==0):
#             print(count)