from sklearn.svm import LinearSVC
from nltk.classify import SklearnClassifier
import pickle
import random

import nltk
from nltk.tokenize import word_tokenize
# cant access /usr/ on heroku so we download locally.
nltk.data.path.append('./nltk_data/')
nltk.download('punkt', './nltk_data/')
nltk.download('wordnet', './nltk_data/')
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

