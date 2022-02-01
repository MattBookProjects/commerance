from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    #id = models.AutoField(primary_key=True)
    pass

class Category(models.Model):
    #id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=64)

class Listing(models.Model):
    #id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    watchers = models.ManyToManyField(User, blank=True, null=True, related_name="watchlist")
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2)
    latest_bid = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    image_url = models.CharField(max_length=1024, blank=True, null=True)
    active = models.BooleanField(default=True)
    buyer = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "owner: " + self.owner.username + " title: " + self.title + " description: " + self.description

class Comment(models.Model):
    #id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)

class Bid(models.Model):
    #id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    value = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)