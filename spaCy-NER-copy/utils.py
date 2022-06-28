import requests
from spacy import load

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

def predict(strToPredict):
    # import model
    link_to_model = "finalModel1"
    loaded_model = load(link_to_model)
    res = loaded_model(str(strToPredict))
    return res