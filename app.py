from flask import Flask, request, render_template, redirect, url_for, flash
import sys
import os

import backend
from forms import URLForm


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()

    # over here, form submission
    if request.method == "POST":
        if form.validate_on_submit():
            print("Got form!")
            sys.stdout.flush()




        
            return redirect(url_for('product_page', product_id="111"))
        else:
            flash("Invalid URL")

    # over here, form request
    return render_template("index.html", form=form)



# product display
@app.route('/query/<product_id>')
def product_page(product_id):
    print("test")
    sys.stdout.flush()

    return render_template("product.html")




@app.route('/test_func')
def test_func():
    reviews, title, image_url = backend.scrape("https://www.amazon.com/Enhanced-Splashproof-Portable-Bluetooth-Radiator/dp/B010OYASRG/ref=sr_1_3?dchild=1&keywords=bluetooth%2Bspeaker&qid=1605484686&sr=8-3&th=1")

    test_string = title + "\n"

    for review in reviews:
        predict, conf = backend.classify(review["rating"], review["category"], review["verified"], review["review_text"])
        test_string += predict + " " + str(conf) +"\n"

    sys.stdout.flush()
    return test_string


if __name__ == '__main__':
    app.run(debug=True)