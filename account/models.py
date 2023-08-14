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
    status = models.CharField(max_length=20, choices=STATUS, default='Active')


class UpdateCustomer(models.Model):
    username = models.CharField(max_length=100, blank=True)
    password1 = models.CharField(max_length=20, blank=True)
    password2 = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    phone_number = models.IntegerField(null=True)
    address = models.CharField(max_length=100, blank=True)
    postal_code = models.IntegerField(null=True)
    twitter_handle = models.CharField(max_length=20, blank=True)


class UpdateProfile(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    phone_number = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True)
    postal_code = models.IntegerField(blank=True, null=True)
    twitter_handle = models.CharField(max_length=20, blank=True)


class Request(models.Model):
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
    category = models.CharField(max_length=30, choices=categories, default='Not yet analysed')

    def __str__(self):
        return self.tweet


class twitterUser(models.Model):
    twitterUser = models.CharField(max_length=255, unique=True)
    hateCount = models.IntegerField(null=True)
    offensiveCount = models.IntegerField(null=True)
    neutralCount = models.IntegerField(null=True)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return self.twitterUser
