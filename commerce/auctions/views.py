from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Category, Comment, Bid
import datetime


class CreateListingForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder" : "Title", "class" : "create-listing-page-form-title"}), max_length=64)
    description = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder" : "Description",  "class" : "create-listing-page-form-description"}), max_length=1024)
    starting_bid = forms.DecimalField(label="", widget=forms.TextInput(attrs={"placeholder": "Starting bid",  "class" : "create-listing-page-form-starting-bid"}), decimal_places=2, max_digits=20, min_value=0)
    image_url = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder" : "Image url (optional)",  "class" : "create-listing-page-form-image-url"}), required=False)
    choices = [(category, category.category) for category in Category.objects.all()]
    choices.append((None, "None"))
    category = forms.ChoiceField(label="Category (optional)", choices=choices, initial=(None, "None"), required=False, widget=forms.Select(attrs={"class" : "create-listing-page-form-category"}))

class CommentForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholer": "Comment here", "class": "listing-page-comment-form-input"}), max_length=1024)

class BidForm(forms.Form):
    bid = forms.DecimalField(label="", widget=forms.TextInput(attrs={"placeholder": "Enter your bid here", "class": "listing-page-bid-input"}))

    def set_min_value(value):
        BidForm.bid.min_value = value






def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
        "no_mathces_message": "No active listings at this moment"
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CreateListingForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                starting_bid = form.cleaned_data["starting_bid"]
                image_url = form.cleaned_data["image_url"]
                category = form.cleaned_data["category"]
                listing = Listing(title=title, description=description, starting_bid=starting_bid, image_url=image_url, owner=request.user, category=None)
                listing.save()
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create_listing.html", {
                "form": CreateListingForm()
            })
    else:
        return HttpResponseRedirect(reverse("index"))

def listing(request, id):
    '''if request.user.is_authenticated:
        if request.user.watchlist.all():
            return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(id=id),
                "in_watchlist": True
            })
        else:
            return render(request, "auctions/listing.html", {
                "listing": Listing.objects.get(id=id)
            })
    else:'''
    listing = Listing.objects.get(id=id)
    if request.method =="POST":
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            user_bid =  bid_form.cleaned_data["bid"]
            if listing.bids.count() > 0:
                current_bid = listing.bids.all().order_by("-value").first().value                
                if user_bid < current_bid and Bid.objects.get(value=current_bid, owner=request.user).owner != request.user:
                    bid = Bid(listing = listing, value=user_bid, owner=request.user)
                    bid.save()
                    return render(request, "auctions/listing.html", {
                        "bid": listing.bids.all().order_by("-value").first().value,
                        "bid_form": bid_form,
                        "comments" : listing.comments.all().order_by("-date"),
                        "comment_form" : CommentForm(),
                        "listing": listing
                    })
                elif Bid.objects.get(value=current_bid, owner=request.user).owner == request.user:
                        
                    return render(request, "auctions/listing.html", {
                        "bid": listing.bids.all().order_by("-value").first().value,
                        "bid_form": bid_form,
                        "comments" : listing.comments.all().order_by("-date"),
                        "comment_form" : CommentForm(),
                        "listing": listing,
                        "bid_error": "Your last bid is the current"

                    })
            else:
                if user_bid > listing.starting_bid:
                    bid = Bid(listing = listing, value=user_bid, owner=request.user)
                    bid.save()
                    return render(request, "auctions/listing.html", {
                        "bid": listing.bids.all().order_by("-value").first().value,
                        "bid_form": bid_form,
                        "comments" : listing.comments.all().order_by("-date"),
                        "comment_form" : CommentForm(),
                        "listing": listing
                    })
        if listing.bids.count() > 0:
            return render(request, "auctions/listing.html", {
                "bid": listing.bids.all().order_by("-value").first().value,
                "bid_form": bid_form,
                "comments" : listing.comments.all().order_by("-date"),
                "comment_form" : CommentForm(),
                "listing": listing,
                "bid_error": "Bid must be a number larger than current bid"
                })
        else:
            return render(request, "auctions/listing.html", {
                "bid_form": bid_form,
                "comments" : listing.comments.all().order_by("-date"),
                "comment_form" : CommentForm(),
                "listing": listing,
                "bid_error": "Bid must be a number larger than current bid"
            })
 

    bid_form = BidForm()
    if listing.bids.count() > 0:
        return render(request, "auctions/listing.html", {
            "listing": listing, 
            "comment_form" : CommentForm(),
            "bid_form" : bid_form,
            "bid" : listing.bids.all().order_by("-value").first().value,
            #"comments" : Comment.objects.filter(listing=Listing.objects.get(id=id)).order_by("date")
            "comments" : listing.comments.all().order_by("-date")

    })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comment_form" : CommentForm(),
            "bid_form" : bid_form,
            "comments" : listing.comments.all().order_by("-date")

        })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
     })
   

def category(request, category):
    return render(request, "auctions/index.html", {
        "listings" : Listing.objects.filter(category=Category.objects.get(category=category), active=True),
        "no_matches_message" : "No active listings for this category"
    })

def watchlist(request):
    if request.user.is_authenticated:
        
        return render(request, "auctions/index.html", {
           "listings" : request.user.watchlist.all(),
           "no_matches_message" : "Your watchlist is empty"
            })
      
    else:
        return HttpResponseRedirect(reverse("login"))

def watchlist_add(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            id = request.POST["id"]   
            request.user.watchlist.add(Listing.objects.get(id=id))
            return HttpResponseRedirect(reverse("listing", kwargs={'id': id}))
        else:
            return HttpResponseRedirect(reverse("watchlist"))
    else:
        return HttpResponseRedirect(reverse("login"))

def watchlist_remove(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            id = request.POST["id"]
            request.user.watchlist.remove(Listing.objects.get(id=id))
            return HttpResponseRedirect(reverse("listing", kwargs={'id': id}))
        else:
            return HttpResponseRedirect(reverse("watchlist"))
    else:
        return HttpResponseRedirect(reverse("login"))

def comment(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                content = form.cleaned_data["content"]
                comment = Comment(author=request.user, content=content, listing=Listing.objects.get(id=id), date=datetime.datetime.utcnow())
                comment.save()
        return HttpResponseRedirect(reverse("listing", kwargs={'id': id}))
    else: 
        return HttpResponseRedirect(reverse("login"))

def close(request, id):
    print("close")
    if request.user.is_authenticated:
        if request.method == "POST":
            listing = Listing.objects.get(id=id)
            print("method post")
            if listing.owner == request.user:
                listing.active = False
                final_bid = listing.bids.all().order_by('-value').first()
                if final_bid is not None:
                    listing.buyer = final_bid.owner
                listing.save()
        return HttpResponseRedirect(reverse("listing", kwargs={'id': id}))
    return HttpResponseRedirect(reverse("login"))

'''
def bid(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = BidForm(request.POST)
            if form.is_valid():
                value = form.cleaned_data["bid"]
                bid = Bid(listing=Listing.objects.get(id=id), value=value, owner=request.user)
                bid.save()
        return HttpResponseRedirect(reverse("listing", kwargs={'id': id}))
    return HttpResponseRedirect(reverse("login"))'''