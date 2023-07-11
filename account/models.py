from django.db import models, connections
from django.contrib.auth.models import AbstractUser, User


# Create your models here.
class Customer(AbstractUser):
    STATUS = [
        ('Active', 'Active'),
        ('Suspended', 'Suspended'),
    ]
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=100, blank=True)
    postal_code = models.IntegerField(null=True)
    twitter_handle = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='Suspended')


class UpdateCustomer(models.Model):
    username = models.CharField(max_length=100,blank=True)
    password1 = models.CharField(max_length=20, blank=True)
    password2 = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100,blank=True)
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=100, blank=True)
    postal_code = models.IntegerField(null=True)
    twitter_handle = models.CharField(max_length=20, blank=True)


class Request(models.Model):
    STATUS = [
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
    ]
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    password_confirmation = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=100)
    postal_code = models.IntegerField(null=True)
    twitter_handle = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')


class Word(models.Model):
    word = models.CharField(max_length=100)
    description = models.TextField()


class tweets(models.Model):
    NEUTRAL = 'NM'
    OFFENSIVE = 'OL'
    HATEFUL = 'HM'
    categories = [
        (NEUTRAL, 'Neutral'),
        (OFFENSIVE, 'Offensive Language'),
        (HATEFUL, 'Hateful Message')
    ]
    twitterUser = models.CharField(max_length=255)
    tweet = models.CharField(max_length=255)
    tweetURL = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=categories, default='Not yet analysed')

    def __str__(self):
        return self.tweet


class twitterUser(models.Model):
    NEUTRAL = 'Neutral'
    OFFENSIVE = 'Offensive Language'
    HATEFUL = 'Hateful Message'
    categories = [
        (NEUTRAL, 'Neutral'),
        (OFFENSIVE, 'Offensive Language'),
        (HATEFUL, 'Hateful Message')
    ]
    twitterUser = models.CharField(max_length=255)
    bio = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=categories, default='Not yet analysed')

    def __str__(self):
        return self.bio
