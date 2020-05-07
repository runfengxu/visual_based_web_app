from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from extract_feature import extract
import os
from flask_pymongo import PyMongo
import json

import uuid
import array
import numpy as np

from scipy.spatial import distance
import sys
# import pymongo
import heapq
import time

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://cs553:cs553@localhost:27017/amazonproducts?authSource=amazonproducts'
mongo = PyMongo(app)

ALLOWED_EXT = set(['png','jpg','jpeg','tif'])

def predict(targetarray):
    s = time.time()
    H=[(-4000,-4000)]*10
    # metaCol = mongo.db.metadata
    heapq.heapify(H)
    recommendUrls = {}
    feature = mongo.db.feature
    metadata = mongo.db.metadata
    cur = feature.find()
    count=0
    for i in cur:
        asin = list(i.keys())[1]
        b = i[asin]
        dist = -1*distance.cosine(targetarray,b[0])
        # dist=0
        heapq.heappushpop(H,(dist,asin[4:]))
        count+=1
        if(count>30000):
            break
            # print(count,file = sys.stdout)
    # print(count,file=sys.stdout)
    # print(time.time()-s)
    for i in H:
        # t=time.time()
        cursor = metadata.find({"asin":i[1]})[0]
        # print(time.time()-t)
        # print(len(cursor))
        t = time.time()
        
        url=cursor['imUrl']
        # print(time.time()-t)
        recommendUrls[i[1]]=url        
    # print(time.time()-s)
    return recommendUrls


def recommend(target):
    # featureCol = mydb["features"]
    metaCol = mongo.db.metadata

    recommendUrls = {}

    for meta in metaCol.find().limit(10):

        recommendUrls[meta["asin"]] = meta["imUrl"]

    return recommendUrls

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/upload_predict', methods = ['POST'])
def upload_predict():
    #upload file
    file = request.files['file']
    if file.filename.find('.') <= 0:
        return redirect(url_for('main_page'))

    file_ext = file.filename.rsplit('.', 1)[1].strip().lower()

    if file_ext not in ALLOWED_EXT:
        return redirect(url_for('main_page'))

    user_input = request.form.get("name")

    file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
    basepath = os.path.dirname(__file__)
    upload_path = os.path.join(basepath, 'static/images', file_name)
    file.save(upload_path)

    #get feature
    feature = extract(upload_path)

    #get recommendation
    # urls = recommend(feature)
    urls = predict(feature)
    origin = os.path.join('static/images', file_name)

    return render_template('display.html', origin=origin, urls=urls)

@app.route('/product/feedback', methods=['POST'])
def get_feedback():
    req = request.get_json()

    # print(req)

    basepath = os.path.dirname(__file__)
    file_name = "result.json"

    download_path = os.path.join(basepath, 'document', file_name)

    f = open(download_path, 'a')

    json.dump(req, f, indent = 4, sort_keys = False)
    f.write('\n')

    f.close()

    res = make_response(jsonify({"message": "JSON received"}), 200)

    return res

@app.route('/product/<asin>')
def hello_name(asin):
    metadata = mongo.db.metadata
    review= mongo.db.reivews

    cursor = metadata.find({"asin":asin})[0]
    meta = {}
    candidate = ['title','brand','description','price']
    url = cursor["imUrl"]
    for element in candidate:
        if element in cursor:
            meta[element]=cursor[element]
    re={}
    try:
        cursor2 = review.find({"asin":asin})[0]
        candidate2 = ["reviewerID","reviewerName","reviewText","overall","summary","unixReviewTime","reviewTime"]

        for element in candidate2:
            if element in cursor2:
                re[element]=cursor2[element]

    except:
        return render_template('product.html',meta = meta,review = re,url = url)
    return render_template('product.html',meta = meta,review = re,url = url)


if __name__ == '__main__':
    app.run(debug = True)