from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('usersettings', views.usersettings, name="usersettings"),
    path('upload', views.upload, name="upload"),
    path('follow', views.follow, name="follow"),
    path('search', views.search, name="search"),
    path('profile/<str:pk>', views.profile, name="profile"),
    path('likePost', views.likePost, name="likePost"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('forgotpass', views.forgotpass, name="forgotpass"),
    path('logout', views.logout, name="logout")
]
