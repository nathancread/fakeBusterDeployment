from flask import Flask, request, render_template
import backend
import sys
import json
app = Flask(__name__,
        static_url_path='',
        static_folder='static',
        template_folder='templates')

@app.route('/')
@app.route('/search.html')
def hello_world():
    return render_template("search.html")

#title,image,percentage_FAKE_reviews,stars_without_fake,stars_with_fake
@app.route('/reviews/',methods = ['POST'])
def reviews():
    url = request.form.get('url')

    reviews, title, image_url  = backend.scrape(url)
    myDict = {}
    myDict["title"] = title 
    myDict["image_url"] = image_url 

    fake = 0
    total = 0
    total_real = 0 
    total_stars_real = 0
    total_stars = 0

    for review in reviews:
        predict, conf = backend.classify(review["rating"], review["category"], review["verified"], review["review_text"])
        total+=1
        total_stars += review["rating"]
        if predict == "FAKE":
            fake +=1
        if predict == "REAL":
            total_real+=1
            total_stars_real += review["rating"]

    myDict["percentage_fake"]= fake/total
    myDict["raw_rating"]= total_stars_real/total_real
    myDict["modified_rating"]=  total_stars/total

    return json.dumps(myDict)

@app.route('/test_func')
def test_func():
    reviews, title, image_url = backend.scrape("https://www.amazon.com/Enhanced-Splashproof-Portable-Bluetooth-Radiator/dp/B010OYASRG/ref=sr_1_3?dchild=1&keywords=bluetooth%2Bspeaker&qid=1605484686&sr=8-3&th=1")

    test_string = title + "\n"

    for review in reviews:
        predict, conf = backend.classify(review["rating"], review["category"], review["verified"], review["review_text"])

        test_string += predict + " " + str(conf) +"\n"

    print("NICER2")
    sys.stdout.flush()
    return test_string
