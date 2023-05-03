from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain
from .models import Profile, Post, LikePost, FollowersCount, Comments
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import random

# Create your views here.

@login_required(login_url='signin') #handles logout if user logs out it will redirect them to sign in / must be logged in
def index(request):
    #feed
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object) 

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    
    feed_list = list(chain(*feed))

    if feed_list: 
        # Get all the comments for the feed list
        for post in feed_list:
            comments = post.comments.all()
            post.comments.set(comments)
    else: 
        comments = ""

    #user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestion_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestion_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
        
    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, "index.html", {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4], 'comments': comments}) #posts is a list that we're passing

@login_required(login_url='signin') 
def upload(request):

    if request.method == 'POST':
        image  = request.FILES.get('image_upload')
        if image: 
            user = request.user.username
            caption = request.POST['caption']

            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()
            return redirect('/')
        else:
            messages.error(request, 'Please add an image')
            return redirect('/')
            
    else: 
        return redirect('/')

@login_required(login_url='signin') 
def comments(request):
    if request.method == 'POST':
        post_id = request.GET.get('post_id')
        user = request.user.username
        text = request.POST['CommentText']
        post = Post.objects.get(id=post_id)
        print('post id' +post_id)
        new_comment = Comments.objects.create(author=user, post=post, text=text)
        new_comment.save()
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    username_profile_list = [] # Define the variable before the if condition and set it to an empty list

    if request.method == 'POST':
        if 'username' in request.POST:
            username = request.POST['username']
            username_object = User.objects.filter(username__icontains=username) #searches for username case insensitive

            username_profile = []

            for users in username_object:
                username_profile.append(users.id) #adds users.id to the list of username profiles

            for ids in username_profile:
                profile_lists = Profile.objects.filter(id_user=ids) #gets the ids for profiles
                username_profile_list.extend(profile_lists) # Update the list with profiles that match the search criteria

            username_profile_list = list(set(username_profile_list)) # Remove duplicates from the list of profiles

    return render(request, "search.html", {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin') 
def likePost(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.num_of_likes = post.num_of_likes + 1
        post.save()
        return redirect('/')
    else: 
        like_filter.delete()
        post.num_of_likes = post.num_of_likes - 1
        post.save()
        return redirect('/')

@login_required(login_url='signin') 
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk) #posts that belong to pk user
    user_post_length = len(user_posts) #number of posts per user

    follower = request.user.username
    user = pk

    #dynamic button text
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    user_followers = len(FollowersCount.objects.filter(user=pk)) #filters by user logged in
    user_following = len(FollowersCount.objects.filter(follower=pk)) 

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    } #better to use a context instead of passing each one 
    return render(request, 'profile.html', context)

@login_required(login_url='signin') 
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']

    #delete because it already exists
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
    #create folower
        else: 
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/') 

@login_required(login_url='signin')
def usersettings(request):
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
        return redirect('usersettings')    
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
                # create user 
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = False
                user.save()

                ## Welcome email
                subject = "Welcome to IReal!"
                message = "Hello " + user.username + " Thank you for signing up!"
                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]
                send_mail(subject, message, from_email, to_list, fail_silently=True)

                # Email address confirmation
                current_site = get_current_site(request)
                email_subject = "Confirm your email"
                message2 = render_to_string('email_confirmation.html', {
                    'name': user.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                })

                email = EmailMessage(
                    email_subject,
                    message2,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                email.fail_silently = True
                email.send()

                #log user in and redirect to settings pages
                # user_login = auth.authenticate(username=username, password=password)
                # auth.login(request, user_login)

                #create a profile object for the new user
                user_model = User.objects.get(username=username) #gets the object of the user
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                return redirect('/checkEmail')
        else: 
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else: 
        return render(request, 'signup.html')
    
def activate (request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('usersettings')
    else:
        return redirect(request, 'activation_failed.html')
        
def checkEmail(request):
    return render(request, "check_email.html")

def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if 'rememberMe' in request.POST:
         rememberMe = request.POST['rememberMe']
        else: 
            rememberMe = False

        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not rememberMe:
                request.session.set_expiry(0)
                return redirect('/')
            else: 
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                return redirect('/')
        else: 
            messages.info(request, 'Credentials invalid')
            return redirect('signin')
    else:
        return render(request, "signin.html")

@login_required(login_url='signin')
def logoutView(request):
    logout(request)
    return redirect("/signin")