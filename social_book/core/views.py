from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages

from .models import Profile

# Create your views here.
def index(request):
    return render(request, "index.html")

def signup(request):

    if request.method == 'POST':
        username = request.POST['username'] #it maps the variable by the name
        email = request.POST['email'] 
        password = request.POST['password'] 
        password2 = request.POST['password2'] #django handles password hashing
        print(username)

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else: 
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page

                #create a profile object for the new user
                user_model = User.objects.get(username=username) #gets the object of the user
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('signup')#to login then
        else: 
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else: 
        return render(request, 'signup.html')