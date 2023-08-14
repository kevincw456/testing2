from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import AnalysisForm, RegistrationForm, CreationForm, UpdateForm, UpdateProfileForm, tweetScrape, haterSearch
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
import bz2
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pathlib import Path

#testing
from django.views.generic import View
from rest_framework.views import APIView
from django.db import connections

import requests
from bs4 import BeautifulSoup

import smtplib
from email.message import EmailMessage


def email_message(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "hatedetect@gmail.com"
    msg['from'] = user
    password = "iqusevfjvyjqgnhq"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()


def send_email(request):
    adminId = "tangweibin1234567890@hotmail.com"
    msg = email_message("New Customer Request!",
                                 """Dear Administrator,

A new customer has requested for approval.

From, HateDetect Team""",
                                 adminId)#custId.email)
    return render(request, 'register.html', {"msg": msg})


# Create your views here.
def login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
            # if request.GET.get('next'):
            #     return redirect(request.GET.get('next'))
            # else:
                return redirect(home)
            else:
                if Customer.objects.filter(is_active=True):
                    login(request, user)
                    return redirect(customer)
                else:
                    messages.error(request, "Account has been suspended!")
        # else:
        #     login(request, user)
        #     if request.GET.get('next'):
        #         return redirect(request.GET.get('next'))
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
            messages.success(request, "Request sent. Kindly wait a few days for approval!")
            send_email(request)
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required()
def home(request):
    if request.method == 'POST':
        #todo CLEAN THE DATA BEFORE ANALYSIS
        #and check if it works with an array of data and not just a string
        form = AnalysisForm(request.POST)
        if form.is_valid():
            tweet = form.cleaned_data['insert_words']
            #THIS IS WHERE TO CHANGE THE FILE LOCATION
            filepath = Path(__file__).parent / "tfidf_pickle_fit.pkl"
            tf_idf_fit_only = pickle.load(open(filepath, "rb"))
            # unit should be the tweet data
            matrix = tf_idf_fit_only.transform([tweet])
            # vectorising the new tweets
            df_vector = pd.DataFrame(matrix.todense(), columns=tf_idf_fit_only.get_feature_names_out())
            result = tweetsAnalysis(df_vector)
            list_Category = result['Category'].tolist()
            messages.info(request, 'Application Status: {}'.format(list_Category[0]))
    else:
        form = AnalysisForm()
    return render(request, 'adminHome.html', {'form': form})


@login_required()
def customer(request):
    if request.method == 'POST':
        #todo CLEAN THE DATA BEFORE ANALYSIS
        #and check if it works with an array of data and not just a string
        form = AnalysisForm(request.POST)
        if form.is_valid():
            tweet = form.cleaned_data['insert_words']
            #THIS IS WHERE TO CHANGE THE FILE LOCATION
            filepath = Path(__file__).parent / "tfidf_pickle_fit.pkl"
            tf_idf_fit_only = pickle.load(open(filepath, "rb"))
            # unit should be the tweet data
            matrix = tf_idf_fit_only.transform([tweet])
            # vectorising the new tweets
            df_vector = pd.DataFrame(matrix.todense(), columns=tf_idf_fit_only.get_feature_names_out())
            result = tweetsAnalysis(df_vector)
            list_Category = result['Category'].tolist()
            messages.info(request, 'Application Status: {}'.format(list_Category[0]))
    else:
        form = AnalysisForm()
    return render(request, 'customerHome.html', {'form': form})


@login_required()
def customer_request(request):
    requests = Request.objects.all()
    return render(request, 'customerRequest.html', {'requests': requests})


def approval_email(request, email):
    cust_email = email_message("Account Approved!",
                                 """Dear Customer,

Your account has been approved. 

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


@login_required()
def approve(request, myid):
    requests = Request.objects.get(id=myid)
    Customer.objects.create(
        username=requests.username,
        password=make_password(requests.password),
        first_name=requests.first_name,
        last_name=requests.last_name,
        email=requests.email,
        phone_number=requests.phone_number,
        address=requests.address,
        postal_code=requests.postal_code,
        twitter_handle=requests.twitter_handle,
    )
    requests.delete()
    approval_email(request, requests.email)
    messages.success(request, "Customer request approved!")
    return redirect(customer_request)


def rejection_email(request, email):
    cust_email = email_message("Account Rejected!",
                                 """Dear Customer,

Your account has been rejected.

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


@login_required()
def reject(request, myid):
    requests = Request.objects.get(id=myid)
    requests.delete()
    rejection_email(request, requests.email)
    messages.error(request, "Customer request rejected!")
    return redirect(customer_request)


def creation_email(request, email):
    cust_email = email_message("Account Created!",
                                 """Dear Customer,

Your account has been created.

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


@login_required()
def admin_create(request):
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            email = form['email'].value()
            form.save()
            creation_email(request, email)
            messages.success(request, "Customer account created!")
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


def updation_email(request, email):
    cust_email = email_message("Particulars Updated!",
                                 """Dear Customer,

Your particulars has been updated.

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


def update_view(request, myid):
    update_particulars = Customer.objects.get(id=myid)
    form = UpdateForm(request.POST or None, instance=update_particulars)
    if form.is_valid():
        form.save()
        updation_email(request, update_particulars.email)
        messages.success(request, "Customer particulars updated!")
        return redirect(view)
    return render(request, 'adminUpdate.html', {'form': form})


def deletion_email(request, email):
    cust_email = email_message("Account Deleted!",
                                 """Dear Customer,

Your account has been deleted.

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


@login_required()
def delete_view(request, myid):
    particulars = Customer.objects.get(id=myid)
    deletion_email(request, particulars.email)
    particulars.delete()
    messages.error(request, "Customer account deleted!")
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
        messages.success(request, "Word added!")
    else:
        pass

    word_list = Word.objects.all()
    return render(request, 'dictionary.html', {'word_list': word_list})


@login_required()
def delete_word(request, myid):
    word = Word.objects.get(id=myid)
    word.delete()
    messages.error(request, "Word removed!")
    return redirect(dictionary)


#sam
def select_cust(request, myid):
    cust_record = Customer.objects.get(id=myid)     #to retrieve a single object,use get
    return render(request, "custRecord.html", {"cust_record" : cust_record})


def suspension_email(request, email):
    cust_email = email_message("Account Suspended!",
                                 """Dear Customer,

Your account has been suspended.

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


def suspend_view(request, myid):
    suspended_cust = Customer.objects.get(id=myid)
    if suspended_cust.is_active == 0:
        messages.error(request, "Account already suspended!")
        return redirect('view')
    else:
        suspend = 0
        suspended_cust.is_active = suspend
        suspended_cust.status = "Suspended"
        suspended_cust.save()
        suspension_email(request, suspended_cust.email)
        messages.success(request, "Account suspended!")
        return redirect('view')


def reinstation_email(request, email):
    cust_email = email_message("Account Reinstated!",
                                 """Dear Customer,

Your profile has been reinstated.

From, HateDetect Team""",
                                 email)  # custId.email)
    return render(request, 'customerHome.html', {"cust_email": cust_email})


def reinstate_view(request, myid):
    reinstated_cust = Customer.objects.get(id=myid)
    if reinstated_cust.is_active == 1:
        messages.error(request, "Account already active!")
        return redirect('view')
    else:
        suspend = 1
        reinstated_cust.is_active = suspend
        reinstated_cust.status = "Active"
        reinstated_cust.save()
        reinstation_email(request, reinstated_cust.email)
        messages.success(request, "Account reinstated!")
        return redirect('view')


@login_required()
def view_profile(request):
    customer_id = request.user.id
    customer_profile = Customer.objects.get(id=customer_id)
    return render(request, 'profile.html', {'customer_profile': customer_profile})


def edit_profile(request):
    customer_id = request.user.id
    update_profile = Customer.objects.get(id=customer_id)
    form = UpdateProfileForm(request.POST or None, instance=update_profile)
    if form.is_valid():
        form.save()
        return redirect('view_profile')
    return render(request, 'profileUpdate.html', {'form': form})


def delete_profile(request):
    customer_id = request.user.id
    Customer.objects.filter(id=customer_id).update(phone_number=None, postal_code=None)
    delete_particulars = Customer.objects.get(id=customer_id)
    delete_particulars.first_name = ''
    delete_particulars.last_name = ''
    delete_particulars.address = ''
    delete_particulars.email = ''
    delete_particulars.twitter_handle = ''
    delete_particulars.save()
    return redirect('view_profile')


# syafiq
class analysisView(viewsets.ModelViewSet):
    queryset = tweets.objects.all()
    serializer_class = tweetsSerializers


def tweetsAnalysis(data):
    try:
        # Loading the saved decision tree model pickle
        # THIS IS WHERE TO CHANGE THE FILE LOCATION
        # 'D:/School/FYP/Website/demo/account/SVMCompressed.pkl'
        filepath = Path(__file__).parent / "SVMCompressed.pkl"
        model_pkl_1 = bz2.BZ2File(filepath, 'rb')
        mdl = joblib.load(model_pkl_1)
        y_pred = mdl.predict(data)
        result = pd.DataFrame(y_pred, columns=['Category'])
        result = result.replace({0: 'Hateful Message', 1: 'Offensive Language', 2: 'Neutral'})
        return (result)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)


def preprocess(text):
    lemma = WordNetLemmatizer()
    text = text.lower()
    # remove url
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    # Replace all non-alphanumeric characters with spaces
    text = re.sub(r'\W', ' ', text)
    # replace all numbers with spaces
    text = re.sub(r'\d', ' ', text)
    # remove stop words and perform lemmatization
    text = [lemma.lemmatize(word) for word in text.split() if word not in stopwords.words('english')]

    return text


def wordCount(data):
    word_counts = {}
    # Iterate over the nested list and count word frequencies
    for sublist in data:
        for word in sublist:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

    return word_counts


def dictionaryLimit(data):
    # Sort the dictionary by values in descending order
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    # Get the top 10 highest values
    top_10 = sorted_data[:10]

    return top_10


# function to view the charts and stuff idk man
@login_required()
def adminChart(response):
    # sql statement to count each user's hateful/offensive/neutral messages
    tweetStats = tweets.objects.raw(
        """       
        SELECT
            account_tweets.id,
            account_tweets.twitterUser, 
            account_tweets.count(CASE WHEN category = 'HM' THEN 1 END) as hateful, 
            account_tweets.count(CASE WHEN category = 'OL' THEN 1 END) as offensive, 
            account_tweets.count(CASE WHEN category = 'NM' THEN 1 END) as neutral 
        FROM 
            account_tweets
        GROUP BY
            account_tweets.twitterUser
        """
    )

    tempUserList = []
    for t in tweetStats:
        # initialise an empty list to store current data
        tempCountList = []
        # find the number of each type of tweet and total of tweets made for the current user
        noOfHate = int(t.hateful)
        noOfOffensive = int(t.offensive)
        noOfNeutral = int(t.neutral)
        totalTweets = noOfHate + noOfOffensive + noOfNeutral

        # if total tweets is < 5, dont even count as there is not enough data
        if totalTweets < 5:
            totalWeight = 0
        else:
            # find the weightage score of the user (hate = 10 points, Offensive = 5 points, neutral = 0 points)
            hateWeight = noOfHate * 10
            offensiveWeight = noOfOffensive * 5
            totalWeight = (hateWeight + offensiveWeight) / totalTweets
            totalWeight = totalWeight * 10
        # find the percentage of categorical messages
        # hatePercent = (noOfHate/totalTweets) * 100
        # offensivePercent = (noOfOffensive/totalTweets) * 100
        # neutralPercent = (noOfNeutral/totalTweets) * 100
        # append the stats into tempCountList
        tempCountList.extend((t.twitterUser, totalWeight, noOfHate, noOfOffensive, noOfNeutral))
        tempUserList.append(tempCountList)

    # sort the tempUserList in desc order and choosing only the TOP 10 hateful users based on weight
    sorted_data = sorted(tempUserList, key=lambda x: x[1], reverse=True)[:10]
    print(sorted_data)

    # might slow down performance too much
    # sql statement to get all the tweets
    tweetHateful = tweets.objects.raw(
        """       
        SELECT
            id,
            tweet
        FROM 
            account_tweets
        WHERE
            category = 'HM'
        """
    )

    tweetOffensive = tweets.objects.raw(
        """       
        SELECT
            id,
            tweet
        FROM 
            account_tweets
        WHERE
            category = 'OL'
        """
    )

    tweetNeutral = tweets.objects.raw(
        """       
        SELECT
            id,
            tweet
        FROM 
            account_tweets
        WHERE
            category = 'NM'
        """
    )

    # for loop to go through all the rows and split the tweets into their own words
    # hate message
    hateWords = []
    for i in tweetHateful:
        hatefulTweet = preprocess(i.tweet)
        hateWords.append(hatefulTweet)

    # offensive language
    offensiveWords = []
    for i in tweetOffensive:
        offensiveTweet = preprocess(i.tweet)
        offensiveWords.append(offensiveTweet)

    # neutral language
    neutralWords = []
    for i in tweetNeutral:
        neutralTweet = preprocess(i.tweet)
        neutralWords.append(neutralTweet)

    hateWordCount = wordCount(hateWords)
    offensiveWordCount = wordCount(offensiveWords)
    neutralWordCount = wordCount(neutralWords)

    hateWordCount = dictionaryLimit(hateWordCount)
    offensiveWordCount = dictionaryLimit(offensiveWordCount)
    neutralWordCount = dictionaryLimit(neutralWordCount)

    print(hateWordCount)
    print(offensiveWordCount)
    print(neutralWordCount)

    return render(response, "adminChartView.html",
                  {'sd': sorted_data, 'hwc': hateWordCount, 'owc': offensiveWordCount, 'nwc': neutralWordCount})


# function to web scrape from fake twitter website
@login_required()
def webScrapper(request):
    if request.method == 'POST':
        form = tweetScrape(request.POST)
        if form.is_valid():
            #################################################################################
            # WEB SCRAPPING PART#
            # getting the url of the tweet
            url = form.cleaned_data['insert_Twitter_thread_URL']
            login_url = 'https://flask-production-7913.up.railway.app/login'
            data = {
                'username': 'admin',
                'password': 'admin'
            }

            with requests.Session() as s:
                response = s.post(login_url, data)
                index_page = s.get(url)
                soup = BeautifulSoup(index_page.text, 'html.parser')

            list_name = []
            list_tweet = []

            for tweeting in soup.find_all("div", class_="tweet-list"):
                for item in tweeting.find_all("div", {"class": "tweet-item"}):
                    # get parent tweet
                    name = item.find("a")
                    list_name.append(name.text)
                    content = item.find("div", {"class": "tweet-content"})
                    # if content is empty, most prob on home page
                    if content is None:
                        content = item.select("p")[1]
                    # blame the twitter clone for this retarded shit
                    # its not the same format at the fucking user profile page idk why man
                    if url == 'http://127.0.0.1:5000/profile':
                        content = item.select("p")[1]
                    list_tweet.append(content.text)
                    # get comments
                    for comments in item.find_all("div", {"class": "comment-section"}):
                        for commentItem in comments.find_all("div", {"class": "comment-item"}):
                            input_string = commentItem.text
                            # Find the index of the first colon
                            index = input_string.index(":")

                            # Split the string into two parts
                            commentName = input_string[:index].strip()
                            commentMessage = input_string[index + 1:].strip()
                            list_name.append(commentName)
                            list_tweet.append(commentMessage)

                    # for profile section <blame the twitter clone side man>
                    for comments in item.find_all("div", {"class": "comment-list"}):
                        for commentItem in comments.find_all("div", {"class": "comment-item"}):
                            commentName = commentItem.find("a")
                            commentMessage = commentItem.select("p")[1]
                            list_name.append(commentName.text)
                            list_tweet.append(commentMessage.text)
            #################################################################################

            #################################################################################
            # ANALYSIS PART
            # process the tweets first
            # for i in list_tweet:
            #    processTweets = preprocess(i)
            #    print(processTweets)
            # pickle fit
            filepath = Path(__file__).parent / "tfidf_pickle_fit.pkl"
            tf_idf_fit_only = pickle.load(open(filepath, "rb"))
            matrix = tf_idf_fit_only.transform(list_tweet)
            df_vector = pd.DataFrame(matrix.todense(), columns=tf_idf_fit_only.get_feature_names_out())
            result = tweetsAnalysis(df_vector)
            list_Category = result['Category'].tolist()
            # print(list_Category)
            #################################################################################

            #################################################################################
            # putting all the data into a list
            # insert the values into the tweet table at the same time
            final_list = []
            cursor = connections['default'].cursor()
            for i in range(len(list_tweet)):
                temp_list = []
                temp_list.extend([list_name[i], list_tweet[i], list_Category[i]])
                # change list category to HM, OL, NM
                tempCategory = ""
                if list_Category[i] == "Hateful Message":
                    tempCategory = "HM"
                elif list_Category[i] == "Offensive Language":
                    tempCategory = "OL"
                elif list_Category[i] == "Neutral":
                    tempCategory = "NM"
                cursor.execute("INSERT INTO account_tweets(twitterUser,tweet,category) VALUES( %s , %s, %s )",
                               [str(list_name[i]), str(list_tweet[i]), tempCategory])

                final_list.append(temp_list)
            #################################################################################

            #################################################################################
            # TODO
            # SELECT TWEET TO COUNT ALL HM, OL AND NM GROUP BY TWITTER USER
            tweetStats = tweets.objects.raw(
                """       
                SELECT
                    id,
                    twitterUser, 
                    count(CASE WHEN category = 'HM' THEN 1 END) as hateful, 
                    count(CASE WHEN category = 'OL' THEN 1 END) as offensive, 
                    count(CASE WHEN category = 'NM' THEN 1 END) as neutral 
                FROM 
                    account_tweets
                GROUP BY
                    twitterUser
                """
            )
            # CALCULATE THE RISK WEIGHTAGE
            tempUserList = []
            # tempUserName = []
            for t in tweetStats:
                # initialise an empty list to store current data
                tempCountList = []
                # find the number of each type of tweet and total of tweets made for the current user
                noOfHate = int(t.hateful)
                noOfOffensive = int(t.offensive)
                noOfNeutral = int(t.neutral)
                totalTweets = noOfHate + noOfOffensive + noOfNeutral
                # find the weightage score of the user (hate = 10 points, Offensive = 5 points, neutral = 0 points)
                hateWeight = noOfHate * 10
                offensiveWeight = noOfOffensive * 5
                totalWeight = (hateWeight + offensiveWeight) / totalTweets
                totalWeight = totalWeight * 10
                # append the stats into tempCountList
                tempCountList.extend((t.twitterUser, totalWeight, noOfHate, noOfOffensive, noOfNeutral))
                # tempUserName.append(t.twitterUser)
                tempUserList.append(tempCountList)
            #################################################################################

            #################################################################################
            # INSERT TWITTER USER INTO TWITTER_USER_TABLE IF DOESNT EXIST
            # UPDATE TWITTER USER IF EXIST IN TWITTER USER TABLE

            # select statement to check for existing users
            userName = twitterUser.objects.raw(
                """
                SELECT id,twitterUser FROM account_twitteruser
                """
            )
            existingUsers = []
            for un in userName:
                existingUsers.append(un.twitterUser)

            # compare existingUsers and tempUserName list
            # if user exist in both list, update
            # else insert data from tempUserName into existingUsers
            ##########################################

            # extract the username from tempuserList
            tempUserList_userName = [item[0] for item in tempUserList]
            # compare and find common usernames
            set1 = set(existingUsers)
            set2 = set(tempUserList_userName)
            common_users = list(set1.intersection(set2))
            not_common_users = list(set1.symmetric_difference(set2))

            # update existing users with the new data
            for item in tempUserList:
                name = item[0]
                weightage = item[1]
                hardCount = item[2]
                offensiveCount = item[3]
                neutralCount = item[4]
                cursor.execute(
                    """
                    UPDATE account_twitteruser 
                    SET
                        hateCount = %s,
                        neutralCount = %s,
                        offensiveCount = %s,
                        weightage = %s
                    WHERE
                        (twitterUser = %s)
                    """, [hardCount, neutralCount, offensiveCount, weightage, name]
                )

            # insert the non-existing users with the new data
            for item in tempUserList:
                # check if the name is the same in not_common_users list
                name = item[0]
                weightage = item[1]
                hardCount = item[2]
                offensiveCount = item[3]
                neutralCount = item[4]

                if name in not_common_users:
                    # if the name exist in not_common_users continue with the insertion
                    cursor.execute(
                        "INSERT INTO account_twitteruser(twitterUser,hateCount,neutralCount,offensiveCount,weightage) VALUES( %s , %s, %s, %s , %s )",
                        [name, hardCount, neutralCount, offensiveCount, weightage])
            ##########################################

            # ONCE ALL THIS IS DONE, USER CAN SEE TWITTER USER WITH THE WEIGHTAGE IN ANOTHER TAB
            # USER SHOULD BE ABLE TO SEE TWITTER_USER PREVIOUS TWEETS
            # SELECT * FROM TWEETS WHRE TWITTER_USER == SEARCH VAR

            # print(final_list)
            # return the result of the webscrape to the page
            return render(request, 'adminTweetScrape.html', {'form': form, 'tweetData': final_list})
    else:
        form = tweetScrape()
    return render(request, 'adminTweetScrape.html', {'form': form})


# function to view all stored tweets and search by twitter user
@login_required()
def tweetSearch(response):
    if response.method == 'POST':
        form = haterSearch(response.POST)
        if form.is_valid():
            #################################################################################
            # this is what the user types in
            userName = form.cleaned_data['twitter_handle']

            # sql statement to search for user tweets with the same name
            t = tweets.objects.raw(
                """       
                SELECT
                    id,
                    twitterUser,
                    tweet,
                    category
                FROM 
                    account_tweets
                WHERE
                    twitterUser = %s
                """
                , [userName])

    else:
        form = haterSearch()
        t = tweets.objects.all()
    return render(response, "adminHaterSearch.html", {"tweets": t, "form": form})


def twitterUserRetrieval(request, myid):
    t = twitterUser.objects.get(twitterUser=myid)
    return render(request, "twitterUserRetrieval.html", {"t": t})


@login_required()
def custChart(response):
    # sql statement to count each user's hateful/offensive/neutral messages
    tweetStats = tweets.objects.raw(
        """       
        SELECT
            id,
            twitterUser, 
            count(CASE WHEN category = 'HM' THEN 1 END) as hateful, 
            count(CASE WHEN category = 'OL' THEN 1 END) as offensive, 
            count(CASE WHEN category = 'NM' THEN 1 END) as neutral 
        FROM 
            account_tweets
        GROUP BY
            twitterUser
        """
    )

    tempUserList = []
    for t in tweetStats:
        # initialise an empty list to store current data
        tempCountList = []
        # find the number of each type of tweet and total of tweets made for the current user
        noOfHate = int(t.hateful)
        noOfOffensive = int(t.offensive)
        noOfNeutral = int(t.neutral)
        totalTweets = noOfHate + noOfOffensive + noOfNeutral

        # if total tweets is < 5, dont even count as there is not enough data
        if totalTweets < 5:
            totalWeight = 0
        else:
            # find the weightage score of the user (hate = 10 points, Offensive = 5 points, neutral = 0 points)
            hateWeight = noOfHate * 10
            offensiveWeight = noOfOffensive * 5
            totalWeight = (hateWeight + offensiveWeight) / totalTweets
            totalWeight = totalWeight * 10
        # find the percentage of categorical messages
        # hatePercent = (noOfHate/totalTweets) * 100
        # offensivePercent = (noOfOffensive/totalTweets) * 100
        # neutralPercent = (noOfNeutral/totalTweets) * 100
        # append the stats into tempCountList
        tempCountList.extend((t.twitterUser, totalWeight, noOfHate, noOfOffensive, noOfNeutral))
        tempUserList.append(tempCountList)

    # sort the tempUserList in desc order and choosing only the TOP 10 hateful users based on weight
    sorted_data = sorted(tempUserList, key=lambda x: x[1], reverse=True)[:10]
    print(sorted_data)

    # might slow down performance too much
    # sql statement to get all the tweets
    tweetHateful = tweets.objects.raw(
        """       
        SELECT
            id,
            tweet
        FROM 
            account_tweets
        WHERE
            category = 'HM'
        """
    )

    tweetOffensive = tweets.objects.raw(
        """       
        SELECT
            id,
            tweet
        FROM 
            account_tweets
        WHERE
            category = 'OL'
        """
    )

    tweetNeutral = tweets.objects.raw(
        """       
        SELECT
            id,
            tweet
        FROM 
            account_tweets
        WHERE
            category = 'NM'
        """
    )

    # for loop to go through all the rows and split the tweets into their own words
    # hate message
    hateWords = []
    for i in tweetHateful:
        hatefulTweet = preprocess(i.tweet)
        hateWords.append(hatefulTweet)

    # offensive language
    offensiveWords = []
    for i in tweetOffensive:
        offensiveTweet = preprocess(i.tweet)
        offensiveWords.append(offensiveTweet)

    # neutral language
    neutralWords = []
    for i in tweetNeutral:
        neutralTweet = preprocess(i.tweet)
        neutralWords.append(neutralTweet)

    hateWordCount = wordCount(hateWords)
    offensiveWordCount = wordCount(offensiveWords)
    neutralWordCount = wordCount(neutralWords)

    hateWordCount = dictionaryLimit(hateWordCount)
    offensiveWordCount = dictionaryLimit(offensiveWordCount)
    neutralWordCount = dictionaryLimit(neutralWordCount)

    print(hateWordCount)
    print(offensiveWordCount)
    print(neutralWordCount)

    return render(response, "custChartView.html",
                  {'sd': sorted_data, 'hwc': hateWordCount, 'owc': offensiveWordCount, 'nwc': neutralWordCount})


# function to web scrape from fake twitter website
@login_required()
def cwebScrapper(request):
    if request.method == 'POST':
        form = tweetScrape(request.POST)
        if form.is_valid():
            #################################################################################
            # WEB SCRAPPING PART#
            # getting the url of the tweet
            url = form.cleaned_data['insert_Twitter_thread_URL']
            login_url = 'https://flask-production-7913.up.railway.app/login'
            data = {
                'username': 'admin',
                'password': 'admin'
            }

            with requests.Session() as s:
                response = s.post(login_url, data)
                index_page = s.get(url)
                soup = BeautifulSoup(index_page.text, 'html.parser')

            list_name = []
            list_tweet = []

            for tweeting in soup.find_all("div", class_="tweet-list"):
                for item in tweeting.find_all("div", {"class": "tweet-item"}):
                    # get parent tweet
                    name = item.find("a")
                    list_name.append(name.text)
                    content = item.find("div", {"class": "tweet-content"})
                    # if content is empty, most prob on home page
                    if content is None:
                        content = item.select("p")[1]
                    # blame the twitter clone for this retarded shit
                    # its not the same format at the fucking user profile page idk why man
                    if url == 'http://127.0.0.1:5000/profile':
                        content = item.select("p")[1]
                    list_tweet.append(content.text)
                    # get comments
                    for comments in item.find_all("div", {"class": "comment-section"}):
                        for commentItem in comments.find_all("div", {"class": "comment-item"}):
                            input_string = commentItem.text
                            # Find the index of the first colon
                            index = input_string.index(":")

                            # Split the string into two parts
                            commentName = input_string[:index].strip()
                            commentMessage = input_string[index + 1:].strip()
                            list_name.append(commentName)
                            list_tweet.append(commentMessage)

                    # for profile section <blame the twitter clone side man>
                    for comments in item.find_all("div", {"class": "comment-list"}):
                        for commentItem in comments.find_all("div", {"class": "comment-item"}):
                            commentName = commentItem.find("a")
                            commentMessage = commentItem.select("p")[1]
                            list_name.append(commentName.text)
                            list_tweet.append(commentMessage.text)
            #################################################################################

            #################################################################################
            # ANALYSIS PART
            # process the tweets first
            # for i in list_tweet:
            #    processTweets = preprocess(i)
            #    print(processTweets)
            # pickle fit
            filepath = Path(__file__).parent / "tfidf_pickle_fit.pkl"
            tf_idf_fit_only = pickle.load(open(filepath, "rb"))
            matrix = tf_idf_fit_only.transform(list_tweet)
            df_vector = pd.DataFrame(matrix.todense(), columns=tf_idf_fit_only.get_feature_names_out())
            result = tweetsAnalysis(df_vector)
            list_Category = result['Category'].tolist()
            # print(list_Category)
            #################################################################################

            #################################################################################
            # putting all the data into a list
            # insert the values into the tweet table at the same time
            final_list = []
            cursor = connections['default'].cursor()
            for i in range(len(list_tweet)):
                temp_list = []
                temp_list.extend([list_name[i], list_tweet[i], list_Category[i]])
                # change list category to HM, OL, NM
                tempCategory = ""
                if list_Category[i] == "Hateful Message":
                    tempCategory = "HM"
                elif list_Category[i] == "Offensive Language":
                    tempCategory = "OL"
                elif list_Category[i] == "Neutral":
                    tempCategory = "NM"
                cursor.execute("INSERT INTO account_tweets(twitterUser,tweet,category) VALUES( %s , %s, %s )",
                               [str(list_name[i]), str(list_tweet[i]), tempCategory])

                final_list.append(temp_list)
            #################################################################################

            #################################################################################
            # TODO
            # SELECT TWEET TO COUNT ALL HM, OL AND NM GROUP BY TWITTER USER
            tweetStats = tweets.objects.raw(
                """       
                SELECT
                    id,
                    twitterUser, 
                    count(CASE WHEN category = 'HM' THEN 1 END) as hateful, 
                    count(CASE WHEN category = 'OL' THEN 1 END) as offensive, 
                    count(CASE WHEN category = 'NM' THEN 1 END) as neutral 
                FROM 
                    account_tweets
                GROUP BY
                    twitterUser
                """
            )
            # CALCULATE THE RISK WEIGHTAGE
            tempUserList = []
            # tempUserName = []
            for t in tweetStats:
                # initialise an empty list to store current data
                tempCountList = []
                # find the number of each type of tweet and total of tweets made for the current user
                noOfHate = int(t.hateful)
                noOfOffensive = int(t.offensive)
                noOfNeutral = int(t.neutral)
                totalTweets = noOfHate + noOfOffensive + noOfNeutral
                # find the weightage score of the user (hate = 10 points, Offensive = 5 points, neutral = 0 points)
                hateWeight = noOfHate * 10
                offensiveWeight = noOfOffensive * 5
                totalWeight = (hateWeight + offensiveWeight) / totalTweets
                totalWeight = totalWeight * 10
                # append the stats into tempCountList
                tempCountList.extend((t.twitterUser, totalWeight, noOfHate, noOfOffensive, noOfNeutral))
                # tempUserName.append(t.twitterUser)
                tempUserList.append(tempCountList)
            #################################################################################

            #################################################################################
            # INSERT TWITTER USER INTO TWITTER_USER_TABLE IF DOESNT EXIST
            # UPDATE TWITTER USER IF EXIST IN TWITTER USER TABLE

            # select statement to check for existing users
            userName = twitterUser.objects.raw(
                """
                SELECT id,twitterUser FROM account_twitteruser
                """
            )
            existingUsers = []
            for un in userName:
                existingUsers.append(un.twitterUser)

            # compare existingUsers and tempUserName list
            # if user exist in both list, update
            # else insert data from tempUserName into existingUsers
            ##########################################

            # extract the username from tempuserList
            tempUserList_userName = [item[0] for item in tempUserList]
            # compare and find common usernames
            set1 = set(existingUsers)
            set2 = set(tempUserList_userName)
            common_users = list(set1.intersection(set2))
            not_common_users = list(set1.symmetric_difference(set2))

            # update existing users with the new data
            for item in tempUserList:
                name = item[0]
                weightage = item[1]
                hardCount = item[2]
                offensiveCount = item[3]
                neutralCount = item[4]
                cursor.execute(
                    """
                    UPDATE account_twitteruser 
                    SET
                        hateCount = %s,
                        neutralCount = %s,
                        offensiveCount = %s,
                        weightage = %s
                    WHERE
                        (twitterUser = %s)
                    """, [hardCount, neutralCount, offensiveCount, weightage, name]
                )

            # insert the non-existing users with the new data
            for item in tempUserList:
                # check if the name is the same in not_common_users list
                name = item[0]
                weightage = item[1]
                hardCount = item[2]
                offensiveCount = item[3]
                neutralCount = item[4]

                if name in not_common_users:
                    # if the name exist in not_common_users continue with the insertion
                    cursor.execute(
                        "INSERT INTO account_twitteruser(twitterUser,hateCount,neutralCount,offensiveCount,weightage) VALUES( %s , %s, %s, %s , %s )",
                        [name, hardCount, neutralCount, offensiveCount, weightage])
            ##########################################

            # ONCE ALL THIS IS DONE, USER CAN SEE TWITTER USER WITH THE WEIGHTAGE IN ANOTHER TAB
            # USER SHOULD BE ABLE TO SEE TWITTER_USER PREVIOUS TWEETS
            # SELECT * FROM TWEETS WHRE TWITTER_USER == SEARCH VAR

            # print(final_list)
            # return the result of the webscrape to the page
            return render(request, 'custTweetScrape.html', {'form': form, 'tweetData': final_list})
    else:
        form = tweetScrape()
    return render(request, 'custTweetScrape.html', {'form': form})


# function to view all stored tweets and search by twitter user
@login_required()
def ctweetSearch(response):
    if response.method == 'POST':
        form = haterSearch(response.POST)
        if form.is_valid():
            #################################################################################
            # this is what the user types in
            userName = form.cleaned_data['twitter_handle']

            # sql statement to search for user tweets with the same name
            t = tweets.objects.raw(
                """       
                SELECT
                    id,
                    twitterUser,
                    tweet,
                    category
                FROM 
                    account_tweets
                WHERE
                    twitterUser = %s
                """
                , [userName])

    else:
        form = haterSearch()
        t = tweets.objects.all()
    return render(response, "custHaterSearch.html", {"tweets": t, "form": form})


def ctwitterUserRetrieval(request, myid):
    t = twitterUser.objects.get(twitterUser=myid)
    return render(request, "custTwitterUserRetrieval.html", {"t": t})


