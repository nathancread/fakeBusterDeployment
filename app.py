from flask import Flask
from flask import render_template
import backend
import sys
app = Flask(__name__, template_folder='templates')

@app.route('/')
def hello_world():
    return render_template("search.html")



@app.route('/test_func')
def test_func():
    reviews, title = backend.scrape("https://www.amazon.com/Enhanced-Splashproof-Portable-Bluetooth-Radiator/dp/B010OYASRG/ref=sr_1_3?dchild=1&keywords=bluetooth%2Bspeaker&qid=1605484686&sr=8-3&th=1")

    test_string = title + "\n"

    for review in reviews:
        predict, conf = backend.classify(review["rating"], review["category"], review["verified"], review["review_text"])

        test_string += predict + " " + str(conf) +"\n"

    print("NICER2")
    sys.stdout.flush()
    return test_string
