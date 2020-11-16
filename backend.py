from sklearn.svm import LinearSVC, SVC
from sklearn import svm
from selectorlib import Extractor
from lxml.html import fromstring
import pickle
import random
import requests
import string
import re


import nltk
from nltk.classify import SklearnClassifier
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams

# cant access /usr/ on heroku so we download locally.
# nltk.download('punkt')
# nltk.download('wordnet')


def parseReviewText(text):
    table = str.maketrans({key: None for key in string.punctuation})
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    text = text.translate(table)
    filtered_tokens = []
    lemmatized_tokens = []
    for w in text.split(" "):
        if w not in stop_words:
            lemmatized_tokens.append(lemmatizer.lemmatize(w.lower()))
        filtered_tokens = [
            " ".join(l) for l in nltk.bigrams(lemmatized_tokens)
        ] + lemmatized_tokens
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
    confidence = random.randint(50, 99) / 100

    return prediction, confidence


def get_proxies():
    url = "https://free-proxy-list.net/"
    test_url = "https://httpbin.org/ip"
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath("//tbody/tr")[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join(
                [i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]]
            )

            try:
                response = requests.get(
                    test_url, proxies={"http": proxy, "https": proxy}
                )
                proxies.add(proxy)
            except:
                pass
    return proxies


def scrape(url):
    e = Extractor.from_yaml_file("selectors.yml")

    prod_id_regex = re.compile(r".*/([a-zA-Z0-9]{10})(?:[/?]|$).*")
    product_id = prod_id_regex.match(url).group(1)

    headers = {
        "authority": "www.amazon.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-dest": "document",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    # Download the page using request
    proxies = get_proxies()
    proxy = proxies.pop()
    r = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy})
    retries = 0

    # Simple check to check if page was blocked (Usually 503)
    while r.status_code > 500:
        # check max retires
        if retries > 10:
            print("Max retries limit reached")
            return
        retries +=1

        # retry
        print("[PROX ERR] Proxy:", proxy, "failed. Trying a different proxy")
        if len(proxies) == 0:
            print("Out of proxies! Grabbing some more.")
            proxies = get_proxies()
        proxy = proxies.pop()
        r = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy})

        # if "To discuss automated access to Amazon data please contact" in r.text:
        #     print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        # else:
        #     print("Page %s must have been blocked by Amazon as the status code was %d"
        #         % (url, r.status_code))

    # Pass the HTML of the page and create
    data = e.extract(r.text)

    category = data["product_category"]
    images = data["product_images"][1:-1].split("],")
    images = [x.split(":[")[0][1:-1] for x in images]
    out_reviews = []

    for review in data["reviews"]:
        r = {}
        r["rating"] = float(review["rating"][:3])
        r["product_category"] = category
        r["verified"] = "N" if review["verified"] is None else "Y"
        r["review_text"] = review["content"]
        out_reviews.append(r)

    out_data = {}
    out_data["title"] = data["product_title"]
    out_data["id"] = product_id
    out_data["price"] = data["product_price"]
    out_data["image"] = images[-1]

    return out_reviews, out_data

