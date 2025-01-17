import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print("POST to {} ".format(url))
    print(json_payload)
    print(kwargs)
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get("state")
    dealer_id = kwargs.get("dealer_id")
    if state:
        json_result = get_request(url, state=state)
    elif dealer_id:
        json_result = get_request(url, dealer_id=dealer_id)
    else:
        json_result = get_request(url)

    if json_result:
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            # dealer = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"], full_name=dealer["full_name"],
                                   state=dealer["state"], st=dealer["st"], zip=dealer["zip"], short_name=dealer["short_name"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_reviews_by_id_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)

    if json_result:
        reviews = json_result["result"]
        # For each dealer object
        for review in reviews:
            # Create a CarDealer object with values in object
            review_obj = DealerReview(dealership=review["dealership"], name=review["name"], purchase=review["purchase"], 
                                      review=review["review"], purchase_date=review["purchase_date"], car_make=review["car_make"],
                                      car_model=review["car_model"], car_year=review["car_year"], sentiment="help", id=review["id"])
            review_obj.sentiment = analyze_review_sentiments(review_text=review_obj.review)
            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(review_text):
    api_key = 'FEkJgTQAKRfmOybABcR5J9651grS3MfgcEOdy1Rhvrcb'
    url = 'https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/d975583a-1899-4983-b4f6-1be39bb05d8b'
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(text=review_text ,features=Features(sentiment=SentimentOptions(targets=[review_text]))).get_result() 
    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 
    return label




