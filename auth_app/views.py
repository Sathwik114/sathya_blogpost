from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .middlewares import auth, guest
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment  # ✅ You forgot to import these models

# ------------------- REGISTER VIEW -------------------
@guest
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


# ------------------- LOGIN VIEW -------------------
@guest
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


# ------------------- DASHBOARD VIEW -------------------
@auth
def dashboard_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'posts': posts})


# ------------------- LOGOUT VIEW -------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------- CREATE POST -------------------
@auth
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Post.objects.create(author=request.user, title=title, content=content)
        return redirect('dashboard')
    return render(request, 'create_post.html')


# ------------------- LIKE POST -------------------
@auth
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Unlike if already liked
    return redirect('dashboard')


# ------------------- COMMENT ON POST -------------------
@auth
def comment_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('comment')
        if text.strip():  # Prevent empty comments
            Comment.objects.create(post=post, user=request.user, text=text)
    return redirect('dashboard')
