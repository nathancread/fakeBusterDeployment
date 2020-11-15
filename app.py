from flask import Flask
from flask import render_template
import backend
import sys
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("test.html")



@app.route('/test_func')
def test_func():
    rating = 1
    product_category = "PC"
    verified_purchase = "N"
    review_text = "I am extremely unhappy with this fudge bar! ALL FUDGE BARS SHOULD COME WITH TWO KITTENS, AT LEAST! I DEMAND A REFUND!"
    print("NICE")
    predict, conf = backend.classify(rating, product_category, verified_purchase, review_text)
    print("NICER2")
    sys.stdout.flush()
    return predict + str(conf)