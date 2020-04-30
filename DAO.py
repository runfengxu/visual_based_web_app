import pymongo

def recommend(target):
    myclient = pymongo.MongoClient("mongodb://test:test@localhost:27017/amazonproducts?authSource=amazonproducts")
    mydb = myclient["amazonproducts"]

    # featureCol = mydb["features"]
    metaCol = mydb["metadata"]

    recommendUrls = {}

    for meta in metaCol.find().limit(10):

        recommendUrls[meta["asin"]] = meta["imUrl"]

    return recommendUrls

if __name__ == '__main__':
    target = "0000037214"
    tmp = recommend(target)
    print(tmp)