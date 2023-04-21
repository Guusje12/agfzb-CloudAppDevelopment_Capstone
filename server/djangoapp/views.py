from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_request, get_dealers_from_cf, get_dealers_by_id_from_cf, post_request
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
        # url = "https://us-south.functions.appdomain.cloud/api/v1/web/CD0201-xxx-nodesample123_Tyler/dealership-package/get-dealerships"
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/get-dealership.json"
        if state:
            dealerships = get_dealers_from_cf(url, state=state)
        else:
            dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # return render(request, 'djangoapp/index.html', context)
        # context["dealership_list"] = dealerships
        return HttpResponse(dealer_names)

    
# def get_dealerships(request):

#     if request.method == "GET":

#         context = {}

#         st = request.GET.get("st")
#         dealerId = request.GET.get("dealerId")
#         url = "https://us-south.functions.appdomain.cloud/api/v1/web/7ccc880f-504c-4f24-a816-b01352454616/dealership-package/get-dealership"
#         # Get dealers from the URL
#         dealerships = get_dealers_from_cf(url)

#         if st:
#             dealerships = get_dealers_from_cf(url, st=st)
#         elif dealerId:
#             dealerId = int(dealerId)
#             dealerships = get_dealers_from_cf(url, dealerId=dealerId)

#         context["dealership_list"] = dealerships

#         return render(request, "djangoapp/index.html", context=context)
    
# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_static(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/static_template.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        # url = "https://us-south.functions.appdomain.cloud/api/v1/web/CD0201-xxx-nodesample123_Tyler/dealership-package/get-dealerships"
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/get-reviews-python.json"
        reviews = get_dealers_by_id_from_cf(url, dealerId=dealer_id)
        # Concat all dealer's short name
        result = ' '.join([review.sentiment for review in reviews])
        # return render(request, 'djangoapp/index.html', context)
        # context["dealership_list"] = dealerships
        return HttpResponse(result)

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
    if request.method == "POST":
    # and request.user.is_authenticated:
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/5d9b64c5-aca0-4edd-b439-d9fd483d8356/dealership-package/store-review.json"
        review={}
        review["id"] = 1115
        review["name"] = "Guusje"
        review["purchase"] = False
        review["purchase_date"] = datetime.utcnow().isoformat()
        review["car_make"] = "Audi"
        review["car_model"] = "A3"
        review["car_year"] = 2018
        review["dealership"] = 1
        review["review"] = "This is a great car dealer"
        json_payload={}
        json_payload["review"] = review
        result = post_request(url, json_payload, dealerId=dealer_id)
        return HttpResponse(result)
