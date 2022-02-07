from django.contrib import admin

from .models import Category, Listing, User, Bid, Comment
# Register your models here.

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(User)

