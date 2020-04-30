from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from extract_feature import extract
import os
from flask_pymongo import PyMongo

from DAO import recommend
import json

import uuid

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://test:test@localhost:27017/amazonproducts?authSource=amazonproducts'
mongo = PyMongo(app)

ALLOWED_EXT = set(['png','jpg','jpeg','tif'])

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
    urls = recommend(feature)

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