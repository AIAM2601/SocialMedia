from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('settings', views.settings, name="settings"),
    path('upload', views.upload, name="upload"),
    path('follow', views.follow, name="follow"),
    path('search', views.search, name="search"),
    path('profile/<str:pk>', views.profile, name="profile"),
    path('likePost', views.likePost, name="likePost"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('logout', views.logout, name="logout")
]
