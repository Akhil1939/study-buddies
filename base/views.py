from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def loginPage(request):
    page= 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Invalid username or password") 
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
             messages.error(request, "username or password not exists")
    context={'page': page}
    return render(request, 'base/login_register.html', context )

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page='register'
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "error while registration")
    context={'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count=rooms.count()
    topics = Topic.objects.all() 
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages,}
    return render(request,'base/home.html', context )

def room(request, pk):
    room = Room.objects.get(id=pk)
    roomMessages= room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method=="POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("comment")
        )
        room.participants.add(request.user)
        return redirect('room', pk= room.id)
    context = {'room':room, 'roomMessages':roomMessages, 'participants':participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='/login' )
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST': 
       topic_name = request.POST.get('topic')
       topic, created = Topic.objects.get_or_create(name=topic_name)

       Room.objects.create(
           host=request.user,
           topic = topic,
           name = request.POST.get('name'),
           description = request.POST.get('description'),
       )
       return redirect('home')
    
    topics = Topic.objects.all() 
    context={'form': form, 'topics': topics}
    return render(request, 'base/create-room.html',context)

@login_required(login_url='/login' )
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host  :
        return HttpResponse('you are not allowed here !!')
    if request.method == 'POST':
       topic_name = request.POST.get('topic')
       topic, created = Topic.objects.get_or_create(name=topic_name)
       room.name  = request.POST.get('name')
       room.topic  = topic
       room.description  = request.POST.get('description')
       room.save()
       return redirect('home')
    
    topics = Topic.objects.all() 
    context={'form': form, 'topics': topics, 'room':room}
    return render(request, 'base/create-room.html',context)

@login_required(login_url='/login' )
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if(request.method == 'POST'):
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='/login' )
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("you are not allowed here !!")
    
    if(request.method == 'POST'):
        message.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='/login')
def profilePage(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context={'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login')
def updateUser(request):
    user=request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})


