from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .middlewares import auth, guest
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment
from django.contrib import messages

@guest
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

@guest
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def dashboard_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'posts': posts})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if title and content:
            post = Post.objects.create(
                user=request.user,
                title=title,
                content=content,
                image=image,
                video=video
            )
            messages.success(request, 'Post created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Title and content are required.')

    return render(request, 'create_post.html')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        messages.info(request, 'Post unliked!')
    else:
        messages.success(request, 'Post liked!')
    return redirect('dashboard')

@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('comment')
        if text.strip():
            Comment.objects.create(post=post, user=request.user, text=text)
            messages.success(request, 'Comment added!')
    return redirect('dashboard')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        if request.FILES.get('video'):
            post.video = request.FILES.get('video')
        post.save()
        messages.success(request, 'Post updated successfully!')
        return redirect('dashboard')
    return render(request, 'edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('dashboard')
    return render(request, 'delete_post.html', {'post': post})