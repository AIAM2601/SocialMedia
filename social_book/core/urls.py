from django.urls import path
from . import views

from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('', views.index, name="index"),
    path('usersettings', views.usersettings, name="usersettings"),
    path('upload', views.upload, name="upload"),
    path('follow', views.follow, name="follow"),
    path('search', views.search, name="search"),
    path('comments', views.comments, name="comments"),
    path('likePost', views.likePost, name="likePost"),
    path('signup', views.signup, name="signup"),
    path('activate/<slug:uidb64>/<slug:token>', views.activate, name="activate"),
    path('checkEmail', views.checkEmail, name="checkEmail"),
    path('profile/<str:pk>', views.profile, name="profile"),
    path('signin', views.signin, name="signin"),
    path('password-reset/', PasswordResetView.as_view(template_name='password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
    path('logout', views.logout, name="logout")
]
