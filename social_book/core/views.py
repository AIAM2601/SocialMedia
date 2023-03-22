from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Profile

# Create your views here.

@login_required(login_url='signin') #handles logout if user logs out it will redirect them to sign in 
def index(request):
    return render(request, "index.html")

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)#currently auth user

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            #if user doesnt change profile img
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            #if user changes profile img
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')    
    return render(request, "setting.html", {"user_profile": user_profile}) #pass to the view so that I can handle it in the html

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

                #log user in and redirect to settings pages
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a profile object for the new user
                user_model = User.objects.get(username=username) #gets the object of the user
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')#to login then
        else: 
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else: 
        return render(request, 'signup.html')
    
def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else: 
            messages.info(request, 'Credentials invalid')
            return redirect('signin')
    else:
        return render(request, "signin.html")
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect("/signin")