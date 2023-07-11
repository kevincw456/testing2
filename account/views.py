from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import AnalysisForm, RegistrationForm, CreationForm, UpdateForm
from .models import Customer, Word, Request, tweets, twitterUser

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .serializers import tweetsSerializers
import pickle
import json
import pandas as pd
import numpy as np
import joblib


# Create your views here.
def login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # if request.GET.get('next'):
            #     return redirect(request.GET.get('next'))
            # else:
            return redirect(home)
        # else:
        #     login(request, user)
        #     if request.GET.get('next'):
        #         return redirect(request.GET.get('next'))
        #     else:
        #         return redirect('/chome')
        else:
            messages.error(request, "Wrong username or password!")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(login_view)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User request sent, kindly wait a few days for account approval!")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required()
def home(request):
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            tweet = form.cleaned_data['tweets']
            tf_idf_fit_only = pickle.load(open("C:/Users/tangw/PycharmProjects/demo/account/tfidf_pickle_fit", "rb"))
            # unit should be the tweet data
            matrix = tf_idf_fit_only.transform([tweet])
            # vectorising the new tweets
            df_vector = pd.DataFrame(matrix.todense(), columns=tf_idf_fit_only.get_feature_names_out())
            result = tweetsAnalysis(df_vector)
            messages.info(request, 'Application Status: {}'.format(result))
    else:
        form = AnalysisForm()
    return render(request, 'adminHome.html', {'form': form})


def user_request(request):
    requests = Request.objects.all()
    return render(request, 'userRequest.html', {'requests': requests})


def reject(request, myid):
    requests = Request.objects.get(id=myid)
    requests.delete()
    messages.error(request, "User account rejected successfully!")
    return redirect(user_request)


@login_required()
def admin_create(request):
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User account created successfully!")
            return redirect(admin_create)

    else:
        form = CreationForm()
    return render(request, 'adminCreate.html', {'form': form})


@login_required()
def view(request):
    if 'q' in request.GET:  # q is the variable that carries the term user is searching for
        q = request.GET['q']
        multiple_queries = Q(Q(first_name__istartswith=q) | Q(last_name__istartswith=q))
        customers = Customer.objects.filter(multiple_queries)  # need to add error for no results found?
    else:
        customers = Customer.objects.filter(is_superuser=False)
    return render(request, 'adminView.html', {'customers': customers})


# def update_view(request, myid):
#     customer = Customer.objects.get(id=myid)
#     if request.method == 'POST':
#         form = UpdateForm(request.POST, instance=request.Customer)
#         if form.is_valid():
#             if form.cleaned_data['first_name']:
#                 customer.first_name = form.cleaned_data['first_name']
#             if form.cleaned_data['last_name']:
#                 customer.last_name = form.cleaned_data['last_name']
#             if form.cleaned_data['email']:
#                 customer.last_name = form.cleaned_data['email']
#             if form.cleaned_data['phone_number']:
#                 customer.last_name = form.cleaned_data['phone_number']
#             if form.cleaned_data['address']:
#                 customer.last_name = form.cleaned_data['address']
#             if form.cleaned_data['postal_code']:
#                 customer.last_name = form.cleaned_data['postal_code']
#             if form.cleaned_data['twitter_handle']:
#                 customer.last_name = form.cleaned_data['twitter_handle']
#             form.save()
#             messages.info(request, "Customer particulars updated successfully")
#             return redirect(update_view)
#     else:
#         form = UpdateForm(instance=request.Customer)
#     return render(request, 'adminUpdate.html', {'form': form})


@login_required()
def delete_view(request, myid):
    particulars = Customer.objects.get(id=myid)
    particulars.delete()
    messages.error(request, "Particular deleted successfully")
    return redirect(view)


@login_required()
def dictionary(request):
    word_list = Word.objects.all()
    return render(request, 'dictionary.html', {'word_list': word_list})


@login_required()
def add_word(request):
    if request.method == "POST":
        word = request.POST['word']
        description = request.POST['description']
        item = Word(word=word, description=description)
        item.save()
        messages.success(request, "Word added successfully!")
    else:
        pass

    word_list = Word.objects.all()
    return render(request, 'dictionary.html', {'word_list': word_list})


@login_required()
def delete_word(request, myid):
    word = Word.objects.get(id=myid)
    word.delete()
    messages.error(request, "Word removed successfully!")
    return redirect(dictionary)


#syafiq
class analysisView(viewsets.ModelViewSet):
    queryset = tweets.objects.all()
    serializer_class = tweetsSerializers


def tweetsAnalysis(data):
    try:
        mdl = joblib.load("C:/Users/tangw/PycharmProjects/demo/account/DecisionTreeClassifier.pkl")
        y_pred = mdl.predict(data)
        result = pd.DataFrame(y_pred, columns=['Category'])
        result = result.replace({0: 'Hateful Message', 1: 'Offensive Language', 2: 'Neutral'})
        print(result)
        return (result.iloc[0]['Category'])
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


def table(response):
    t = tweets.objects.all()
    tu = twitterUser.objects.all()
    return render(response, "tweetTable.html", {"t": t, "tu": tu})


def tweetRetrieval(response):
    t = tweets.objects.all()
    return render(response, "tweetRetrieval.html", {"t": t})


def twitterUserRetrieval(response):
    t = twitterUser.objects.all()
    return render(response, "twitterUserRetrieval.html", {"t": t})


#sam
def select_cust(request, myid):
    cust_record = Customer.objects.get(id=myid)     #to retrieve a single object,use get
    return render(request, "custRecord.html", {"cust_record" : cust_record})


def suspend_view(request, myid):
    suspended_cust = Customer.objects.get(id=myid)
    if(suspended_cust.is_active == 0):
        messages.error(request, "Account already suspended!")
        return redirect('view')
    else:
        suspend = 0
        suspended_cust.is_active = suspend
        suspended_cust.status = "Suspended"
        suspended_cust.save()
        messages.success(request, "Account successfully suspended!")
        return redirect('view')


def update_view(request, myid):
    updated_cust = Customer.objects.get(id=myid)
    form = UpdateForm(request.POST or None, instance=updated_cust)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer particulars updated successfully!")
        return redirect(view)
    return render(request, 'adminUpdate.html', {'form': form})


def reinstate_view(request, myid):
    reinstated_cust = Customer.objects.get(id=myid)
    if (reinstated_cust.is_active == 1):
        messages.error(request, "Account already active!")
        return redirect('view')
    else:
        suspend = 1
        reinstated_cust.is_active = suspend
        reinstated_cust.status = "Active"
        reinstated_cust.save()
        messages.success(request, "Account successfully reinstated!")
        return redirect('view')
