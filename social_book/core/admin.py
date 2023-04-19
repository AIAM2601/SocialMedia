from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Comments

# Register your models here.
#to manage profile on the django admin 
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Comments)