from django.contrib import admin
from .models import Profile, Post, LikePost

# Register your models here.
#to manage profile on the django admin 
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)