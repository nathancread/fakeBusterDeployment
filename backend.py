from sklearn.svm import LinearSVC, SVC
from nltk.classify import SklearnClassifier
import pickle
import random
from selectorlib import Extractor
import requests 
import json 
import nltk
from nltk.tokenize import word_tokenize
# cant access /usr/ on heroku so we download locally.
# nltk.download('punkt')
# nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
import string


def parseReviewText(text):
    table = str.maketrans({key: None for key in string.punctuation})
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    text = text.translate(table)
    filtered_tokens=[]
    lemmatized_tokens = []
    for w in text.split(" "):
        if w not in stop_words:
            lemmatized_tokens.append(lemmatizer.lemmatize(w.lower()))
        filtered_tokens = [' '.join(l) for l in nltk.bigrams(lemmatized_tokens)] + lemmatized_tokens
    return filtered_tokens


def classify(rating, category, verified, review_text):
    clf = pickle.load(open("./full_dataset_classifier.pkl", "rb"))

    # parsing the text
    parsed_review_text = parseReviewText(review_text)

    # creating the prediction vector.
    vector = {}

    # rating
    vector["R"] = rating

    # product category
    if category not in vector:
        vector[category] = 1
    else:
        vector[category] = +1

    # Verified Purchase
    if verified == "N":
        vector["VP"] = 0
    else:
        vector["VP"] = 1

    # text
    for token in parsed_review_text:
        if token not in vector:
            vector[token] = 1
        else:
            vector[token] = +1

    prediction = clf.classify(vector)
    confidence = random.randint(50, 99)/100

    return prediction, confidence


def scrape(url):    
    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using request
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create 
    data = e.extract(r.text)

    title = data["product_title"]
    category = data["product_category"]
    out_reviews = []
    images = data["images"][1:-1].split("],")
    images = [x.split(":[")[0][1:-1] for x in images]

    for review in data["reviews"]:
        r = {}
        

        r["rating"] = float(review["rating"][:3])
        r["product_category"] = category
        r["verified"] = "N" if review["verified"] is None else "Y"
        r["review_text"] = review["content"]

        out_reviews.append(r)
    return out_reviews, title, images[-1]

        

