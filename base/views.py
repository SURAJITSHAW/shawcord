from email import message
from django.shortcuts import render, redirect
from django.db.models import Q
from base.models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

# test data
# rooms = [
#     {'id': 1, 'name': 'Learn Django together'},
#     {'id': 2, 'name': 'Backend developers only!'},
#     {'id': 3, 'name': 'OP verse'},
# ]

# Create your views here.

def loginPage(request):
    # variable to determine which page to render
    page = 'login'

    # if user is logged in, redirect to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try: 
            user = User.objects.get(username=username)
        except: 
            messages.error(request, "User doesn't esists.")
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'User or Password does not exist!')

    context = {'page':page}
    return render(request, 'login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    # process the form
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error occurred while registering')

    return render(request, 'login_register.html', {'form': form})

def home(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    return render(request, 'home.html', {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages})

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created_at')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'room.html', context)

# CRUD operations for Room

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

    # Process the data get from the Post request
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}

    return render(request, 'create_room.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)  # the room we want to update
    form = RoomForm(instance=room)

    # Resttricted permissions
    if request.user != room.host:
        return HttpResponse("You are not allowed to update this room!")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'create_room.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)  # the room we want to delete

    # Resttricted permissions
    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this room!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj': room})

# Delete message
@login_required(login_url='login')
def delete_message(request, pk):

    message = Message.objects.get(id=pk)  # the message we want to delete

    # Resttricted permissions
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this message!")

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'delete.html', {'obj': message})

# User profile view
def UserProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'profile.html', context)

# Edit User Profile
@login_required(login_url='login')
def UserEdit(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('userProfile', pk=user.id)

    return render(request, 'edit-user.html', {'form': form})

# mobile view : topics
def topics(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains = q)

    return render(request, 'topics.html', {'topics': topics})

# mobile view : activity
def activity(request):
    room_messages = Message.objects.all()
    return render(request, 'activity.html', {'room_messages': room_messages})
