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
            print("Got form! URL is:", form.url.data)
            sys.stdout.flush()
            reviews, data = backend.scrape(form.url.data)

            num_fake, num_real = 0, 0
            num_fake_stars, num_real_stars = 0, 0
            
            for review in reviews:
                predict, conf = backend.classify(review["rating"], review["product_category"], review["verified"], review["review_text"])
                num_fake += 1 if predict == "FAKE" else 0
                num_real += 0 if predict == "FAKE" else 1

                num_fake_stars += review["rating"] if predict == "FAKE" else 0
                num_real_stars += 0 if predict == "FAKE" else review["rating"]


            product_data = {}
            product_data["percentage_fake"] = int((num_fake/(num_real+num_fake))*100)
            product_data["raw_rating"] = round((num_fake_stars+num_real_stars)/(num_fake+num_real), 2)
            product_data["adjusted_rating"] = round((num_real_stars)/(num_real), 2)
            product_data["title"] = data["title"]
            product_data["price"] = data["price"]
            product_data["image_url"] = data["image"]
            product_data["url"] = form.url.data
            
            # return here index.html, but with the product info
            return render_template("index.html", form=form, product_data=product_data)
        else:
            flash("Invalid URL")

    # over here, form request
    return render_template("index.html", form=form)



if __name__ == '__main__':
    app.run(debug=True)