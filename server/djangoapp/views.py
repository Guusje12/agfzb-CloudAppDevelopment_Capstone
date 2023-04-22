from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import get_request, get_dealers_from_cf, get_reviews_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.views.decorators.csrf import csrf_exempt


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/user_registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/user_registration.html', context)
    
    
def get_dealerships(request):
    if request.method == "GET":
        state = request.GET.get("state")
        context = {}
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/get-dealership.json"
        if state:
            dealerships = get_dealers_from_cf(url, state=state)
        else:
            dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)
    
# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/get-reviews-python.json"
        review_list = get_reviews_by_id_from_cf(url, dealerId=dealer_id)
        context["review_list"] = review_list
        # result = ' '.join([review.sentiment for review in review_list])
        return render(request, 'djangoapp/dealer_details.html', context)
        # return HttpResponse(result)

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
    context = {}
    dealer_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/get-dealership.json"
    dealer = get_dealers_from_cf(url=dealer_url, dealer_id=dealer_id)[0]
    context["dealer"] = dealer
    if request.method == 'GET':
        context["dealer_id"] = dealer_id
        cars = CarModel.objects.all()
        context["cars"] = cars
        # return HttpResponse(cars)
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
    # and request.user.is_authenticated:
        car_id = request.POST['car']
        car = CarModel.objects.get(pk=car_id)
        review_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/store-review.json"
        review={}
        review["id"] = dealer_id
        review["name"] = request.user.username
        if request.POST['purchasecheck']=='on':
            review["purchase"] = True
        else:
            review["purchase"] = False
        review["purchase_date"] = request.POST["purchasedate"]
        review["car_make"] = car.car_make.name
        review["car_model"] = car.name
        review["car_year"] = int(car.year.year)
        review["dealership"] = dealer_id
        review["review"] = request.POST['review']
        json_payload={}
        json_payload["review"] = review
        result = post_request(review_url, json_payload, dealerId=dealer_id)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)


